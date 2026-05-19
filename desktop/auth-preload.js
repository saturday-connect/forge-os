'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  onAuthStatus: (callback) => {
    ipcRenderer.on('auth-status', (_event, data) => callback(data))
  },
  copyCode: () => ipcRenderer.send('auth-copy-code'),
  cancel: () => ipcRenderer.send('auth-cancel'),
  retry: () => ipcRenderer.send('auth-retry')
})
