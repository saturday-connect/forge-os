'use strict'

const { app, BrowserWindow, Tray, Menu, shell, dialog, nativeImage, ipcMain, clipboard } = require('electron')
const { autoUpdater } = require('electron-updater')
const { spawn, execSync, execFileSync } = require('child_process')
const path = require('path')
const net = require('net')
const fs = require('fs')
const http = require('http')

const auth = require('./auth')
const github = require('./github')
const org = require('./org')
const os = require('os')

function writeTempHtml(name, html) {
  const p = path.join(os.tmpdir(), `forge-os-${name}.html`)
  fs.writeFileSync(p, html, 'utf8')
  return p
}

// ─── App identity (must be set before 'ready') ───────────────────────────────

app.setName('Forge OS')

// ─── Constants ───────────────────────────────────────────────────────────────

const FORGE_VERSION = app.getVersion()
const USER_DATA = app.getPath('userData')
const CONFIG_FILE = path.join(USER_DATA, 'config.json')
const READY_POLL_INTERVAL_MS = 300
const READY_TIMEOUT_MS = 20000

// Shared secret for local HTTP API — generated fresh each run
const crypto = require('crypto')
const FORGE_TOKEN = crypto.randomBytes(32).toString('hex')

// App icon for native dialogs (overrides default Electron icon)
const APP_ICON_PATH = path.join(__dirname, 'assets', 'icon-256.png')
const appDialogIcon = fs.existsSync(APP_ICON_PATH) ? nativeImage.createFromPath(APP_ICON_PATH) : undefined

// ─── State ────────────────────────────────────────────────────────────────────

let win = null
let tray = null
let serverProcess = null
let serverPort = null
let isQuitting = false
let currentUser = null    // { login, name, avatar_url }
let currentOrg = null     // GitHub org login string

// ─── Config ───────────────────────────────────────────────────────────────────

function readConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'))
  } catch (_) {}
  return {}
}

function writeConfig(data) {
  fs.mkdirSync(USER_DATA, { recursive: true })
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(data, null, 2), { mode: 0o600 })
}

function addProjectToHistory(projectPath) {
  const config = readConfig()
  const history = (config.projectHistory || []).filter(p => p !== projectPath)
  history.unshift(projectPath)
  writeConfig({ ...config, projectHistory: history.slice(0, 10) })
}

function addOrgToHistory(orgName, repoName) {
  const config = readConfig()
  const history = (config.orgHistory || []).filter(o => o.org !== orgName)
  history.unshift({ org: orgName, repo: repoName || 'forge-knowledge' })
  writeConfig({ ...config, orgHistory: history.slice(0, 5) })
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function getFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer()
    srv.listen(0, '127.0.0.1', () => {
      const { port } = srv.address()
      srv.close(() => resolve(port))
    })
    srv.on('error', reject)
  })
}

function forgeBinaryPath() {
  return app.isPackaged
    ? path.join(process.resourcesPath, 'forge')
    : path.join(__dirname, '..', 'forge')
}

// ─── Setup wizard ────────────────────────────────────────────────────────────

function needsSetup() {
  try {
    const config = readConfig()
    return !config.githubClientId && !config.org
  } catch (_) {
    return true
  }
}

