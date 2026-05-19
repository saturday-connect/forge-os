'use strict'

/**
 * GitHub Device Flow authentication.
 *
 * The GitHub OAuth App Client ID is stored in userData/config.json by the
 * setup wizard (admin flow) or pulled from the org's forge-knowledge repo
 * (member flow). It is never hardcoded in source.
 *
 * The client_id is not sensitive — device flow does not use client_secret.
 */

const { app, safeStorage, shell, BrowserWindow, ipcMain } = require('electron')
const https = require('https')
const path = require('path')
const fs = require('fs')

const CONFIG_FILE = path.join(app.getPath('userData'), 'config.json')
const TOKEN_FILE = path.join(app.getPath('userData'), 'gh_token.enc')
const GIT_PAT_FILE = path.join(app.getPath('userData'), 'git_pat.enc')
const OAUTH_SCOPES = 'read:org,repo'

function getClientId() {
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'))
    if (config.githubClientId) return config.githubClientId
  } catch (_) {}
  throw new Error(
    'GitHub OAuth App is not configured.\n\n' +
    'Launch Forge OS setup to register your GitHub OAuth App and obtain a Client ID.'
  )
}

// ─── Token storage ────────────────────────────────────────────────────────────

function isEncryptionAvailable() {
  return safeStorage.isEncryptionAvailable()
}

function storeToken(token) {
  if (!isEncryptionAvailable()) {
    throw new Error(
      'Secure credential storage is unavailable on this system.\n\n' +
      'On Linux, install libsecret:\n  sudo apt install libsecret-1-0\n\n' +
      'Then restart Forge OS.'
    )
  }
  const encrypted = safeStorage.encryptString(token)
  fs.mkdirSync(path.dirname(TOKEN_FILE), { recursive: true })
  fs.writeFileSync(TOKEN_FILE, encrypted)
}

function loadToken() {
  if (!fs.existsSync(TOKEN_FILE)) return null
  if (!isEncryptionAvailable()) return null
  try {
    const encrypted = fs.readFileSync(TOKEN_FILE)
    return safeStorage.decryptString(encrypted)
  } catch (_) {
    fs.unlinkSync(TOKEN_FILE)
    return null
  }
}

function clearToken() {
  try {
    if (fs.existsSync(TOKEN_FILE)) fs.unlinkSync(TOKEN_FILE)
  } catch (_) {}
}

// ─── Git PAT storage (same safeStorage mechanism as OAuth token) ──────────────

function storeGitPat(pat) {
  if (!isEncryptionAvailable()) return
  const encrypted = safeStorage.encryptString(pat)
  fs.mkdirSync(path.dirname(GIT_PAT_FILE), { recursive: true })
  fs.writeFileSync(GIT_PAT_FILE, encrypted, { mode: 0o600 })
}

function loadGitPat() {
  if (!fs.existsSync(GIT_PAT_FILE)) return null
  if (!isEncryptionAvailable()) return null
  try {
    const encrypted = fs.readFileSync(GIT_PAT_FILE)
    return safeStorage.decryptString(encrypted)
  } catch (_) {
    fs.unlinkSync(GIT_PAT_FILE)
    return null
  }
}

function clearGitPat() {
  try {
    if (fs.existsSync(GIT_PAT_FILE)) fs.unlinkSync(GIT_PAT_FILE)
  } catch (_) {}
}

// ─── Device flow HTTP ─────────────────────────────────────────────────────────

function post(hostname, path, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(body)
    const req = https.request(
      {
        hostname,
        path,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          'Content-Length': Buffer.byteLength(payload),
          'User-Agent': 'forge-os-desktop',
          ...headers
        }
      },
      res => {
        let raw = ''
        res.on('data', c => { raw += c })
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, body: JSON.parse(raw) })
          } catch (_) {
            reject(new Error(`Unexpected response from GitHub auth: ${raw.slice(0, 200)}`))
          }
        })
      }
    )
    req.on('error', reject)
    req.setTimeout(12000, () => { req.destroy(); reject(new Error('GitHub auth request timed out.')) })
    req.write(payload)
    req.end()
  })
}

async function requestDeviceCode() {
  const res = await post('github.com', '/login/device/code', {
    client_id: getClientId(),
    scope: OAUTH_SCOPES
  })
  if (res.body.error) {
    throw new Error(res.body.error_description || `Device code request failed: ${res.body.error}`)
  }
  return res.body
}

