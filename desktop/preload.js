'use strict'

// Phase 1: no IPC bridge needed — dashboard communicates via HTTP to localhost
// This file satisfies Electron's contextIsolation requirement.
window.addEventListener('DOMContentLoaded', () => {})
