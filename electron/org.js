'use strict'

/**
 * Org repo operations.
 *
 * Discovers github.com/{org}/forge-knowledge across the authenticated user's orgs,
 * syncs its contents to ~/.forge/org-cache/{org}/ using the GitHub Contents API
 * (no git binary required), and exposes the parsed forge.config.json.
 *
 * Sync is delta-based: files are only downloaded when their SHA has changed.
 * The cache is considered fresh for CACHE_TTL_MS after the last sync; startup
 * skips a network round-trip when the cache is warm.
 */

const { app } = require('electron')
const github = require('./github')
const fs = require('fs')
const path = require('path')

let REPO_NAME = 'forge-knowledge'

function setRepoName(name) {
  if (name && typeof name === 'string') REPO_NAME = name.trim()
}
const CACHE_ROOT = path.join(app.getPath('home'), '.forge', 'org-cache')
const CACHE_TTL_MS = 60 * 60 * 1000   // 1 hour
const META_FILE = '.sync_meta.json'
const CONFIG_FILE = 'forge.config.json'

// ─── Cache helpers ────────────────────────────────────────────────────────────

function cacheDir(orgLogin) {
  return path.join(CACHE_ROOT, orgLogin)
}

function readMeta(orgLogin) {
  const file = path.join(cacheDir(orgLogin), META_FILE)
  if (!fs.existsSync(file)) return null
  try { return JSON.parse(fs.readFileSync(file, 'utf8')) } catch (_) { return null }
}

function writeMeta(orgLogin, meta) {
  const dir = cacheDir(orgLogin)
  fs.mkdirSync(dir, { recursive: true })
  fs.writeFileSync(path.join(dir, META_FILE), JSON.stringify(meta, null, 2))
}

function isCacheFresh(orgLogin) {
  const meta = readMeta(orgLogin)
  if (!meta?.synced_at) return false
  return Date.now() - new Date(meta.synced_at).getTime() < CACHE_TTL_MS
}

// ─── Org discovery ────────────────────────────────────────────────────────────

/**
 * Returns all orgs the user belongs to that have a forge-knowledge repo.
 * Checks in parallel (one request per org) and returns login names.
 */
async function discoverOrgs(token) {
  const orgs = await github.getUserOrgs(token)
  if (!orgs.length) return []

  const checks = orgs.map(async org => {
    try {
      const exists = await github.repoExists(token, org.login, REPO_NAME)
      return exists ? org.login : null
    } catch (_) {
      return null
    }
  })

  const results = await Promise.all(checks)
  return results.filter(Boolean)
}

// ─── Sync ─────────────────────────────────────────────────────────────────────

/**
 * Sync the forge-knowledge repo for orgLogin to the local cache.
 * Uses delta sync: only fetches files whose SHA differs from the cached version.
 * Returns the number of files updated.
 */
async function syncOrg(token, orgLogin) {
  const dir = cacheDir(orgLogin)
  fs.mkdirSync(dir, { recursive: true })

  let tree
  try {
    tree = await github.getRepoTree(token, orgLogin, REPO_NAME)
  } catch (err) {
    if (err.code === 'GITHUB_NOT_FOUND') return 0
    throw err
  }

  const meta = readMeta(orgLogin) || { files: {} }
  const prevFiles = meta.files || {}
  const nextFiles = {}
  let updated = 0

  for (const node of tree.files) {
    nextFiles[node.path] = node.sha

    if (prevFiles[node.path] === node.sha) continue  // unchanged

    let content
    try {
      content = await github.getFileContent(token, orgLogin, REPO_NAME, node.path)
    } catch (err) {
      console.error(`[org] Failed to fetch ${node.path}: ${err.message}`)
      continue
    }

    const localPath = path.join(dir, node.path)
    fs.mkdirSync(path.dirname(localPath), { recursive: true })
    fs.writeFileSync(localPath, content, 'utf8')
    updated++
  }

  // Remove locally cached files that no longer exist in the remote
  for (const cachedPath of Object.keys(prevFiles)) {
    if (!nextFiles[cachedPath]) {
      const localPath = path.join(dir, cachedPath)
      try { if (fs.existsSync(localPath)) fs.unlinkSync(localPath) } catch (_) {}
    }
  }

  writeMeta(orgLogin, {
    synced_at: new Date().toISOString(),
    tree_sha: tree.treeSha,
    files: nextFiles
  })

  return updated
}

/**
 * Fire-and-forget sync. Logs errors but never throws.
 * Call this after app startup to keep the cache warm without blocking the UI.
 */
async function syncInBackground(token, orgLogin) {
  if (!orgLogin) return
  if (isCacheFresh(orgLogin)) return
  try {
    const n = await syncOrg(token, orgLogin)
    if (n > 0) console.log(`[org] Synced ${n} file(s) from ${orgLogin}/${REPO_NAME}`)
  } catch (err) {
    console.warn(`[org] Background sync failed for ${orgLogin}: ${err.message}`)
  }
}

// ─── Config ───────────────────────────────────────────────────────────────────

/**
 * Read and parse forge.config.json from the org cache.
 * Returns null if not found or unparseable.
 */
function readOrgConfig(orgLogin) {
  if (!orgLogin) return null
  const file = path.join(cacheDir(orgLogin), CONFIG_FILE)
  if (!fs.existsSync(file)) return null
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'))
  } catch (err) {
    console.warn(`[org] Failed to parse ${CONFIG_FILE} for ${orgLogin}: ${err.message}`)
    return null
  }
}

/**
 * Resolve the user's role within the org.
 * Returns 'admin', 'member', or 'viewer'. Defaults to 'member' if unlisted.
 */
function resolveUserRole(orgLogin, githubLogin) {
  const config = readOrgConfig(orgLogin)
  if (!config?.users) return 'member'
  const entry = config.users.find(u => u.github?.toLowerCase() === githubLogin?.toLowerCase())
  return entry?.role ?? 'member'
}

/**
 * List all knowledge, pattern, and agent files in the org cache.
 * Returns an array of absolute paths.
 */
function listOrgContextFiles(orgLogin) {
  if (!orgLogin) return []
  const dir = cacheDir(orgLogin)
  const contextDirs = ['knowledge', 'patterns', 'agents']
  const files = []

  for (const sub of contextDirs) {
    const subDir = path.join(dir, sub)
    if (!fs.existsSync(subDir)) continue
    for (const entry of fs.readdirSync(subDir, { withFileTypes: true })) {
      if (entry.isFile() && entry.name.endsWith('.md')) {
        files.push(path.join(subDir, entry.name))
      }
    }
  }

  return files
}

/**
 * Push a file into the org repo. Used by the learning loop (Phase 5).
 * Creates or updates the file with a commit message.
 */
async function pushToOrg(token, orgLogin, repoPath, content, commitMessage) {
  const sha = await github.getFileSha(token, orgLogin, REPO_NAME, repoPath)
  await github.putFileContent(token, orgLogin, REPO_NAME, repoPath, content, commitMessage, sha)

  // Invalidate the local cache entry so next sync picks it up
  const meta = readMeta(orgLogin)
  if (meta?.files) {
    delete meta.files[repoPath]
    writeMeta(orgLogin, meta)
  }
}

module.exports = {
  discoverOrgs,
  syncOrg,
  syncInBackground,
  readOrgConfig,
  resolveUserRole,
  listOrgContextFiles,
  pushToOrg,
  cacheDir,
  setRepoName
}
