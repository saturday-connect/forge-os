const { notarize } = require('@electron/notarize')

exports.default = async function notarizing(context) {
  const { electronPlatformName, appOutDir } = context
  if (electronPlatformName !== 'darwin') return

  const appleId       = process.env.APPLE_ID
  const appleIdPass   = process.env.APPLE_ID_PASSWORD
  const teamId        = process.env.APPLE_TEAM_ID

  // Skip silently if secrets are not configured
  if (!appleId || !appleIdPass || !teamId) {
    console.log('[notarize] Skipping — APPLE_ID / APPLE_ID_PASSWORD / APPLE_TEAM_ID not set.')
    return
  }

  const appName = context.packager.appInfo.productFilename
  const appPath = `${appOutDir}/${appName}.app`

  console.log(`[notarize] Submitting ${appPath} to Apple notarization service…`)

  await notarize({
    appPath,
    appleId,
    appleIdPassword: appleIdPass,
    teamId,
  })

  console.log('[notarize] Done.')
}
