# Forge OS

Documentation-first PDLC and build orchestration framework. Treats Markdown files and generated runtime state as the control plane for product planning, generation, review, build, and deployment.

## What It Does

Forge sits at the repository root as a top-level orchestrator and manages multiple generated projects under `.projects/`. The full lifecycle:

```
Projects → Input → Generate → Review → Build → Deploy
```

Each project gets a `.forge/` directory containing all generated documentation, build artifacts, gate state, and runtime scripts. The web dashboard drives the entire lifecycle from a browser — or use the native desktop app for macOS, Windows, and Linux.

## Requirements

- Python 3.8+ (stdlib only, no pip dependencies)
- Node.js 22+ (for Electron desktop app only)
- GitHub CLI `gh` (optional, for secrets push and PR automation)

## Quick Start

**Build the `forge` binary:**

```bash
python3 src/build_forge.py
```

**Initialize the root orchestrator:**

```bash
./forge init
./forge upgrade
```

**Start the dashboard:**

```bash
./forge dashboard 8080
```

Then open `http://localhost:8080` in your browser.

**Or use `dev` mode** (build + init + serve in one command):

```bash
./forge dev 8080
```

## CLI Reference

| Command | Description |
|---|---|
| `./forge version` | Print version |
| `./forge init` | Initialize `.forge/` in current directory |
| `./forge --project <path> init` | Initialize a specific project |
| `./forge upgrade` | Update generated runtime files, preserve state |
| `./forge generate <stage>` | Generate one documentation stage |
| `./forge pipeline` | Run all documentation stages |
| `./forge dashboard [port]` | Start dashboard server (default: 8080) |
| `./forge dev [port]` | Build, init, and serve in one step |

`--project <path>` goes before the command when targeting a specific project.

## Supported AI Tools

| Tool | Models |
|---|---|
| Gemini CLI | Gemini 3 Flash, Gemini 3 Pro, Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash Lite |
| Claude Code CLI | Claude Sonnet 4.6, Claude Opus 4.7, Claude Haiku 4.5 |
| Codex CLI | o4 Mini, o3, GPT-5.5, GPT-4.1, GPT-4.1 Mini |
| OpenAI API | GPT-5.5, GPT-4o, GPT-4o Mini, o3 Mini |

Configure the active tool and model in dashboard Settings or via `FORGE_TOOL` / `FORGE_MODEL` environment variables.

## Source Layout

```
src/build_forge.py                compiler — assembles the forge binary
src/runtime/forge_cli.py.tmpl     CLI template
src/runtime/server.py             dashboard API server
src/runtime/build_runner.py       build-system runner
src/dashboard/index.html          dashboard HTML shell
src/dashboard/styles.css          dashboard styles
src/dashboard/scripts/*.js        dashboard JavaScript, assembled in order
src/dashboard/DESIGN.md           design contract
forge                             built binary (generated)
desktop/                          desktop app wrapper (Electron)
desktop/assets/                   app icons and macOS entitlements
docs/                             GitHub Pages product site
.github/workflows/                CI — builds macOS DMG, Windows installer, Linux AppImage
```

**Edit source in `src/`.** Never hand-edit `forge`, `src/dashboard.html`, or `.forge/scripts/*` — they are generated artifacts.

## Development Workflow

After any source change:

```bash
python3 src/build_forge.py
./forge upgrade
```

Restart the dashboard:

```bash
screen -S forge-dashboard -X quit >/dev/null 2>&1 || true
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill
screen -dmS forge-dashboard ./forge dashboard 8080
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/
```

Expected response: `200`

## Desktop App

The Electron wrapper in `desktop/` packages `forge` as a native desktop app. CI builds run on every push to `main` and publish to GitHub Releases on version tags.

```bash
cd desktop
npm install
npm run build:mac    # macOS DMG (arm64 + x64)
npm run build:win    # Windows NSIS installer
npm run build:linux  # Linux AppImage
```

Authentication uses GitHub Device Flow. The OAuth App Client ID is configured via the setup wizard — never hardcoded.

### macOS — "Forge OS is damaged" fix

Downloaded builds are quarantined by Gatekeeper until the app is notarized. Run this once in Terminal after moving the app to Applications:

```bash
xattr -cr "/Applications/Forge OS.app"
```

Or right-click the app → **Open** → **Open Anyway**.

To enable full code signing and notarization, add these secrets to the GitHub repository:

| Secret | Description |
|---|---|
| `CSC_LINK` | Base64-encoded `.p12` Apple Developer certificate |
| `CSC_KEY_PASSWORD` | Certificate password |
| `APPLE_ID` | Apple ID email |
| `APPLE_ID_PASSWORD` | App-specific password from appleid.apple.com |
| `APPLE_TEAM_ID` | 10-character team ID from developer.apple.com |

## Dashboard Views

| View | Purpose |
|---|---|
| Projects | Create, open, archive, restore, and delete projects |
| Overview | Lifecycle command center — phase progress, stage matrix, gates |
| Input | Raw input Markdown files |
| Generate | Per-stage and full-pipeline generation |
| Review | File viewer, critique regeneration, gate status, version history |
| Build | Build-system generation and git/PR automation |
| Deploy | Environment config, CI/CD workflow generator, GitHub secrets status |
| Issues | Lightweight issue tracker |
| Settings | Product config, AI tool/model, git, environments |

## Security

- `.projects/` is gitignored — managed project state never commits.
- `.forge/project-state.json` may contain tokens from setup; treat as sensitive.
- Generated build artifacts may include `.env.example` and secret requirement docs — review before sharing.
- Secret values are never stored in source; only configured-secret metadata is persisted.
- API endpoints validate path inputs, enforce request body size limits, and restrict model IDs to known allowlists.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
