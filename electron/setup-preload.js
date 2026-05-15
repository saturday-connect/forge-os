'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('setupAPI', {
  openUrl: (url) => ipcRenderer.send('setup-open-url', url),
  verifyOrg: (orgName) => ipcRenderer.invoke('setup-verify-org', orgName),
  fetchOrgConfig: (orgName) => ipcRenderer.invoke('setup-fetch-org-config', orgName),
  saveSetup: (config) => ipcRenderer.send('setup-save', config)
})
