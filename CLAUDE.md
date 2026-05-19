# Forge OS — Developer Reference

> Version: 0.3.4. Python 3 stdlib runtime. Electron desktop app. Root orchestrator plus managed project runtimes.

## Product Overview

Forge OS is a documentation-first PDLC and build orchestration framework. It treats Markdown files and generated runtime state as the control plane for product planning, AI generation, review, build, and deployment.

Forge stands at the repository root as a top-level orchestrator and manages multiple generated projects under `.projects/`. The dashboard drives the entire lifecycle from a browser — or through the native Electron desktop app for macOS, Windows, and Linux.

Current lifecycle:

```text
Projects → Input → Generate → Review → Build → Deploy
```

The dashboard is project-first. A user starts at the Projects page, creates or selects a project, then operates the lifecycle for that project.

---

## Architecture: Source Layout

```text
src/build_forge.py                 compiler — assembles forge binary, hot-deploys runtime
src/runtime/forge_cli.py.tmpl      CLI template compiled into ./forge
src/runtime/server.py              dashboard API server (copied to .forge/scripts/server.py)
src/runtime/build_runner.py        build-system runner (copied to .forge/scripts/build_runner.py)
src/dashboard/index.html           dashboard HTML shell
src/dashboard/styles.css           dashboard CSS source
src/dashboard/scripts/*.js         dashboard JS source, assembled in order
src/dashboard/scripts.txt          dashboard script assembly order
src/dashboard/DESIGN.md            active dashboard design contract
src/dashboard.html                 generated compatibility snapshot (do not hand-edit)
forge                              built executable artifact (do not hand-edit)
desktop/                           Electron desktop app wrapper
desktop/main.js                    Electron main process
desktop/preload.js                 Electron preload script
desktop/assets/                    icons, entitlements.mac.plist
desktop/scripts/notarize.js        macOS notarization hook (no-op until Apple secrets set)
desktop/package.json               Electron build config (electron-builder)
docs/                              GitHub Pages product site (deployed from /docs branch)
.github/workflows/build-desktop.yml   CI — builds macOS DMG, Windows installer, Linux AppImage
```

**Rules:**
- Edit source in `src/`, `desktop/`, `docs/`.
- Never hand-edit `forge`, `src/dashboard.html`, or `.forge/scripts/*` — they are generated artifacts.
- After any source change: `python3 src/build_forge.py` then `./forge upgrade`.

---

## Build And Deploy Cycle

```bash
python3 src/build_forge.py
./forge upgrade
./forge --project "$PWD/.projects/task-flow" upgrade
./forge --project "$PWD/test-projects/saas-todo" upgrade
```