function pollForToken(deviceCode, intervalSec) {
  return new Promise((resolve, reject) => {
    let delayMs = Math.max((intervalSec + 1) * 1000, 6000)
    let cancelled = false

    ipcMain.once('auth-cancel', () => {
      cancelled = true
      reject(new Error('Authentication cancelled.'))
    })

    const attempt = async () => {
      if (cancelled) return

      let res
      try {
        res = await post('github.com', '/login/oauth/access_token', {
          client_id: getClientId(),
          device_code: deviceCode,
          grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
        })
      } catch (networkErr) {
        if (!cancelled) setTimeout(attempt, delayMs)
        return
      }

      const b = res.body

      if (b.access_token) {
        ipcMain.removeAllListeners('auth-cancel')
        return resolve(b.access_token)
      }

      switch (b.error) {
        case 'authorization_pending':
          setTimeout(attempt, delayMs)
          break
        case 'slow_down':
          delayMs = Math.min(delayMs + 5000, 30000)
          setTimeout(attempt, delayMs)
          break
        case 'expired_token':
          reject(new Error('The authorization code expired. Please try again.'))
          break
        case 'access_denied':
          reject(new Error('GitHub authorization was denied.'))
          break
        default:
          reject(new Error(b.error_description || `Unexpected auth error: ${b.error}`))
      }
    }

    attempt()
  })
}

// ─── Auth window ──────────────────────────────────────────────────────────────

function createAuthWindow() {
  const win = new BrowserWindow({
    width: 460,
    height: 420,      // +40 to absorb hiddenInset top padding without squishing content
    resizable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    title: 'Connect GitHub Account',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      preload: path.join(__dirname, 'auth-preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })
  win.setMenuBarVisibility(false)
  win.loadFile(path.join(__dirname, 'auth-window.html'))
  return win
}

function sendToAuthWindow(win, event, data) {
  if (!win || win.isDestroyed()) return
  win.webContents.send(event, data)
}

// ─── Public: run full auth flow ───────────────────────────────────────────────

/**
 * Run the GitHub Device Flow and return a valid access token.
 * If the user already has a stored token it is returned immediately.
 * On GITHUB_UNAUTHORIZED errors the caller should call runAuthFlow() again.
 */
async function runAuthFlow() {
  let deviceData
  try {
    deviceData = await requestDeviceCode()
  } catch (err) {
    throw new Error(`Failed to contact GitHub: ${err.message}`)
  }

  const authWin = createAuthWindow()

  // Wait for the window to be ready before sending initial state
  await new Promise(resolve => authWin.webContents.once('did-finish-load', resolve))

  sendToAuthWindow(authWin, 'auth-status', {
    state: 'waiting',
    code: deviceData.user_code,
    url: deviceData.verification_uri,
    expiresIn: deviceData.expires_in
  })

  shell.openExternal(deviceData.verification_uri)

  try {
    const token = await pollForToken(deviceData.device_code, deviceData.interval)
    sendToAuthWindow(authWin, 'auth-status', { state: 'success' })
    await new Promise(r => setTimeout(r, 1200))
    authWin.close()
    return token
  } catch (err) {
    if (!authWin.isDestroyed()) {
      sendToAuthWindow(authWin, 'auth-status', { state: 'error', message: err.message })
      // Keep window open so user can retry — caller handles the retry loop
      await new Promise(resolve => {
        ipcMain.once('auth-retry', resolve)
        authWin.once('closed', () => resolve(null))
      })
      if (!authWin.isDestroyed()) authWin.close()
    }
    throw err
  }
}

/**
 * Ensure a valid token exists. Shows auth flow if needed.
 * Retries indefinitely until the user authenticates or closes the window.
 */
async function ensureAuthenticated() {
  const stored = loadToken()
  if (stored) return stored

  while (true) {
    try {
      const token = await runAuthFlow()
      storeToken(token)
      return token
    } catch (err) {
      if (err.message === 'Authentication cancelled.') {
        throw err
      }
      // Any other error: loop back to show auth window again
    }
  }
}

module.exports = { ensureAuthenticated, loadToken, storeToken, clearToken, runAuthFlow, storeGitPat, loadGitPat, clearGitPat }
