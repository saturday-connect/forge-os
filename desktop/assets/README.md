# App Icons

Place the following icon files here before building:

| File | Size | Used for |
|---|---|---|
| `icon.png` | 512×512 | Linux tray + AppImage |
| `icon.icns` | macOS bundle | macOS .app (electron-builder generates from .png if `electron-icon-builder` is run) |
| `icon.ico` | Windows bundle | Windows .exe (electron-builder generates from .png if `electron-icon-builder` is run) |

## Generating from a single PNG

```bash
npm install --save-dev electron-icon-builder
npx electron-icon-builder --input=assets/icon.png --output=assets/
```

## macOS entitlements (required for notarization)

Place `entitlements.mac.plist` here with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>com.apple.security.cs.allow-jit</key><true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key><true/>
    <key>com.apple.security.cs.disable-library-validation</key><true/>
  </dict>
</plist>
```