function createSetupWindow() {
  return new Promise((resolve, reject) => {
    const setupWin = new BrowserWindow({
      width: 640,
      height: 560,
      minWidth: 560,
      minHeight: 480,
      resizable: true,
      title: 'Forge OS Setup',
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        preload: path.join(__dirname, 'setup-preload.js'),
        contextIsolation: true,
        nodeIntegration: false
      }
    })
    setupWin.setMenuBarVisibility(false)
    setupWin.loadFile(path.join(__dirname, 'setup-window.html'))

    // IPC: open URL in browser
    ipcMain.on('setup-open-url', (_e, url) => shell.openExternal(url))

    // IPC: verify org (admin step 3)
    ipcMain.handle('setup-verify-org', async (_e, orgName, repoName) => {
      const repo = repoName || 'forge-knowledge'
      try {
        const exists = await github.repoExists(null, orgName, repo).catch(() => false)
        return { repoExists: exists }
      } catch (err) {
        return { error: `Could not verify organization: ${err.message}` }
      }
    })

    // IPC: fetch org config for member flow — pulls forge.config.json from the
    // org's forge-knowledge repo using the unauthenticated GitHub Contents API
    // (works for public repos; private repos require auth, handled post-setup).
    ipcMain.handle('setup-fetch-org-config', async (_e, orgName) => {
      const url = `https://api.github.com/repos/${orgName}/forge-knowledge/contents/forge.config.json`
      return new Promise(res => {
        const https = require('https')
        const req = https.get(url, {
          headers: { 'User-Agent': 'forge-os-desktop', Accept: 'application/vnd.github+json' }
        }, response => {
          let raw = ''
          response.on('data', c => { raw += c })
          response.on('end', () => {
            if (response.statusCode === 404) {
              return res({ error: `No forge-knowledge repo found in "${orgName}". Ask your admin to set up Forge OS first.` })
            }
            if (response.statusCode === 403 || response.statusCode === 401) {
              // Private repo — we can't fetch without auth yet; store org name and proceed.
              // The Client ID will be pulled after the user authenticates.
              return res({ orgName, private: true })
            }
            if (response.statusCode !== 200) {
              return res({ error: `GitHub returned status ${response.statusCode}. Check the organization name and try again.` })
            }
            try {
              const data = JSON.parse(raw)
              const content = JSON.parse(Buffer.from(data.content.replace(/\n/g, ''), 'base64').toString('utf8'))
              if (!content.githubClientId) {
                return res({ error: 'forge.config.json exists but has no githubClientId. Ask your admin to complete setup.' })
              }
              return res({ orgName, githubClientId: content.githubClientId })
            } catch (_) {
              return res({ error: 'Could not parse forge.config.json from the organization repo.' })
            }
          })
        })
        req.on('error', err => res({ error: `Network error: ${err.message}` }))
        req.setTimeout(10000, () => { req.destroy(); res({ error: 'Request timed out.' }) })
      })
    })

    // IPC: copy text to clipboard (used by SSH key copy button)
    ipcMain.on('setup-copy-clipboard', (_e, text) => clipboard.writeText(text))

    // IPC: check git installation, global identity, and SSH key
    ipcMain.handle('setup-git-status', async () => {
      const result = { gitInstalled: false, gitName: '', gitEmail: '', sshKeyExists: false, sshPublicKey: '' }
      try { execSync('git --version', { stdio: 'ignore' }); result.gitInstalled = true } catch (_) { return result }
      try { result.gitName = execSync('git config --global user.name', { encoding: 'utf8' }).trim() } catch (_) {}
      try { result.gitEmail = execSync('git config --global user.email', { encoding: 'utf8' }).trim() } catch (_) {}
      const pubPath = path.join(os.homedir(), '.ssh', 'id_ed25519_forge_os.pub')
      if (fs.existsSync(pubPath)) {
        result.sshKeyExists = true
        result.sshPublicKey = fs.readFileSync(pubPath, 'utf8').trim()
      }
      return result
    })

    // IPC: save git global name/email
    ipcMain.handle('setup-git-config', async (_e, name, email) => {
      try {
        if (name) execFileSync('git', ['config', '--global', 'user.name', name])
        if (email) execFileSync('git', ['config', '--global', 'user.email', email])
        return { ok: true }
      } catch (err) { return { error: err.message } }
    })

    // IPC: generate ed25519 SSH key
    ipcMain.handle('setup-ssh-generate', async () => {
      const sshDir = path.join(os.homedir(), '.ssh')
      const keyPath = path.join(sshDir, 'id_ed25519_forge_os')
      const pubPath = keyPath + '.pub'
      if (fs.existsSync(pubPath)) return { publicKey: fs.readFileSync(pubPath, 'utf8').trim() }
      try {
        fs.mkdirSync(sshDir, { recursive: true })
        try { fs.chmodSync(sshDir, 0o700) } catch (_) {}
        execFileSync('ssh-keygen', ['-t', 'ed25519', '-C', 'forge-os', '-f', keyPath, '-N', ''])
        return { publicKey: fs.readFileSync(pubPath, 'utf8').trim() }
      } catch (err) { return { error: err.message } }
    })

    // IPC: test SSH connection to GitHub (exit code 1 = success for ssh -T)
    ipcMain.handle('setup-ssh-test', () => {
      return new Promise(resolve => {
        let finished = false
        const done = (connected, message) => {
          if (finished) return
          finished = true
          resolve({ connected, message })
        }
        const sshDir = path.join(os.homedir(), '.ssh')
        const keyPath = path.join(sshDir, 'id_ed25519_forge_os')

        // Ensure correct permissions
        try { fs.chmodSync(sshDir, 0o700) } catch (_) {}
        if (fs.existsSync(keyPath)) { try { fs.chmodSync(keyPath, 0o600) } catch (_) {} }

        if (!fs.existsSync(keyPath)) {
          return done(false, 'Private key not found at ~/.ssh/id_ed25519_forge_os. Generate the key first.')
        }

        // Detect if the key has a passphrase (ssh-keygen -y with empty passphrase fails if protected)
        let hasPassphrase = false
        try { execFileSync('ssh-keygen', ['-y', '-f', keyPath, '-P', ''], { stdio: 'pipe' }) }
        catch (_) { hasPassphrase = true }

        // Write the standard macOS SSH config for github.com if not already present
        // This enables UseKeychain so once added with ssh-add --apple-use-keychain it persists
        const sshConfigPath = path.join(sshDir, 'config')
        const sshConfig = fs.existsSync(sshConfigPath) ? fs.readFileSync(sshConfigPath, 'utf8') : ''
        if (!sshConfig.includes('Host github.com')) {
          const entry = '\nHost github.com\n  AddKeysToAgent yes\n  UseKeychain yes\n  IdentityFile ~/.ssh/id_ed25519_forge_os\n'
          fs.appendFileSync(sshConfigPath, entry)
          try { fs.chmodSync(sshConfigPath, 0o644) } catch (_) {}
        }

        // If key has a passphrase and agent has nothing, we can't auth without passphrase
        if (hasPassphrase) {
          const agentKeys = (() => { try { return execSync('ssh-add -l', { encoding: 'utf8' }) } catch (_) { return '' } })()
          if (!agentKeys.includes('id_ed25519_forge_os') && !agentKeys.includes(path.basename(keyPath, ''))) {
            return done(false, 'PASSPHRASE_NEEDED')
          }
        }

        const proc = spawn('ssh', [
          '-T', 'git@github.com',
          '-o', 'StrictHostKeyChecking=accept-new',
          '-o', 'ConnectTimeout=10'
        ], { stdio: ['ignore', 'pipe', 'pipe'] })
        let out = ''
        proc.stdout.on('data', d => { out += d })
        proc.stderr.on('data', d => { out += d })
        proc.on('close', () => {
          const connected = out.includes('successfully authenticated')
          let message = out.trim()
          if (!connected) {
            if (out.includes('Permission denied') || out.includes('publickey')) {
              message = 'GitHub does not recognise this key. Make sure you copied the full public key and saved it at github.com/settings/ssh/new.'
            } else if (out.includes('Could not resolve') || out.includes('Network')) {
              message = 'Network error — check your internet connection.'
            } else if (!message) {
              message = 'Authentication failed.'
            }
          }
          done(connected, message)
        })
        proc.on('error', err => done(false, `Could not run SSH: ${err.message}`))
        setTimeout(() => { try { proc.kill() } catch (_) {} done(false, 'Connection timed out.') }, 15000)
      })
    })

    // IPC: unlock passphrase-protected SSH key and add to macOS Keychain / agent
    ipcMain.handle('setup-ssh-unlock', async (_e, passphrase) => {
      const keyPath = path.join(os.homedir(), '.ssh', 'id_ed25519_forge_os')
      if (!fs.existsSync(keyPath)) return { error: 'Key file not found. Generate the key first.' }

      // Askpass script reads passphrase from env — no passphrase embedded in the file
      const tmpScript = path.join(os.tmpdir(), `forge-askpass-${Date.now()}.sh`)
      try {
        fs.writeFileSync(tmpScript, '#!/bin/sh\nprintf \'%s\' "$FORGE_SSH_PASS"\n', { mode: 0o700 })
        const env = { ...process.env, SSH_ASKPASS: tmpScript, SSH_ASKPASS_REQUIRE: 'force', DISPLAY: 'localhost:0', FORGE_SSH_PASS: passphrase }

        // Try --apple-use-keychain (Ventura+), fall back to plain ssh-add
        try {
          execFileSync('ssh-add', ['--apple-use-keychain', keyPath], { env, stdio: 'pipe' })
        } catch (_) {
          execFileSync('ssh-add', [keyPath], { env, stdio: 'pipe' })
        }
        return { ok: true }
      } catch (err) {
        const msg = (err.stderr?.toString() || err.stdout?.toString() || err.message || '').toLowerCase()
        return { error: msg.includes('bad passphrase') || msg.includes('incorrect') || msg.includes('wrong')
          ? 'Incorrect passphrase — please try again.'
          : `Could not unlock key: ${err.message}` }
      } finally {
        try { fs.unlinkSync(tmpScript) } catch (_) {}
      }
    })

    // IPC: save setup config and close window
    ipcMain.once('setup-save', (_e, setupConfig) => {
      const existing = readConfig()
      writeConfig({ ...existing, ...setupConfig })
      if (setupConfig.knowledgeRepo) org.setRepoName(setupConfig.knowledgeRepo)
      ipcMain.removeAllListeners('setup-open-url')
      ipcMain.removeAllListeners('setup-copy-clipboard')
      ipcMain.removeHandler('setup-verify-org')
      ipcMain.removeHandler('setup-fetch-org-config')
      ipcMain.removeHandler('setup-git-status')
      ipcMain.removeHandler('setup-git-config')
      ipcMain.removeHandler('setup-ssh-generate')
      ipcMain.removeHandler('setup-ssh-unlock')
      ipcMain.removeHandler('setup-ssh-test')
      setupWin.close()
      resolve(setupConfig)
    })

    setupWin.on('closed', () => {
      // User closed window without completing setup
      const config = readConfig()
      if (!config.githubClientId && !config.org) {
        reject(new Error('Setup cancelled.'))
      }
    })
  })
}

