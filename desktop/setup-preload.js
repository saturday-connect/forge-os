'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('setupAPI', {
  openUrl: (url) => ipcRenderer.send('setup-open-url', url),
  copyToClipboard: (text) => ipcRenderer.send('setup-copy-clipboard', text),
  verifyOrg: (orgName, repoName) => ipcRenderer.invoke('setup-verify-org', orgName, repoName),
  fetchOrgConfig: (orgName) => ipcRenderer.invoke('setup-fetch-org-config', orgName),
  gitStatus: () => ipcRenderer.invoke('setup-git-status'),
  gitConfig: (name, email) => ipcRenderer.invoke('setup-git-config', name, email),
  sshGenerate: () => ipcRenderer.invoke('setup-ssh-generate'),
  sshTest: () => ipcRenderer.invoke('setup-ssh-test'),
  sshUnlock: (passphrase) => ipcRenderer.invoke('setup-ssh-unlock', passphrase),
  saveSetup: (config) => ipcRenderer.send('setup-save', config)
})