The build script hot-deploys `server.py` and `dashboard.html` to all live `.forge/scripts/` directories it can find, including `~/.forge/scripts/` (the Electron app's runtime location). This means a local rebuild immediately updates the Electron server without a manual upgrade — **but only if `~/.forge/scripts/` already exists** (created when Electron is first run).

Restart dashboard:

```bash
screen -S forge-dashboard -X quit >/dev/null 2>&1 || true
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill
screen -dmS forge-dashboard ./forge dashboard 8080
curl -sS -o /tmp/forge-dashboard.html -w '%{http_code} %{size_download}\n' http://127.0.0.1:8080/
```

Expected successful response: `200 <non-zero-size>`

---

## Validation Workflow

After any source change:

```bash
python3 src/build_forge.py
python3 -m py_compile src/build_forge.py src/runtime/server.py src/runtime/build_runner.py
./forge upgrade
./forge --project "$PWD/.projects/task-flow" upgrade
./forge --project "$PWD/test-projects/saas-todo" upgrade
screen -S forge-dashboard -X quit >/dev/null 2>&1 || true
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill
screen -dmS forge-dashboard ./forge dashboard 8080
curl -sS -o /tmp/forge-dashboard.html -w '%{http_code} %{size_download}\n' http://127.0.0.1:8080/
```

UI sanity pass must cover: Projects, Overview, Input, Generate, Review, Build, Deploy, Issues, Settings.

Known acceptable finding: absolute project paths are intentionally ellipsized in cards.

---

## CLI Reference

| Command | Description |
|---|---|
| `./forge version` | Print Forge version |
| `./forge init` | Initialize `.forge/` in current directory |
| `./forge --project <path> init` | Initialize a specific project |
| `./forge upgrade` | Update generated runtime files, preserve state |
| `./forge generate <stage>` | Generate one documentation stage |
| `./forge pipeline` | Run all documentation stages |
| `./forge dashboard [port]` | Start dashboard server (default: 8080) |
| `./forge dev [port]` | Build, init, and serve in one step |

`--project <path>` goes before the command.

---

## Supported AI Tools And Models

| Tool key | Label | Models |
|---|---|---|
| `gemini` | Gemini CLI | gemini-3-flash-preview, gemini-3-pro-preview, gemini-2.5-flash, gemini-2.5-pro, gemini-2.5-flash-lite |
| `claude` | Claude Code CLI | claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5-20251001 |
| `codex` | Codex CLI | o4-mini, o3, gpt-5.5, gpt-4.1, gpt-4.1-mini |
| `openai` | OpenAI API (direct) | gpt-5.5, gpt-4o, gpt-4o-mini, o3-mini |

Model IDs are validated at two layers:
1. `POST /api/settings` — server-side against `KNOWN_TOOLS`
2. `invoke_model()` in `forge_cli.py.tmpl` — runtime against `_ALLOWED_MODELS`

To add a new model: update `KNOWN_TOOLS` in `server.py` AND `_ALLOWED_MODELS` in `forge_cli.py.tmpl`, then rebuild.

---

## Project Name Resolution

When `project_name` is empty in `project-state.json`, `compute_full_state()` resolves in order:

1. Active project's `name` field from `.projects/index.json`
2. `os.path.basename(REPO_ROOT)` (directory name)

Additionally, `POST /api/projects/select` backfills `project_name` into the project's `project-state.json` from the index entry if missing — this is permanent and survives server restarts.

---

## Security Architecture

### Thread Safety
All shared state I/O is protected by module-level locks:
- `_state_lock` — `load_project_state` / `save_project_state`
- `_reviews_lock` — `load_reviews` / `save_reviews`
- `_index_lock` — `load_projects_index` / `save_projects_index`

Multiple background threads (generate, review, build, fix, distill, build-system) run concurrently. Without locks, concurrent writes to the same JSON file produce corruption.

### Path Traversal
All version API handlers validate:
- `ver_id` matches `re.fullmatch(r'\d{8}-\d{6}', ver_id)` — rejects any non-timestamp input
- Paths go through `os.path.normpath` + prefix check against `FORGE_DIR/versions/`

The `/api/file` and `/api/raw-input` GET handlers already had traversal guards.

### Model ID Allowlist
`POST /api/settings` rejects any `tool` not in `KNOWN_TOOLS` and any `model` not in that tool's list. The runtime `invoke_model()` in the compiled forge binary has its own `_ALLOWED_MODELS` check before constructing subprocess arguments.

### Request Size
`do_POST` and `do_DELETE` cap body reads at 4 MB via:
```python
_MAX_BODY = 4 * 1024 * 1024
content_length = min(int(self.headers.get("Content-Length", 0) or 0), _MAX_BODY)
```

### Electron IPC Validation
- `setup-git-config`: name ≤128 chars, email ≤256 chars, email format regex
- `setup-ssh-unlock`: type check + passphrase ≤1024 chars
- `setup-save`: must be plain object, payload ≤8 KB

### PAT Signal File
Server writes GitHub PAT to `~/.forge/_pat_signal` for Electron to pick up and store in `safeStorage`. The write uses `tempfile.mkstemp` + `os.replace` (atomic), `0o600` permissions applied before rename. Electron polls every 2 seconds, reads, deletes, stores in safeStorage.

### Structured Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [server] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("forge.server")
```
All bare `except Exception: pass` swallows replaced with typed exceptions (`OSError`, `json.JSONDecodeError`, `ValueError`) and `logger.debug/warning` calls.

---

## Desktop App (Electron)

### Requirements
- Node.js 22+
- `electron-builder` ^24.13.0
- `@electron/notarize` ^2.5.0

### Build Commands
```bash
cd desktop
npm install
npm run build:mac    # macOS DMG (arm64 + x64)
npm run build:win    # Windows NSIS installer
npm run build:linux  # Linux AppImage
```

### macOS Code Signing And Notarization

**`entitlements.mac.plist` is required.** The file lives at `desktop/assets/entitlements.mac.plist` and must exist or electron-builder produces a malformed bundle. Required entitlements for Electron:
- `com.apple.security.cs.allow-jit` — Electron renderer (V8 JIT)
- `com.apple.security.cs.allow-unsigned-executable-memory` — Node.js
- `com.apple.security.cs.disable-library-validation` — bundled native modules
- `com.apple.security.network.client` + `.server` — dashboard HTTP server
- File access entitlements for project directories

**Notarization**: `desktop/scripts/notarize.js` runs as `afterSign` hook. It is a no-op unless all three Apple secrets are present (`APPLE_ID`, `APPLE_ID_PASSWORD`, `APPLE_TEAM_ID`).

**To enable full signing and notarization**, add these GitHub repo secrets:

| Secret | Description |
|---|---|
| `CSC_LINK` | Base64-encoded `.p12` Apple Developer certificate |
| `CSC_KEY_PASSWORD` | Certificate password |
| `APPLE_ID` | Apple ID email |
| `APPLE_ID_PASSWORD` | App-specific password from appleid.apple.com |
| `APPLE_TEAM_ID` | 10-character team ID from developer.apple.com |

**User workaround (unsigned builds)**:
```bash
xattr -cr "/Applications/Forge OS.app"
```

### Windows icon.ico Requirement
`electron-builder` requires `icon.ico` to contain at least a 256×256 image. The file must be a proper multi-size ICO — Pillow's built-in ICO saver produces incorrect output. Use manual binary ICO construction:

```python
# ICO ICONDIR: reserved=0, type=1, count=N
# ICONDIRENTRY: width(0=256), height(0=256), colors=0, reserved=0, planes=1, bpp=32, size, offset
# Followed by raw PNG data for each size
```

Current file: 6 sizes (16/32/48/64/128/256 px), PNG-compressed, 32-bit RGBA.

---

## GitHub Actions CI/CD

Single workflow: `.github/workflows/build-desktop.yml`

- Triggers: push to `main`, version tags (`v*`), manual `workflow_dispatch`
- Matrix: `macos-latest`, `windows-latest`, `ubuntu-latest`
- Non-tag builds: upload 14-day artifacts
- Tag builds: publish to GitHub Releases (electron-updater reads `latest*.yml` from releases)

**GitHub Pages**: Configured to deploy from `/docs` branch directly — no Actions workflow needed or present. The old `static.yml` workflow was deleted to prevent duplicate deployments.

---

## Root And Project Directory Structure

Root-level source and orchestration:

```text
.forge/                      root runtime state for orchestrator dashboard
.projects/                   managed project workspace, gitignored
.projects/index.json         managed project registry
.projects/<slug>/.forge/     per-project generated runtime state
src/                         source for compiler, runtime, dashboard
test-projects/saas-todo/     validation project outside .projects
forge                        built executable
```

Inside a target `.forge/`:

```text
.forge/
|-- 00-raw-input/
|-- 00-context/
|-- 01-requirements/
|-- 02-design/
|-- 03-analysis/
|-- 04-architecture/
|-- 05-delivery/
|-- 06-engineering/
|-- 07-quality/
|-- 08-operations/
|-- 09-release/
|-- 10-marketing/
|-- 11-agents/
|-- 12-gates/
|-- 13-decisions/
|-- 14-assets/
|-- 15-build/
|-- runs/
|   |-- status.json
|   |-- build-system.json
|   |-- build-review.json
|   `-- run-log.md
|-- scripts/
|   |-- server.py
|   |-- dashboard.html
|   |-- run.py
|   |-- stage_runner.py
|   |-- validate_gates.py
|   `-- build_runner.py
|-- reviews.json
`-- project-state.json
```

---

## Dashboard Views

| View | Purpose |
|---|---|
| Projects | Create, open, archive, restore, delete managed projects |
| Overview | Lifecycle command center — phase strip, attention cards, stage matrix, stats, gates |
| Input | Raw input Markdown files |
| Generate | Per-stage and full-pipeline AI generation |
| Review | File viewer, critique regeneration, gate status, version history |
| Build | Build-system generation, git branch/commit/push/PR automation |
| Deploy | Environment config, CI/CD workflow generator, GitHub secrets status |
| Issues | Lightweight issue tracker |
| Settings | Product config, AI tool/model, git, environments, danger zone |

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serve dashboard |
| `GET` | `/api/state` | Full active project state |
| `GET` | `/api/file` | Raw generated file content |
| `GET/POST/DELETE` | `/api/raw-input` | Raw input file CRUD |
| `POST` | `/api/generate` | Generate one or all stages |
| `POST` | `/api/review` | Mark file reviewed or needs review |
| `POST` | `/api/fix` | Regenerate with critique |
| `POST` | `/api/gate` | Toggle gate state |
| `POST` | `/api/build` | Branch, commit, push, PR workflow |
| `GET/POST` | `/api/build-system` | Build subsystem status and generation |
| `GET` | `/api/build-file` | Generated build artifact content |
| `GET/POST` | `/api/build-review` | Pre-push review lifecycle |
| `GET/POST` | `/api/secrets` | Secret requirements and push/config status |
| `GET` | `/api/tools` | Supported AI tools and models |
| `GET` | `/api/versions` | File version list |
| `GET` | `/api/version` | File version content |
| `POST` | `/api/version/restore` | Restore previous file version |
| `GET` | `/api/pr-status` | Pull request status |
| `POST` | `/api/settings` | Save project settings (validates tool + model) |
| `POST` | `/api/issue` | Create/update issue |
| `POST` | `/api/reset` | Reset generated docs/reviews/gates |
| `GET/POST/DELETE` | `/api/projects` | Managed project lifecycle |
| `POST` | `/api/projects/select` | Select active project (backfills name) |
| `POST` | `/api/projects/archive` | Archive project |
| `POST` | `/api/projects/restore` | Restore project |

---

## State Files

```text
.forge/project-state.json       project settings, git, environments, builds, issues
.forge/reviews.json             per-file review status
.forge/runs/status.json         generation/processing status
.forge/runs/build-system.json   build subsystem step status
.forge/runs/build-review.json   pre-push review state
.projects/index.json            managed project registry and active selection
~/.forge/user.json              user role and department
~/.forge/_pat_signal            transient PAT handoff file (deleted after Electron reads it)
```

`project-state.json` is saved with `0o600` permissions. Git PAT is stripped before persistence (stored only in Electron safeStorage).

---

## Phase Computation

Lifecycle phase is computed from file/build state, not stored as the source of truth.

| Phase | Condition |
|---|---|
| `input` | No raw input files or all stage files are empty |
| `generate` | Raw inputs exist but generated docs are below threshold |
| `review` | Generated docs exist but not all are reviewed |
| `build` | Generated docs are reviewed and no build exists |
| `deploy` | At least one build exists |

---

## Gate System

Gate files live in `.forge/12-gates/<gate>.md`. Review status lives in `.forge/reviews.json`. A gate passes only when every generated non-empty file mapped to that gate is reviewed.

```text
context-gate      -> 00-context
prd-gate          -> 01-requirements
design-gate       -> 02-design
architecture-gate -> 04-architecture
engineering-gate  -> 06-engineering
qa-gate           -> 07-quality
release-gate      -> 09-release
marketing-gate    -> 10-marketing
```

---

## Design System

Direction: Revolut-inspired. Sources of truth:
- `src/dashboard/DESIGN.md`
- `src/dashboard/styles.css`

Active tokens:
- `--primary: #4ADE80` — primary green
- `--accent: #494fdf` — cobalt violet (scarce use)
- `--purple: #8B5CF6`
- Canvas: true black `#060D06`
- Operational surfaces: white

Component sizing rules:
- Buttons: base 36px, sm 30px, xs 26px min-height
- Inputs: 40px min-height (38px compact)
- `.view-title`: 18px — NOT 40–64px (that is marketing-hero scale)
- Cards: 20px border-radius
- No decorative shadows as core depth language

**Critical adaptation rule**: Marketing design contracts cannot be applied literally to a dense production dashboard. Adapt tokens and component rules for control density and readability.

---

## Failure Log

### Stale Generated Dashboard
- Symptom: browser showed old UI after source changes
- Cause: source changed but `src/dashboard.html` and `.forge/scripts/dashboard.html` not regenerated
- Fix: `python3 src/build_forge.py` → `./forge upgrade` → project upgrades

### Server Not Reachable
- Symptom: "site cannot be reached"
- Causes: server not running, wrong project target, stale port listener, runtime not upgraded
- Fix: kill port, restart with screen, verify with curl

### Blank Page After Design Experiment
- Symptom: HTTP 200 but browser renders blank
- Cause: unstable generated output + stale browser tab
- Fix: revert source, rebuild, upgrade, restart, fresh tab

### Review Panel Overflow
- Symptom: "Regenerate with critique" clipped in Review panel
- Cause: fixed-width panel + global `white-space: nowrap` on buttons
- Fix: widen panel, constrain button typography, ellipsize filenames

### Marketing Design Over-Application
- Symptom: pasted design MD produced poor dashboard usability, hero-scale typography in dense controls
- Cause: marketing design systems assume sparse landing content
- Fix: preserve design intent through tokens, adapt for dashboard density

### icon.ico Too Small (Windows CI Failure)
- Symptom: `image desktop/assets/icon.ico must be at least 256x256`
- Cause: ICO contained only 16×16 image (400 bytes)
- Fix: rebuilt as 6-image ICO using manual binary construction — **do not use `PIL.Image.save(format="ICO")` for multi-size; use `struct.pack` ICO construction directly**

### Duplicate GitHub Pages Deployment
- Symptom: two "deployments" on every push
- Cause: `static.yml` Actions workflow + branch-based Pages both active
- Fix: deleted `static.yml`. Branch-based Pages from `/docs` requires no workflow.

### Unnamed Project / My Project In Dashboard
- Root cause 1: empty `project_name` in `project-state.json`
- Root cause 2: hot-deploy didn't include `~/.forge/scripts/` so Electron server didn't get the fix
- Fix: 3-level fallback in `compute_full_state()`, added `~/.forge/scripts/` to hot-deploy scan, added name backfill on `select`

### New Model Not Visible In Tool Selector
- Cause: model added to one tool in `KNOWN_TOOLS` but not another, or not added to `_ALLOWED_MODELS` in template
- Fix: always update BOTH `server.py` `KNOWN_TOOLS` AND `forge_cli.py.tmpl` `_ALLOWED_MODELS` for every tool the model applies to

### macOS "Forge OS Is Damaged And Can't Be Opened"
- Root cause: `entitlements.mac.plist` referenced in `package.json` but file didn't exist → malformed bundle
- Secondary cause: unsigned/unnotarized app quarantined by macOS Gatekeeper
- Fix: created `entitlements.mac.plist`, added `@electron/notarize`, created notarize hook, wired Apple secrets to CI
- User workaround: `xattr -cr "/Applications/Forge OS.app"`
- Permanent fix: configure Apple Developer cert and notarization secrets in GitHub repo

### Git Worktree Config Compatibility
- Symptom: `core.repositoryformatversion does not support extension: worktreeconfig`
- Takeaway: prefer operating in main repo; worktrees may expose Git config compatibility issues

---

## Success Log

- Modular source layout (compiler + runtime + dashboard sources); single built `forge` artifact
- Project-first dashboard with full create/select/archive/restore/delete lifecycle
- `.projects/` gitignored
- Thread-safe state I/O with three module-level locks
- Security hardening: path traversal guards, model allowlist, IPC validation, 4 MB request cap
- Structured logging throughout `server.py`; typed exception handling replaces bare `except: pass`
- Hot-deploy includes `~/.forge/scripts/` for Electron users
- Overview command center: phase strip, attention cards, stage matrix, stats sidebar
- Deploy section: env cards, CI/CD workflow generator, secrets status
- Design system cleanup: tokens normalized, hero typography scaled for dashboard density
- GPT-5.5 in both Codex and OpenAI tool selectors with allowlist enforcement
- macOS: `entitlements.mac.plist` created, notarization hook ready for Apple secrets
- Windows: proper 6-size ICO (16/32/48/64/128/256 px) via binary construction
- GitHub Pages: single clean deployment from `/docs` branch, no redundant workflow
- README, LICENSE, CLAUDE.md, AGENT.md all production-grade

---

## Security And Hygiene

Non-negotiable rules:
- Do not commit `.projects/` runtime state
- Do not expose `project-state.json` without checking for tokens
- Do not paste tokens, repo credentials, AI keys, or environment values into docs, logs, or chat
- Generated build artifacts may include `.env.example` — review before sharing
- `configured-secret` metadata only — never plaintext secret values in state
- When adding a new AI model, update BOTH `KNOWN_TOOLS` in `server.py` AND `_ALLOWED_MODELS` in `forge_cli.py.tmpl`, then rebuild

---

## Updating This File

Update whenever:
- New command added
- New API endpoint added
- New state file introduced
- New AI model or tool added
- Source layout changes
- New security control added
- New failure pattern discovered
- Any desktop/CI change that affects distribution

Runtime is the source of truth. If this file disagrees with actual `forge` behavior, update this file.