// ─── Python check ─────────────────────────────────────────────────────────────

function findPython3() {
  const candidates = [
    'python3',
    '/usr/local/bin/python3',
    '/opt/homebrew/bin/python3',
    `${require('os').homedir()}/.pyenv/shims/python3`,
    '/usr/bin/python3',
  ]
  for (const candidate of candidates) {
    try {
      execSync(`"${candidate}" --version`, { stdio: 'ignore', shell: true })
      return candidate
    } catch (_) {}
  }
  return null
}

const PYTHON3 = findPython3()

// ─── Authentication ───────────────────────────────────────────────────────────

ipcMain.on('auth-copy-code', () => {
  // The current user_code is held by the auth flow via closure — auth.js sends
  // the copy event through to the clipboard via the main process.
  // The code value is surfaced from the auth-window IPC channel; we read it
  // from the BrowserWindow's URL params set during window creation.
  const allWindows = BrowserWindow.getAllWindows()
  const authWin = allWindows.find(w => w.getTitle() === 'Connect GitHub Account')
  if (!authWin) return
  // Code is stored in auth window's userData
  const code = authWin.getUserData?.()
  if (code) clipboard.writeText(code)
})

/**
 * Run the full authentication + org discovery sequence.
 * Returns { token, user, orgLogin }.
 * On GITHUB_UNAUTHORIZED mid-session, call this again to re-auth.
 */
async function authenticate() {
  const config = readConfig()

  // Apply saved knowledge repo name if configured
  if (config.knowledgeRepo) org.setRepoName(config.knowledgeRepo)

  // Seed org history from saved config so it shows up immediately
  if (config.org && !(config.orgHistory || []).find(o => o.org === config.org)) {
    addOrgToHistory(config.org, config.knowledgeRepo || 'forge-knowledge')
  }

  // Attempt to use stored token first
  let token = auth.loadToken()

  if (token) {
    try {
      currentUser = await github.getAuthenticatedUser(token)
    } catch (err) {
      if (err.code === 'GITHUB_UNAUTHORIZED') {
        auth.clearToken()
        token = null
      } else {
        // Network error — allow offline startup with stale config
        console.warn(`[auth] Token validation failed (offline?): ${err.message}`)
        currentUser = config.user || null
        currentOrg = config.org || null
        return { token, user: currentUser, orgLogin: currentOrg }
      }
    }
  }

  if (!token) {
    token = await auth.ensureAuthenticated()
    currentUser = await github.getAuthenticatedUser(token)
    auth.storeToken(token)
  }

  // Org discovery: use stored org if still valid, otherwise re-discover
  let orgLogin = config.org
  if (!orgLogin) {
    orgLogin = await resolveOrg(token)
  } else {
    // Confirm the stored org still has a forge-knowledge repo (quick check)
    const still_exists = await github.repoExists(token, orgLogin, 'forge-knowledge').catch(() => false)
    if (!still_exists) orgLogin = await resolveOrg(token)
  }

  currentOrg = orgLogin
  writeConfig({ ...config, user: { login: currentUser.login, name: currentUser.name }, org: orgLogin })

  return { token, user: currentUser, orgLogin }
}

/**
 * Discover which org to use. If the user belongs to exactly one org with a
 * forge-knowledge repo, it is selected automatically. If multiple exist,
 * the user is prompted to choose.
 */
async function resolveOrg(token) {
  let available
  try {
    available = await org.discoverOrgs(token)
  } catch (err) {
    console.warn(`[org] Discovery failed: ${err.message}`)
    return null
  }

  if (!available.length) return null
  if (available.length === 1) return available[0]

  // Multiple orgs — ask user to pick
  const { response } = await dialog.showMessageBox({ icon: appDialogIcon,
    type: 'question',
    title: 'Select Organization',
    message: 'Multiple organizations have a forge-knowledge repository.',
    detail: 'Choose which organization to connect with:',
    buttons: available,
    cancelId: -1
  })

  return response >= 0 ? available[response] : available[0]
}

// ─── Project management ───────────────────────────────────────────────────────

/**
 * Read the .forge dotfile from a project root.
 * Returns { dataDir, meta } if dotfile exists and is valid.
 * Returns { isLegacy: true, dataDir } if .forge/ directory (legacy) exists.
 * Returns null if neither exists.
 */
function readForgeDotfile(projectRoot) {
  const dotfilePath = path.join(projectRoot, '.forge')
  try {
    const stat = fs.statSync(dotfilePath)
    if (stat.isFile()) {
      const meta = JSON.parse(fs.readFileSync(dotfilePath, 'utf8'))
      const dataDir = meta.data_dir.replace(/^~/, require('os').homedir())
      return { isLegacy: false, dataDir, meta }
    }
    if (stat.isDirectory()) {
      return { isLegacy: true, dataDir: dotfilePath }
    }
  } catch (_) {}
  return null
}

function runForgeCommand(projectRoot, command) {
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', [forgeBinaryPath(), '--project', projectRoot, command], {
      stdio: 'inherit'
    })
    proc.on('close', code => code === 0 ? resolve() : reject(new Error(`forge ${command} failed (exit ${code})`)))
    proc.on('error', reject)
  })
}

/**
 * Ensure the project at projectRoot has a valid .forge dotfile pointing to
 * a populated data directory. Handles:
 *   - fresh project (no .forge): prompt init
 *   - legacy project (.forge/ dir): prompt migration
 *   - valid project (.forge file): nothing to do
 * Returns forgeDataDir string on success, null if user cancelled.
 */
