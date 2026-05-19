'use strict'

const { contextBridge, ipcRenderer } = require('electron')

// Expose a minimal, typed IPC surface for the dashboard.
// The dashboard communicates with the server via HTTP; this bridge covers
// Electron-only events that cannot go through HTTP (update notifications, etc.).
contextBridge.exposeInMainWorld('forgeElectron', {
  // Called by main when an update has downloaded and is ready to install.
  onUpdateReady: (cb) => ipcRenderer.on('forge:update-ready', (_e, info) => cb(info)),
  // Called by main to clear the update banner (e.g. stale ghost update cleared).
  onUpdateCleared: (cb) => ipcRenderer.on('forge:update-cleared', () => cb()),
  // User clicked "Restart Now" in the in-app banner.
  installUpdate: () => ipcRenderer.send('forge:install-update'),
  // User clicked "Later" — hides the banner for this session.
  dismissUpdate: () => ipcRenderer.send('forge:dismiss-update'),
})
