'use strict'

const https = require('https')

const API_HOST = 'api.github.com'
const DEFAULT_TIMEOUT_MS = 15000
const MAX_RETRIES = 3

// ─── Core HTTP ────────────────────────────────────────────────────────────────

function apiRequest(token, method, path, body = null, attempt = 0) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null
    const options = {
      hostname: API_HOST,
      path,
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'forge-os-desktop'
      }
    }
    if (payload) {
      options.headers['Content-Type'] = 'application/json'
      options.headers['Content-Length'] = Buffer.byteLength(payload)
    }

    const req = https.request(options, res => {
      let raw = ''
      res.on('data', chunk => { raw += chunk })
      res.on('end', () => {
        const remaining = parseInt(res.headers['x-ratelimit-remaining'] ?? '60', 10)
        const reset = parseInt(res.headers['x-ratelimit-reset'] ?? '0', 10)

        if (res.statusCode === 429 || remaining === 0) {
          const waitMs = Math.max(0, reset * 1000 - Date.now()) + 2000
          setTimeout(() => apiRequest(token, method, path, body, attempt).then(resolve).catch(reject), waitMs)
          return
        }

        if (res.statusCode === 401) {
          const err = new Error('GitHub token is invalid or has expired.')
          err.code = 'GITHUB_UNAUTHORIZED'
          return reject(err)
        }

        if (res.statusCode === 403) {
          const err = new Error('Insufficient permissions. Check your GitHub OAuth scopes.')
          err.code = 'GITHUB_FORBIDDEN'
          return reject(err)
        }

        if (res.statusCode === 404) {
          const err = new Error(`Resource not found: ${path}`)
          err.code = 'GITHUB_NOT_FOUND'
          return reject(err)
        }

        if (res.statusCode >= 500 && attempt < MAX_RETRIES) {
          const backoff = Math.pow(2, attempt) * 1000
          setTimeout(() => apiRequest(token, method, path, body, attempt + 1).then(resolve).catch(reject), backoff)
          return
        }

        if (res.statusCode >= 400) {
          let message = `GitHub API error ${res.statusCode}`
          try { message = JSON.parse(raw).message || message } catch (_) {}
          return reject(new Error(message))
        }

        if (res.statusCode === 204 || !raw.trim()) return resolve(null)

        try {
          resolve(JSON.parse(raw))
        } catch (_) {
          reject(new Error(`Failed to parse GitHub response for ${path}`))
        }
      })
    })

    req.on('error', err => {
      if (attempt < MAX_RETRIES) {
        const backoff = Math.pow(2, attempt) * 1000
        setTimeout(() => apiRequest(token, method, path, body, attempt + 1).then(resolve).catch(reject), backoff)
      } else {
        reject(err)
      }
    })

    req.setTimeout(DEFAULT_TIMEOUT_MS, () => {
      req.destroy()
      reject(new Error(`GitHub API request timed out: ${method} ${path}`))
    })

    if (payload) req.write(payload)
    req.end()
  })
}

async function paginate(token, path) {
  const results = []
  let nextPath = path.includes('?') ? `${path}&per_page=100` : `${path}?per_page=100`

  while (nextPath) {
    const data = await new Promise((resolve, reject) => {
      const options = {
        hostname: API_HOST,
        path: nextPath,
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'User-Agent': 'forge-os-desktop'
        }
      }

      const req = https.request(options, res => {
        let raw = ''
        res.on('data', c => { raw += c })
        res.on('end', () => {
          if (res.statusCode === 401) {
            const err = new Error('GitHub token is invalid or has expired.')
            err.code = 'GITHUB_UNAUTHORIZED'
            return reject(err)
          }
          const link = res.headers['link'] || ''
          const match = link.match(/<https:\/\/api\.github\.com([^>]+)>;\s*rel="next"/)
          try {
            resolve({ data: JSON.parse(raw), next: match ? match[1] : null })
          } catch (_) {
            reject(new Error('Failed to parse paginated response'))
          }
        })
      })

      req.on('error', reject)
      req.setTimeout(DEFAULT_TIMEOUT_MS, () => { req.destroy(); reject(new Error('Paginated request timed out')) })
      req.end()
    })

    if (Array.isArray(data.data)) results.push(...data.data)
    nextPath = data.next
  }

  return results
}

// ─── Public API ───────────────────────────────────────────────────────────────

async function getAuthenticatedUser(token) {
  return apiRequest(token, 'GET', '/user')
}

async function getUserOrgs(token) {
  return paginate(token, '/user/orgs')
}

async function repoExists(token, owner, repo) {
  try {
    await apiRequest(token, 'GET', `/repos/${owner}/${repo}`)
    return true
  } catch (err) {
    if (err.code === 'GITHUB_NOT_FOUND') return false
    throw err
  }
}

async function getRepoTree(token, owner, repo, branch = 'main') {
  try {
    const branch_data = await apiRequest(token, 'GET', `/repos/${owner}/${repo}/branches/${branch}`)
    const treeSha = branch_data.commit.commit.tree.sha
    const tree = await apiRequest(token, 'GET', `/repos/${owner}/${repo}/git/trees/${treeSha}?recursive=1`)
    return { treeSha, files: tree.tree.filter(n => n.type === 'blob') }
  } catch (err) {
    if (err.code === 'GITHUB_NOT_FOUND') {
      // Try 'master' if 'main' not found
      if (branch === 'main') return getRepoTree(token, owner, repo, 'master')
    }
    throw err
  }
}

async function getFileContent(token, owner, repo, filePath) {
  const data = await apiRequest(token, 'GET', `/repos/${owner}/${repo}/contents/${encodeURIComponent(filePath)}`)
  if (!data.content) throw new Error(`No content returned for ${filePath}`)
  return Buffer.from(data.content.replace(/\n/g, ''), 'base64').toString('utf8')
}

async function putFileContent(token, owner, repo, filePath, content, commitMessage, existingSha = null) {
  const body = {
    message: commitMessage,
    content: Buffer.from(content, 'utf8').toString('base64')
  }
  if (existingSha) body.sha = existingSha
  return apiRequest(token, 'PUT', `/repos/${owner}/${repo}/contents/${encodeURIComponent(filePath)}`, body)
}

async function getFileSha(token, owner, repo, filePath) {
  try {
    const data = await apiRequest(token, 'GET', `/repos/${owner}/${repo}/contents/${encodeURIComponent(filePath)}`)
    return data.sha
  } catch (err) {
    if (err.code === 'GITHUB_NOT_FOUND') return null
    throw err
  }
}

module.exports = {
  getAuthenticatedUser,
  getUserOrgs,
  repoExists,
  getRepoTree,
  getFileContent,
  putFileContent,
  getFileSha
}