async function ensureProjectReady(projectRoot) {
  let dotfile = readForgeDotfile(projectRoot)

  if (!dotfile) {
    const { response } = await dialog.showMessageBox({ icon: appDialogIcon,
      type: 'question',
      title: 'Initialize Forge Project',
      message: `No Forge project found in:\n${projectRoot}`,
      detail: 'Would you like to initialize a new Forge project here?',
      buttons: ['Initialize', 'Cancel'],
      defaultId: 0
    })
    if (response !== 0) return null
    await runForgeCommand(projectRoot, 'init')
    dotfile = readForgeDotfile(projectRoot)
    if (!dotfile) return null
  }

  if (dotfile.isLegacy) {
    const { response } = await dialog.showMessageBox({ icon: appDialogIcon,
      type: 'question',
      title: 'Migrate Forge Project',
      message: 'This project uses the old layout.',
      detail: 'Project documentation will be moved to ~/.forge/projects/ and a .forge pointer file will be created in the project root. This is a one-time migration.',
      buttons: ['Migrate', 'Cancel'],
      defaultId: 0
    })
    if (response !== 0) return null
    await runForgeCommand(projectRoot, 'migrate')
    dotfile = readForgeDotfile(projectRoot)
    if (!dotfile || dotfile.isLegacy) return null
  }

  return dotfile.dataDir
}

// ─── Server management ────────────────────────────────────────────────────────

function startServer(projectRoot, forgeDataDir, port) {
  const serverScript = path.join(forgeDataDir, 'scripts', 'server.py')
  const gitPat = auth.loadGitPat() || ''
  // projectsRoot is always ~/.forge/projects regardless of projectRoot
  const forgeBase = path.join(path.dirname(forgeDataDir), '..')  // forgeDataDir/../.. = ~/.forge
  const projectsRoot = path.join(os.homedir(), '.forge', 'projects')

  serverProcess = spawn(PYTHON3 || 'python3', [serverScript, String(port)], {
    env: {
      ...process.env,
      FORGE_REPO_ROOT: projectRoot,
      FORGE_DATA_DIR: forgeDataDir,
      FORGE_ORCHESTRATOR_ROOT: path.join(os.homedir(), '.forge'),
      FORGE_PROJECTS_ROOT: projectsRoot,
      FORGE_VERSION,
      FORGE_SCRIPT: forgeBinaryPath(),
      FORGE_ORG: currentOrg || '',
      FORGE_USER: currentUser?.login || '',
      FORGE_TOKEN,
      FORGE_GIT_PAT: gitPat,
    },
    stdio: ['ignore', 'pipe', 'pipe']
  })

  serverProcess.stdout.on('data', d => console.log('[server]', d.toString().trim()))
  serverProcess.stderr.on('data', d => console.error('[server]', d.toString().trim()))

  serverProcess.on('exit', (code, signal) => {
    if (!isQuitting) {
      console.error(`[server] Exited unexpectedly (code=${code}, signal=${signal})`)
      dialog.showMessageBox({ icon: appDialogIcon,
        type: 'error',
        title: 'Forge OS — Server Crashed',
        message: 'The background server stopped unexpectedly.',
        detail: `Exit code: ${code ?? 'unknown'}  Signal: ${signal ?? 'none'}\n\nRestart Forge OS to resume.`,
        buttons: ['Restart', 'Quit'],
        defaultId: 0
      }).then(({ response }) => {
        if (response === 0) {
          app.relaunch()
          app.exit(0)
        } else {
          app.quit()
        }
      })
    }
  })
}

function killServer() {
  if (serverProcess) {
    try { serverProcess.kill('SIGTERM') } catch (_) {}
    serverProcess = null
  }
}

function waitForServer(port) {
  return new Promise((resolve, reject) => {
    const start = Date.now()
    const check = () => {
      const req = http.get(`http://127.0.0.1:${port}/api/state`, res => {
        res.resume()
        if (res.statusCode === 200) return resolve()
        setTimeout(check, READY_POLL_INTERVAL_MS)
      })
      req.on('error', () => {
        if (Date.now() - start > READY_TIMEOUT_MS) {
          reject(new Error('Server did not respond within 20 seconds.'))
        } else {
          setTimeout(check, READY_POLL_INTERVAL_MS)
        }
      })
      req.setTimeout(500, () => { req.destroy(); setTimeout(check, READY_POLL_INTERVAL_MS) })
    }
    check()
  })
}

// ─── Window ───────────────────────────────────────────────────────────────────

function createWindow(port) {
  const appIconPath = path.join(__dirname, 'assets', 'icon-256.png')
  win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'Forge OS',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    icon: fs.existsSync(appIconPath) ? appIconPath : undefined,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  win.on('close', e => {
    if (!isQuitting) {
      e.preventDefault()
      win.hide()
    }
  })

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

// ─── Project opener ───────────────────────────────────────────────────────────

async function openProject(newPath) {
  const newDataDir = await ensureProjectReady(newPath)
  if (!newDataDir) return

  addProjectToHistory(newPath)
  writeConfig({ ...readConfig(), projectPath: newPath })
  killServer()

  try { await runForgeCommand(newPath, 'upgrade') } catch (_) {}

  serverPort = await getFreePort()
  startServer(newPath, newDataDir, serverPort)

  try {
    await waitForServer(serverPort)
  } catch (err) {
    dialog.showErrorBox('Server Error', `Failed to start server:\n${err.message}`)
    return
  }

  if (win) {
    win.loadURL(`http://127.0.0.1:${serverPort}`)
    win.show()
    win.focus()
  }
  buildTrayMenu()
}

const PICKER_STYLES = `
  *{box-sizing:border-box;margin:0;padding:0;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
  body{background:#0a0a0a;color:#fff;display:flex;flex-direction:column;height:100vh;overflow:hidden}
  .header{padding:16px 16px 12px;font-size:11px;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid #1a1a1a;flex-shrink:0}
  .list{flex:1;overflow-y:auto}
  .item{padding:13px 16px;cursor:pointer;border-bottom:1px solid #141414;transition:background .1s;position:relative}
  .item:hover{background:#141414}
  .item.active{background:#0c0c22}
  .item-name{font-size:14px;font-weight:600;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:52px}
  .item-sub{font-size:11px;color:#444;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .item.active .item-sub{color:#494fdf66}
  .badge{position:absolute;right:16px;top:50%;transform:translateY(-50%);font-size:10px;color:#494fdf;font-weight:700;background:#0d0d2a;padding:2px 7px;border-radius:10px;border:1px solid #494fdf44}
  .empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:32px 24px;text-align:center}
  .empty-icon{font-size:28px;opacity:.3}
  .empty-title{font-size:14px;font-weight:600;color:#555}
  .empty-desc{font-size:12px;color:#333;line-height:1.5}
  .footer{padding:12px 16px;border-top:1px solid #1a1a1a;flex-shrink:0;display:flex;flex-direction:column;gap:8px}
  .btn{width:100%;padding:10px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .15s}
  .btn-primary{background:#494fdf;color:#fff}
  .btn-primary:hover{background:#5a60e8}
  .btn-ghost{background:transparent;border:1px solid #222;color:#666}
  .btn-ghost:hover{border-color:#333;color:#aaa}
  input{width:100%;background:#141414;border:1px solid #222;color:#fff;padding:9px 12px;border-radius:8px;font-size:13px;outline:none}
  input:focus{border-color:#494fdf}
  input::placeholder{color:#333}
  .field-label{font-size:11px;color:#555;margin-bottom:5px;display:block}
`

async function showProjectPicker() {
  const config = readConfig()
  const history = (config.projectHistory || []).filter(p => fs.existsSync(p))
  const current = config.projectPath || ''
  const isEmpty = history.length === 0

  const pickerWin = new BrowserWindow({
    width: 460,
    height: isEmpty ? 280 : Math.min(80 + history.length * 62 + 76, 500),
    resizable: false, minimizable: false, maximizable: false,
    title: 'Switch Project',
    parent: win || undefined, modal: !!win,
    webPreferences: { nodeIntegration: true, contextIsolation: false }
  })

  const items = history.map((p, i) => `
    <div class="item ${p === current ? 'active' : ''}" onclick="pick(${i})">
      <div class="item-name">${require('path').basename(p)}</div>
      <div class="item-sub">${p}</div>
      ${p === current ? '<span class="badge">active</span>' : ''}
    </div>`).join('')

  const emptyState = `
    <div class="empty">
      <div class="empty-icon">📁</div>
      <div class="empty-title">No recent projects</div>
      <div class="empty-desc">Open a folder to initialize it as a Forge project. Your projects will appear here for quick switching.</div>
    </div>`

  const projectHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${PICKER_STYLES}</style></head><body>
    <div class="header">Recent Projects</div>
    ${isEmpty ? emptyState : `<div class="list">${items}</div>`}
    <div class="footer">
      <button class="btn btn-${isEmpty ? 'primary' : 'ghost'}" onclick="browseNew()">Open Folder…</button>
    </div>
    <script>
      const {ipcRenderer}=require('electron')
      const paths=${JSON.stringify(history)}
      function pick(i){ipcRenderer.send('project-pick',paths[i])}
      function browseNew(){ipcRenderer.send('project-browse')}
    </script>
  </body></html>`
  pickerWin.loadFile(writeTempHtml('project-picker', projectHtml))

  pickerWin.once('ready-to-show', () => pickerWin.show())

  return new Promise(resolve => {
    const { ipcMain: ipc } = require('electron')
    ipc.once('project-pick', (_e, p) => { pickerWin.close(); resolve(p) })
    ipc.once('project-browse', async () => {
      pickerWin.close()
      const result = await dialog.showOpenDialog(win || null, {
        title: 'Open Forge Project',
        defaultPath: current || app.getPath('home'),
        properties: ['openDirectory', 'createDirectory'],
        buttonLabel: 'Open Project'
      })
      resolve(result.canceled || !result.filePaths.length ? null : result.filePaths[0])
    })
    pickerWin.on('closed', () => {
      ipc.removeAllListeners('project-pick')
      ipc.removeAllListeners('project-browse')
      resolve(null)
    })
  }).then(async chosenPath => {
    if (chosenPath) await openProject(chosenPath)
  })
}

// ─── Tray ─────────────────────────────────────────────────────────────────────

function createTray() {
  const icon16 = path.join(__dirname, 'assets', 'icon-16.png')
  const iconFallback = path.join(__dirname, 'assets', 'icon.png')
  const iconSrc = fs.existsSync(icon16) ? icon16 : iconFallback
  const icon = fs.existsSync(iconSrc)
    ? nativeImage.createFromPath(iconSrc)
    : nativeImage.createEmpty()

  tray = new Tray(icon)
  tray.setToolTip('Forge OS')
  buildTrayMenu()

  tray.on('click', () => {
    if (win) { win.show(); win.focus() }
  })
}

function buildTrayMenu() {
  if (!tray) return

  const config = readConfig()
  const projectName = config.projectPath ? path.basename(config.projectPath) : null
  const orgLabel = currentOrg
    ? `Connected: ${currentOrg}/forge-knowledge`
    : 'No org connected'
  const userLabel = currentUser?.login ? `Signed in as ${currentUser.login}` : null

  const menuTemplate = [
    { label: 'Show Forge OS', click: () => { if (win) { win.show(); win.focus() } } },
    { type: 'separator' },
    ...(userLabel ? [{ label: userLabel, enabled: false }] : []),
    { label: orgLabel, enabled: false },
    ...(projectName ? [{ label: `Project: ${projectName}`, enabled: false }] : []),
    { type: 'separator' },
    {
      label: 'Switch Project',
      click: async () => { await showProjectPicker() }
    },
    {
      label: 'Switch Organization',
      enabled: !!currentUser,
      click: async () => {
        const token = auth.loadToken()
        if (!token) return

        const config = readConfig()
        const orgHistory = config.orgHistory || []
        const currentRepo = config.knowledgeRepo || 'forge-knowledge'
        const isEmpty = orgHistory.length === 0

        const orgWin = new BrowserWindow({
          width: 460,
          height: isEmpty ? 340 : Math.min(80 + orgHistory.length * 62 + 180, 520),
          resizable: false, minimizable: false, maximizable: false,
          title: 'Switch Organization',
          parent: win || undefined, modal: !!win,
          webPreferences: { nodeIntegration: true, contextIsolation: false }
        })

        const items = orgHistory.map((o, i) => `
          <div class="item ${o.org === currentOrg ? 'active' : ''}" onclick="pick(${i})">
            <div class="item-name">${o.org}</div>
            <div class="item-sub">${o.org}/${o.repo}</div>
            ${o.org === currentOrg ? '<span class="badge">active</span>' : ''}
          </div>`).join('')

        const emptyState = `
          <div class="empty">
            <div class="empty-icon">🏢</div>
            <div class="empty-title">No recent organizations</div>
            <div class="empty-desc">Enter your GitHub organization name below. It will appear here for quick switching next time.</div>
          </div>`

        const orgHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${PICKER_STYLES}</style></head><body>
          <div class="header">Organizations</div>
          ${isEmpty ? emptyState : `<div class="list">${items}</div>`}
          <div class="footer">
            <div style="display:flex;flex-direction:column;gap:6px">
              <div><label class="field-label">Organization name</label><input id="org" value="${currentOrg || ''}" placeholder="acme-corp" autofocus /></div>
              <div><label class="field-label">Knowledge repository</label><input id="repo" value="${currentRepo}" placeholder="forge-knowledge" /></div>
            </div>
            <button class="btn btn-primary" style="margin-top:4px" onclick="save()">Switch Organization</button>
          </div>
          <script>
            const {ipcRenderer}=require('electron')
            const orgs=${JSON.stringify(orgHistory)}
            function pick(i){
              document.getElementById('org').value=orgs[i].org
              document.getElementById('repo').value=orgs[i].repo
            }
            function save(){
              const o=document.getElementById('org').value.trim()
              const r=document.getElementById('repo').value.trim()
              if(!o)return
              ipcRenderer.send('org-switch-save',o,r)
            }
            document.addEventListener('keydown',e=>{if(e.key==='Enter')save()})
          </script>
        </body></html>`
        orgWin.loadFile(writeTempHtml('org-picker', orgHtml))

        orgWin.once('ready-to-show', () => orgWin.show())

        const result = await new Promise(resolve => {
          const { ipcMain: ipc } = require('electron')
          ipc.once('org-switch-save', (_e, orgVal, repoVal) => {
            orgWin.close()
            resolve({ orgVal, repoVal })
          })
          orgWin.on('closed', () => {
            ipc.removeAllListeners('org-switch-save')
            resolve(null)
          })
        })

        if (!result || !result.orgVal) return

        const { orgVal, repoVal } = result
        const repoName = repoVal || 'forge-knowledge'

        currentOrg = orgVal
        org.setRepoName(repoName)
        addOrgToHistory(orgVal, repoName)
        writeConfig({ ...readConfig(), org: orgVal, knowledgeRepo: repoName })

        org.syncInBackground(token, orgVal)
        buildTrayMenu()

        dialog.showMessageBox({ icon: appDialogIcon, type: 'info', title: 'Organization Updated', message: `Switched to ${orgVal}/${repoName}.\n\nKnowledge base sync started in the background.` })
      }
    },
    { type: 'separator' },
    {
      label: 'View Knowledge Base',
      enabled: !!currentOrg,
      click: () => {
        const dir = org.cacheDir(currentOrg)
        if (require('fs').existsSync(dir)) {
          shell.openPath(dir)
        } else {
          dialog.showMessageBox({ icon: appDialogIcon, type: 'info', title: 'Knowledge Base', message: `No local cache yet for ${currentOrg}.\n\nForge OS syncs the knowledge base on first launch. Try switching org or restarting.` })
        }
      }
    },
    {
      label: 'Open in Browser',
      enabled: !!serverPort,
      click: () => { if (serverPort) shell.openExternal(`http://127.0.0.1:${serverPort}`) }
    },
    ...(_updateReady ? [{
      label: '⬆  Restart to Update',
      click: () => _notifyUpdateReady()
    }] : [{
      label: 'Check for Updates',
      click: () => checkForUpdatesManual()
    }]),
    { type: 'separator' },
    {
      label: 'Reset Setup & Reconfigure',
      click: async () => {
        const { response } = await dialog.showMessageBox({ icon: appDialogIcon,
          type: 'warning',
          title: 'Reset Setup',
          message: 'This will clear your configuration and restart the setup wizard.',
          detail: 'Your project data will not be deleted.',
          buttons: ['Reset', 'Cancel'],
          defaultId: 1
        })
        if (response !== 0) return
        auth.clearToken()
        fs.rmSync(CONFIG_FILE, { force: true })
        currentUser = null
        currentOrg = null
        isQuitting = true
        killServer()
        app.relaunch()
        app.exit(0)
      }
    },
    {
      label: 'Disconnect GitHub Account',
      click: async () => {
        const { response } = await dialog.showMessageBox({ icon: appDialogIcon,
          type: 'question',
          title: 'Disconnect GitHub Account',
          message: 'Disconnect your GitHub account?',
          detail: 'You will need to re-authenticate the next time you launch Forge OS.',
          buttons: ['Disconnect', 'Cancel'],
          defaultId: 1
        })
        if (response !== 0) return
        auth.clearToken()
        currentUser = null
        currentOrg = null
        writeConfig({ ...readConfig(), user: null, org: null })
        buildTrayMenu()
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true
        killServer()
        app.exit(0)
      }
    }
  ]

  tray.setContextMenu(Menu.buildFromTemplate(menuTemplate))
}

// ─── Auto-updater ─────────────────────────────────────────────────────────────

// In dev mode, allow update checks against the real GitHub release feed.
// dev-app-update.yml must exist in the app directory for this to work.
if (!app.isPackaged) {
  autoUpdater.forceDevUpdateConfig = true
}

// Track whether the current check was triggered manually (tray menu click)
// so we can show "You're up to date" — background checks are silent on no-update.
let _updateCheckManual = false
let _updateReady = false          // true once update-downloaded fires
let _updateChecking = false       // debounce rapid tray clicks

// ─── Update progress window ───────────────────────────────────────────────────

const PROGRESS_WIN_STYLES = `
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden}
  body{
    font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    background:#111;color:#e5e5e5;
    display:flex;flex-direction:column;justify-content:center;
    padding:22px 26px 18px;
    -webkit-app-region:drag;
  }
  .title{font-size:13px;font-weight:600;margin-bottom:2px;letter-spacing:-.1px}
  .sub{font-size:11px;color:#666;margin-bottom:15px}
  .bar-track{background:#1f1f1f;border-radius:4px;height:5px;overflow:hidden;margin-bottom:10px}
  .bar-fill{background:#494fdf;height:100%;border-radius:4px;width:0%;transition:width .25s ease}
  .meta{display:flex;justify-content:space-between;font-size:11px;color:#555}
`

let _progressWin = null

function _formatBytes(bytes) {
  if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  if (bytes >= 1024) return Math.round(bytes / 1024) + ' KB'
  return bytes + ' B'
}

function showProgressWindow(version) {
  if (_progressWin && !_progressWin.isDestroyed()) return
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${PROGRESS_WIN_STYLES}</style></head><body>
    <div class="title">Downloading Forge OS ${version || ''}</div>
    <div class="sub" id="sub">Starting download…</div>
    <div class="bar-track"><div class="bar-fill" id="bar"></div></div>
    <div class="meta"><span id="pct">0%</span><span id="speed"></span></div>
  </body></html>`

  _progressWin = new BrowserWindow({
    width: 380,
    height: 108,
    resizable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    frame: false,
    alwaysOnTop: true,
    webPreferences: { nodeIntegration: false, contextIsolation: true }
  })
  _progressWin.setMenuBarVisibility(false)
  _progressWin.loadFile(writeTempHtml('update-progress', html))
  _progressWin.once('ready-to-show', () => {
    if (_progressWin && !_progressWin.isDestroyed()) _progressWin.show()
  })
  _progressWin.on('closed', () => { _progressWin = null })
}

function updateProgressWindow(pct, speedBps) {
  if (!_progressWin || _progressWin.isDestroyed()) return
  const speedStr = speedBps > 0 ? _formatBytes(speedBps) + '/s' : ''
  const subText = pct < 5 ? 'Starting download…' : 'Downloading update…'
  _progressWin.webContents.executeJavaScript(`
    (function(){
      var b=document.getElementById('bar');   if(b) b.style.width=${JSON.stringify(pct+'%')};
      var p=document.getElementById('pct');   if(p) p.textContent=${JSON.stringify(pct+'%')};
      var s=document.getElementById('speed'); if(s) s.textContent=${JSON.stringify(speedStr)};
      var u=document.getElementById('sub');   if(u) u.textContent=${JSON.stringify(subText)};
    })()
  `).catch(() => {})
}

function closeProgressWindow() {
  if (_progressWin && !_progressWin.isDestroyed()) {
    try { _progressWin.close() } catch (_) {}
    _progressWin = null
  }
}

// ─────────────────────────────────────────────────────────────────────────────

function _applyUpdateNow() {
  isQuitting = true
  killServer()
  if (!app.isPackaged) {
    // quitAndInstall() is a no-op in dev mode (no installer to run).
    // Relaunch the process directly so the flow is testable end-to-end.
    app.relaunch()
    app.exit(0)
  } else {
    // isSilent=false  forceRunAfter=true — quit, run installer, restart app
    autoUpdater.quitAndInstall(false, true)
  }
}

function _notifyUpdateReady() {
  // Update tray tooltip + menu so the user always has a visible signal
  if (tray) {
    tray.setToolTip('Forge OS — Update ready to install')
    buildTrayMenu()   // re-renders menu with "Restart to Update" item
  }

  dialog.showMessageBox({ icon: appDialogIcon,
    type: 'info',
    title: 'Update Ready to Install',
    message: 'A Forge OS update has downloaded and is ready.',
    detail: 'Restart now to apply it, or it will install automatically the next time you quit.',
    buttons: ['Restart Now', 'Later'],
    defaultId: 0
  }).then(({ response }) => {
    if (response === 0) _applyUpdateNow()
  })
}

function setupAutoUpdater() {
  autoUpdater.logger = console
  autoUpdater.autoDownload = false      // manual download so we own the promise and can catch it
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.on('checking-for-update', () => {
    console.log('[updater] Checking for updates…')
  })

  autoUpdater.on('update-available', info => {
    console.log(`[updater] Update available: ${info.version}`)
    _updateCheckManual = false
    _updateChecking = false
    // Show progress window immediately so the user sees something happening
    showProgressWindow(info.version)
    // Start download manually — we own the promise so unhandled rejections are impossible.
    // The 'error' event fires on failure; this .catch() is just the safety net.
    autoUpdater.downloadUpdate().catch(err => {
      console.error('[updater] Download failed:', err.message)
      closeProgressWindow()
      if (tray) tray.setToolTip('Forge OS')
    })
  })

  autoUpdater.on('update-not-available', () => {
    console.log('[updater] Already up to date.')
    if (_updateCheckManual) {
      // Only show dialog when user explicitly asked — background checks stay silent
      dialog.showMessageBox({ icon: appDialogIcon,
        type: 'info',
        title: 'You\'re up to date',
        message: `Forge OS ${FORGE_VERSION} is the latest version.`,
        buttons: ['OK']
      })
    }
    _updateCheckManual = false
    _updateChecking = false
  })

  autoUpdater.on('update-downloaded', info => {
    console.log(`[updater] Update downloaded: ${info.version}`)
    _updateReady = true
    _updateChecking = false
    // Fill bar to 100% briefly, then close and prompt restart
    updateProgressWindow(100, 0)
    setTimeout(() => {
      closeProgressWindow()
      _notifyUpdateReady()
    }, 600)
  })

  autoUpdater.on('download-progress', progress => {
    const pct = Math.round(progress.percent)
    if (tray) tray.setToolTip(`Forge OS — Downloading update ${pct}%`)
    updateProgressWindow(pct, Math.round(progress.bytesPerSecond || 0))
    console.log(`[updater] Download ${pct}% — ${_formatBytes(Math.round(progress.bytesPerSecond || 0))}/s`)
  })

  autoUpdater.on('error', err => {
    console.error('[updater]', err.message)
    closeProgressWindow()
    if (tray) tray.setToolTip('Forge OS')
    if (_updateCheckManual) {
      dialog.showMessageBox({ icon: appDialogIcon,
        type: 'warning',
        title: 'Update Check Failed',
        message: 'Could not check for updates.',
        detail: `${err.message}\n\nCheck your internet connection and try again.`,
        buttons: ['OK']
      })
    }
    _updateCheckManual = false
    _updateChecking = false
  })

  // Background check on startup — silent unless an update is found.
  // The 'error' event handles user-facing errors; .catch() here only suppresses
  // the unhandled-rejection warning when the error event already fired.
  autoUpdater.checkForUpdates().catch(() => {})

  // Periodic background check every 4 hours — keeps long-running sessions current
  setInterval(() => {
    autoUpdater.checkForUpdates().catch(() => {})
  }, 4 * 60 * 60 * 1000)
}

// Called from tray "Check for Updates" — marks intent as manual so "up to date"
// dialog is shown, then fires the check.
function checkForUpdatesManual() {
  if (_updateReady) {
    // Update already downloaded — skip network round-trip, go straight to install prompt
    _notifyUpdateReady()
    return
  }
  if (_updateChecking) return   // debounce rapid clicks
  _updateCheckManual = true
  _updateChecking = true
  if (tray) tray.setToolTip('Forge OS — Checking for updates…')
  // 'error' event handles user-facing dialog; .catch() suppresses unhandled rejection
  autoUpdater.checkForUpdates().catch(() => {})
}

// ─── App lifecycle ────────────────────────────────────────────────────────────

if (!app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (win) { win.show(); win.focus() }
  })

  app.whenReady().then(async () => {

    // Set dock icon and app name explicitly (overrides Electron defaults in dev mode)
    if (process.platform === 'darwin' && app.dock) {
      const dockIconPath = path.join(__dirname, 'assets', 'icon-512.png')
      if (fs.existsSync(dockIconPath)) {
        app.dock.setIcon(nativeImage.createFromPath(dockIconPath))
      }
    }

    // 1. Python check
    if (!PYTHON3) {
      dialog.showErrorBox(
        'Python 3 Required',
        'Forge OS requires Python 3 to run.\n\nInstall it from https://python.org/downloads and relaunch the app.'
      )
      app.exit(1)
      return
    }

    // Poll for PAT signal file written by the server when user saves a new token in Settings
    const os = require('os')
    const PAT_SIGNAL = path.join(os.homedir(), '.forge', '_pat_signal')
    setInterval(() => {
      if (fs.existsSync(PAT_SIGNAL)) {
        try {
          const newPat = fs.readFileSync(PAT_SIGNAL, 'utf8').trim()
          fs.unlinkSync(PAT_SIGNAL)
          if (newPat) auth.storeGitPat(newPat)
        } catch (_) {}
      }
    }, 2000)

    // 2. First-launch setup wizard (runs once per machine — admin or member onboarding)
    if (needsSetup()) {
      try {
        const setupResult = await createSetupWindow()
        // For member flow: if the org repo is private, githubClientId may arrive
        // after the first successful auth. It's stored in config for the next run.
        if (setupResult.githubClientId) {
          console.log(`[setup] Admin setup complete. Org: ${setupResult.org}`)
        } else {
          console.log(`[setup] Member setup complete. Org: ${setupResult.org}`)
        }
      } catch (err) {
        // User closed setup window without completing — exit cleanly.
        app.exit(0)
        return
      }
    }

    // 3. Authenticate (device flow if no stored token; offline-tolerant if network down)
    let token
    try {
      const result = await authenticate()
      token = result.token
    } catch (err) {
      if (err.message === 'Authentication cancelled.') {
        app.exit(0)
        return
      }
      dialog.showErrorBox('Authentication Error', err.message)
      app.exit(1)
      return
    }

    // 4. Background org sync — non-blocking, does not delay startup
    if (token && currentOrg) {
      org.syncInBackground(token, currentOrg).catch(err => {
        console.warn('[org] Background sync error:', err.message)
      })
    }

    // 5. Resolve orchestrator data dir — lives inside ~/.forge/projects/<uuid>/
    // Projects are created and managed there via the dashboard. No folder picker.
    const homeDir = app.getPath('home')
    const projectsRoot = path.join(homeDir, '.forge', 'projects')

    // Find the best available data dir.
    // Priority: (1) index.json active_project_id, (2) any non-archived index project,
    // (3) most-recently-modified UUID dir with scripts (deterministic across restarts).
    function resolveOrchestratorDataDir() {
      if (!fs.existsSync(projectsRoot)) return null
      const indexPath = path.join(projectsRoot, 'index.json')
      if (fs.existsSync(indexPath)) {
        try {
          const idx = JSON.parse(fs.readFileSync(indexPath, 'utf8'))
          const activeId = idx.active_project_id
          if (activeId) {
            const candidate = path.join(projectsRoot, activeId)
            if (fs.existsSync(path.join(candidate, 'scripts', 'server.py'))) return candidate
          }
          for (const p of (idx.projects || [])) {
            if (p.status === 'archived') continue
            const candidate = path.join(projectsRoot, p.id)
            if (fs.existsSync(path.join(candidate, 'scripts', 'server.py'))) return candidate
          }
        } catch (_) {}
      }
      // Fallback: scan dirs, pick the most recently modified one with server.py
      // (avoids random inode-order selection that varies across OS restarts)
      let best = null, bestMtime = 0
      try {
        for (const entry of fs.readdirSync(projectsRoot)) {
          const candidate = path.join(projectsRoot, entry)
          const serverPy = path.join(candidate, 'scripts', 'server.py')
          if (!fs.existsSync(serverPy)) continue
          try {
            const mtime = fs.statSync(serverPy).mtimeMs
            if (mtime > bestMtime) { bestMtime = mtime; best = candidate }
          } catch (_) {}
        }
      } catch (_) {}
      return best
    }

    // Bootstrap: ensure ~/.forge/projects/ exists and has at least one data dir
    fs.mkdirSync(projectsRoot, { recursive: true })

    let forgeDataDir = resolveOrchestratorDataDir()

    // If no valid data dir found, create a fresh one.
    // We create the directory, write a temporary .forge dotfile, run forge init
    // (which populates scripts/), then remove the dotfile.
    if (!forgeDataDir) {
      const newId = (() => { try { return require('crypto').randomUUID() } catch (_) { return Date.now().toString() } })()
      const newDir = path.join(projectsRoot, newId)
      fs.mkdirSync(newDir, { recursive: true })
      const newDotfile = path.join(newDir, '.forge')
      try {
        fs.writeFileSync(newDotfile, JSON.stringify({
          project_id: newId,
          project_name: 'forge-orchestrator',
          data_dir: newDir
        }, null, 2), { mode: 0o600 })
        execFileSync(PYTHON3 || 'python3', [forgeBinaryPath(), 'init'], {
          stdio: 'ignore',
          env: { ...process.env, FORGE_REPO_ROOT: newDir }
        })
      } catch (_) {}
      // Remove dotfile — the data dir is self-contained, no project root needed
      try { fs.unlinkSync(newDotfile) } catch (_) {}
      forgeDataDir = resolveOrchestratorDataDir()
    }

    if (!forgeDataDir) {
      dialog.showErrorBox('Forge OS', 'Could not initialize Forge data directory.\nPlease reinstall the app.')
      app.exit(1); return
    }

    // Keep scripts fresh: run forge upgrade against the data dir by injecting a
    // temporary .forge dotfile so the forge binary can locate the data directory.
    // This ensures server.py + dashboard.html are always current after app updates.
    const tmpDotfile = path.join(forgeDataDir, '.forge')
    const hadDotfile = fs.existsSync(tmpDotfile)
    if (!hadDotfile) {
      try {
        fs.writeFileSync(tmpDotfile, JSON.stringify({
          project_id: path.basename(forgeDataDir),
          project_name: 'forge-orchestrator',
          data_dir: forgeDataDir
        }, null, 2), { mode: 0o600 })
      } catch (_) {}
    }
    try {
      execFileSync(PYTHON3 || 'python3', [forgeBinaryPath(), 'upgrade'], {
        stdio: 'ignore',
        env: { ...process.env, FORGE_REPO_ROOT: forgeDataDir }
      })
    } catch (_) {}
    // Clean up temporary dotfile if we created it
    if (!hadDotfile && fs.existsSync(tmpDotfile)) {
      try { fs.unlinkSync(tmpDotfile) } catch (_) {}
    }

    // Ensure index.json exists (server will create it on first load_projects_index call,
    // but writing it here makes resolveOrchestratorDataDir deterministic on next start)
    const indexPath = path.join(projectsRoot, 'index.json')
    if (!fs.existsSync(indexPath)) {
      try {
        fs.writeFileSync(indexPath, JSON.stringify({
          active_project_id: '',
          projects: []
        }, null, 2), { mode: 0o600 })
      } catch (_) {}
    }

    writeConfig({ ...readConfig(), projectPath: homeDir })

    // 7. Start Python server
    serverPort = await getFreePort()
    startServer(homeDir, forgeDataDir, serverPort)

    // 8. Create window and tray
    createWindow(serverPort)
    createTray()
    setupAutoUpdater()

    // 9. Wait for server, then load URL and show window
    try {
      await waitForServer(serverPort)
      win.loadURL(`http://127.0.0.1:${serverPort}`)
      win.show()
    } catch (err) {
      dialog.showErrorBox(
        'Server Failed to Start',
        `Forge OS could not start the document server.\n\n${err.message}\n\nEnsure .forge/scripts/server.py exists in your project folder.`
      )
      isQuitting = true
      killServer()
      app.exit(1)
    }
  })

  app.on('activate', () => {
    if (win) { win.show(); win.focus() }
  })

  app.on('window-all-closed', () => {
    // Intentionally do nothing — app lives in the tray on all platforms
  })

  app.on('before-quit', () => {
    isQuitting = true
    killServer()
  })
}
