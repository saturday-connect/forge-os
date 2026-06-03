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
src/build_constants.py             all build-time string constants (paths, markers, codegen prefixes)
src/runtime/forge_cli.py.tmpl      CLI template compiled into ./forge
src/runtime/server.py              dashboard API server (copied to .forge/scripts/server.py)
src/runtime/build_runner.py        build-system runner (copied to .forge/scripts/build_runner.py)
src/runtime/batch_runner.py        batch doc generator — whole stage in one AI call (copied to .forge/scripts/batch_runner.py)
src/runtime/constants.py           runtime constants shared by server, build_runner, and template
src/data/tools.json                AI tool + model definitions (source of truth for KNOWN_TOOLS)
src/data/build_steps.json          build step definitions and execution order
src/data/stages.json               stage → output file mappings
src/data/stage_pipeline.json       stage agent, gate, input, and directory config
src/data/agents/                   agent prompt Markdown files (one per agent)
src/data/gates/                    gate prompt Markdown files (one per gate)
src/data/prompts/agent_prompt.md   AI generation prompt template
src/data/prompts/distill_prompt.md distillation prompt template
src/dashboard/index.html           dashboard HTML shell
src/dashboard/styles.css           dashboard CSS source
src/dashboard/scripts/*.js         dashboard JS source, assembled in order
src/dashboard/DESIGN.md            active dashboard design contract
src/dashboard.html                 generated compatibility snapshot (do not hand-edit)
forge                              built executable artifact (do not hand-edit)
desktop/                           Electron desktop app wrapper
desktop/main.js                    Electron main process
desktop/preload.js                 Electron preload script
desktop/auth.js                    OAuth / GitHub auth flow
desktop/github.js                  GitHub API helpers
desktop/org.js                     org context helpers
desktop/auth-preload.js            auth window preload
desktop/setup-preload.js           setup window preload
desktop/auth-window.html           OAuth window shell
desktop/setup-window.html          setup/onboarding window shell
desktop/assets/                    icons, entitlements.mac.plist
desktop/scripts/notarize.js        macOS notarization hook (no-op until Apple secrets set)
desktop/scripts/pkg/               postinstall scripts for macOS .pkg installer
desktop/package.json               Electron build config (electron-builder)
docs/                              GitHub Pages product site (deployed from /docs branch)
.github/workflows/build-desktop.yml   CI — builds macOS DMG/PKG, Windows installer, Linux AppImage
```

**Rules:**
- Edit source in `src/`, `desktop/`, `docs/`.
- Never hand-edit `forge`, `src/dashboard.html`, or `.forge/scripts/*` — they are generated artifacts.
- After any source change: `python3 src/build_forge.py` then `./forge upgrade`.
- Never name the Electron wrapper directory `electron/` — Node.js treats it as a reserved package name.

---

## Build System Architecture

`build_forge.py` is a pure compiler (~260 lines). It:
1. Reads all data from `src/data/*.json`, `src/data/agents/*.md`, `src/data/gates/*.md`
2. Reads runtime source files from `src/runtime/`
3. Injects generated Python code blocks into `server.py`, `build_runner.py`, and `batch_runner.py` via placeholder tokens
4. Renders `forge_cli.py.tmpl` via `str.format()` with all injected code blocks
5. Writes the rendered output to `./forge`
6. Hot-deploys `server.py`, `dashboard.html`, `constants.py`, `build_runner.py`, and `batch_runner.py` to all live `.forge/scripts/` directories

All build-time string constants (file paths, JSON keys, codegen prefixes, placeholder sentinels, log messages, glob patterns) live in `src/build_constants.py`. There are no magic strings in `build_forge.py`.

### Placeholder Injection Pattern

Runtime source files contain sentinel comments that are replaced during build:

```python
# server.py
KNOWN_TOOLS = {}  # __FORGE_KNOWN_TOOLS__

# build_runner.py
STEPS = {}  # __FORGE_BUILD_STEPS__

# batch_runner.py
STAGE_INPUTS = {}  # __FORGE_STAGE_INPUTS__
STAGE_AGENTS = {}  # __FORGE_STAGE_AGENTS__
```

These are replaced with generated Python dicts before the content is embedded into `forge`.

### Template Format() Pattern

`forge_cli.py.tmpl` uses `str.format()` for code injection. Any literal Python braces inside the template that should survive injection unchanged must be doubled: `{{agent}}`, `{{gate}}`. Injected values do not need escaping.

### Batch Generation (`FORGE_STAGE_BATCH`)

The per-file generator (`run.py`) re-sends the full upstream context for every file in a stage, so an N-file stage pays for that context N times. `batch_runner.py` is an opt-in alternative that sends the shared context **once** and asks the model to emit every file of the stage in a single response (`=== path === ` blocks — the same pattern the code generator uses).

- **Enable**: **Settings → AI Runtime → "Batch generation"** toggle (persisted as `stage_batch` in `project-state.json`; the server sets `FORGE_STAGE_BATCH=1` on the generation subprocess). Or, for CLI use, set `FORGE_STAGE_BATCH=1` in the environment directly. The saved toggle is **authoritative** for dashboard-launched generation — when off, the server clears any inherited env so OFF always wins. Opt-in; default off.
- **Hook**: `stage_runner.py` tries `batch_runner.py` first when `FORGE_STAGE_BATCH=1` and the stage has ≥2 pending files. Exit `0` = all files written (or all cached) → stage done. Any non-zero exit (`3` = deferred/incomplete/AI-failure, `2` = bad args) → falls through to the proven per-file loop. The batch path can never regress generation.
- **Atomicity**: `batch_runner` writes files only when the parsed response contains *every* requested file; a partial/garbled batch writes nothing and defers.
- **Reuse**: `batch_runner` imports `build_runner` and reuses its `invoke_ai`, `parse_files`, `_est_tokens`, and `_strip_wrapping_code_fence` — no duplication of AI-invocation logic.
- **Cache caveat**: both paths share `runs/generate-cache.json`, but the input-hash covers the prompt, which differs between batch (multi-file) and per-file. Toggling `FORGE_STAGE_BATCH` invalidates the cache for affected files once (one redundant regen), then re-converges. Not a correctness issue — outputs are always written correctly.
- **Injection**: `STAGE_INPUTS` / `STAGE_AGENTS` are injected at build time from `src/data/stage_pipeline.json` (the same source `run.py` uses), so no manual edits.

---

## Build And Deploy Cycle

```bash
python3 src/build_forge.py
./forge upgrade
./forge --project "$PWD/.projects/task-flow" upgrade
./forge --project "$PWD/test-projects/saas-todo" upgrade
```

The build script hot-deploys `server.py`, `dashboard.html`, and `constants.py` to all live `.forge/scripts/` directories it can find, including `~/.forge/scripts/` (the Electron app's runtime location). This means a local rebuild immediately updates the Electron server without a manual upgrade — **but only if `~/.forge/scripts/` already exists** (created when Electron is first run).

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
python3 -m py_compile src/build_forge.py src/runtime/server.py src/runtime/build_runner.py src/runtime/batch_runner.py
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
1. `POST /api/settings` — server-side against `KNOWN_TOOLS` (generated from `src/data/tools.json`)
2. `invoke_model()` in the compiled `forge` binary — runtime against `_ALLOWED_MODELS` (also generated from `src/data/tools.json`)

### Adding A New AI Model

1. Edit `src/data/tools.json` — add the model ID to the relevant tool's `models` array
2. Rebuild: `python3 src/build_forge.py`
3. Upgrade: `./forge upgrade`
4. Restart dashboard

Both the server-side `KNOWN_TOOLS` and the runtime `_ALLOWED_MODELS` are generated from the same `tools.json` source during build. No manual edits to `server.py` or `forge_cli.py.tmpl` are needed.

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
`POST /api/settings` rejects any `tool` not in `KNOWN_TOOLS` and any `model` not in that tool's list. The runtime `invoke_model()` in the compiled forge binary has its own `_ALLOWED_MODELS` check before constructing subprocess arguments. Both are generated from `src/data/tools.json` at build time.

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

The app lives in `desktop/` — **not** `electron/`. The `electron/` name conflicts with Node.js package resolution and causes `not a file` build errors in electron-builder.

### Requirements
- Node.js 22+
- `electron-builder` ^24.13.0
- `@electron/notarize` ^2.5.0

### Build Commands
```bash
cd desktop
npm install
npm run build:mac    # macOS DMG + PKG + ZIP (arm64 + x64, sequential)
npm run build:win    # Windows NSIS installer
npm run build:linux  # Linux AppImage
```

### Asar Bundle Completeness
`desktop/package.json` uses an explicit `files` allowlist. Every module required at runtime must be listed:
```json
"files": [
  "main.js", "preload.js", "auth.js", "github.js", "org.js",
  "auth-preload.js", "setup-preload.js", "auth-window.html", "setup-window.html",
  "assets/**/*"
]
```
Missing files are silently excluded from the asar bundle and crash the app at runtime with `Cannot find module`.

### macOS Targets
Three targets are built: `dmg`, `pkg`, `zip`. The `pkg` installer runs a postinstall script at `desktop/scripts/pkg/postinstall` that automatically executes `xattr -cr` to clear the quarantine attribute — this means users who install via `.pkg` get a working app without any manual steps.

macOS arch targets (arm64 + x64) are built **sequentially** in CI to avoid pkg packaging race conditions.

### macOS Code Signing And Notarization

**`entitlements.mac.plist` is required.** The file lives at `desktop/assets/entitlements.mac.plist` and must exist or electron-builder produces a malformed bundle. Required entitlements for Electron:
- `com.apple.security.cs.allow-jit` — Electron renderer (V8 JIT)
- `com.apple.security.cs.allow-unsigned-executable-memory` — Node.js
- `com.apple.security.cs.disable-library-validation` — bundled native modules
- `com.apple.security.network.client` + `.server` — dashboard HTTP server
- File access entitlements for project directories

**Notarization**: `desktop/scripts/notarize.js` runs as `afterSign` hook. It is a no-op unless all three Apple secrets are present (`APPLE_ID`, `APPLE_ID_PASSWORD`, `APPLE_TEAM_ID`). The hook also checks for `CSC_LINK` being a non-empty string before attempting to notarize.

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
Or install via `.pkg` — the postinstall script handles this automatically.

### Windows icon.ico Requirement
`electron-builder` requires `icon.ico` to contain at least a 256×256 image. The file must be a proper multi-size ICO — Pillow's built-in ICO saver produces incorrect output. Use manual binary ICO construction:

```python
# ICO ICONDIR: reserved=0, type=1, count=N
# ICONDIRENTRY: width(0=256), height(0=256), colors=0, reserved=0, planes=1, bpp=32, size, offset
# Followed by raw PNG data for each size
```

Current file: 6 sizes (16/32/48/64/128/256 px), PNG-compressed, 32-bit RGBA.

### CI: Empty CSC_LINK Guard
When `CSC_LINK` is not set as a GitHub secret, the environment variable is an empty string. electron-builder treats this as a signing credential and crashes. The CI workflow sets `CSC_IDENTITY_AUTO_DISCOVERY: false` and the notarize hook checks `process.env.CSC_LINK` before invoking notarization.

---

## GitHub Actions CI/CD

Single workflow: `.github/workflows/build-desktop.yml`

- Triggers: push to `main`, version tags (`v*`), manual `workflow_dispatch`
- Matrix: `macos-latest`, `windows-latest`, `ubuntu-latest`
- macOS: builds arm64 and x64 **sequentially** (not in parallel matrix) to avoid pkg race condition
- Non-tag builds: upload 14-day artifacts
- Tag builds: publish to GitHub Releases (electron-updater reads `latest*.yml` from releases)
- Working directory: `desktop/` (not `electron/`)

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
|   |-- constants.py
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
| Knowledge | Knowledge base export (per-project docs → KB repo), AI distillation to global patterns/decisions/learnings, sync ref management |
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
| `GET/POST` | `/api/build-system` | Build subsystem status and generation; POST `step` accepts `all`, `failed` (retry only errored steps), or a single step; also accepts `action: "clear_cache"` (wipe local cache) and `action: "sync_cache"` (union-sync the cache with the configured git repo) |
| `GET` | `/api/build-file` | Generated build artifact content |
| `GET/POST` | `/api/build-review` | Pre-push review lifecycle; also accepts `action: "human_review"` with `{verdict, notes}` to record the human reviewer verdict before pushing |
| `GET/POST` | `/api/secrets` | Secret requirements and push/config status |
| `GET` | `/api/tools` | Supported AI tools and models |
| `GET` | `/api/versions` | File version list |
| `GET` | `/api/version` | File version content |
| `POST` | `/api/version/restore` | Restore previous file version |
| `GET` | `/api/pr-status` | Pull request status |
| `POST` | `/api/settings` | Save project settings (validates tool + model) |
| `POST` | `/api/issue` | Create/update issue |
| `POST` | `/api/reset` | Reset generated docs/reviews/gates |
| `GET/POST` | `/api/knowledge` | Knowledge base config, status, reviewed docs |
| `POST` | `/api/knowledge/configure` | Save KB repo config (owner, repo, branch) |
| `POST` | `/api/knowledge/export` | Export reviewed docs to KB repo as PR |
| `POST` | `/api/knowledge/distill` | AI distillation pass → global KB dirs as draft PR |
| `POST` | `/api/knowledge/sync` | Pin KB repo ref for generation context |
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
.forge/runs/generate-cache.json  per-file gen cache (input hash, tokens); shared by run.py + batch_runner
.forge/runs/build-system.json   build subsystem step status
.forge/runs/build-review.json   pre-push review state
.forge/runs/kb-state.json           knowledge base pipeline operation state
.forge/runs/consistency-check.json  last consistency check result (downstream affected docs)
.projects/index.json            managed project registry and active selection
~/.forge/user.json              user role and department
~/.forge/_pat_signal            transient PAT handoff file (deleted after Electron reads it)
~/.forge/build-cache/<hash>/    cross-run build cache: content-addressed step output + _cache_meta.json (LRU-capped)
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
- Old cause: model added to `server.py` KNOWN_TOOLS but not to `forge_cli.py.tmpl` `_ALLOWED_MODELS` (or vice versa)
- Current state: both are generated from `src/data/tools.json` — editing one source fixes both
- If a model is invisible: verify it is in `tools.json`, rebuild, upgrade

### macOS "Forge OS Is Damaged And Can't Be Opened"
- Root cause: `entitlements.mac.plist` referenced in `package.json` but file didn't exist → malformed bundle
- Secondary cause: unsigned/unnotarized app quarantined by macOS Gatekeeper
- Fix: created `entitlements.mac.plist`, added `@electron/notarize`, created notarize hook, wired Apple secrets to CI
- User workaround: `xattr -cr "/Applications/Forge OS.app"` or install via `.pkg`
- Permanent fix: configure Apple Developer cert and notarization secrets in GitHub repo

### Git Worktree Config Compatibility
- Symptom: `core.repositoryformatversion does not support extension: worktreeconfig`
- Takeaway: prefer operating in main repo; worktrees may expose Git config compatibility issues

### Template Extraction Escape Bug
- Symptom: `SyntaxError: unexpected character after line continuation character` in generated `forge` binary
- Cause: raw file slicing preserves literal source bytes including escaped quotes (`r\"\"\"`) instead of decoded values (`r"""`)
- Fix: use `ast.literal_eval()` to decode Python string escapes when extracting embedded string content from source files; raw slicing is only safe for content without Python escape sequences

### `{agent}` KeyError In Template Format()
- Symptom: `KeyError: 'agent'` during build
- Cause: `forge_cli.py.tmpl` contained `f"11-agents/{agent}.md"` — the `{agent}` was consumed by `TEMPLATE.format()` before the f-string could evaluate it
- Fix: escape any literal Python braces in the template file to `{{agent}}`, `{{gate}}`, etc. Only `{PLACEHOLDER_NAME}` constructs (uppercase, no spaces) are consumed by `format()`

### Electron `not a file` CI Error
- Symptom: `⨯ /path/to/forge-os/electron not a file` in CI build
- Cause: directory named `electron/` conflicts with Node.js package resolution — electron-builder resolves it as the `electron` npm package path rather than a directory
- Fix: renamed to `desktop/`. Any wrapper directory name works except `electron/`

### Missing Asar Modules (Cannot Find Module At Runtime)
- Symptom: Electron app launches then immediately crashes with `Error: Cannot find module './auth'`
- Cause: `desktop/package.json` `files` array is an explicit allowlist — any module not listed is silently excluded from the asar bundle
- Fix: list every required module explicitly: `auth.js`, `github.js`, `org.js`, `auth-preload.js`, `setup-preload.js`, `auth-window.html`, `setup-window.html`

### Empty CSC_LINK Electron-Builder Crash
- Symptom: CI build crashes during signing step with certificate error
- Cause: when `CSC_LINK` GitHub secret is not configured, the env var is an empty string — electron-builder treats it as an invalid certificate and aborts
- Fix: set `CSC_IDENTITY_AUTO_DISCOVERY: false` in the CI workflow env; check `process.env.CSC_LINK` is non-empty in the notarize hook before proceeding

### "Failed To Create Project" In Packaged Electron App
- Symptom: project creation silently fails with "Failed to create project" toast; no project appears
- Cause: `server.py` invoked `forge init` as `[forge_script, ...]`, relying on the `#!/usr/bin/env python3` shebang. Inside a packaged `.app`, the `forge` resource may not be executable and the shebang's `env` lookup may fail inside the app sandbox
- Fix: prepend `sys.executable` to all `forge` subprocess invocations in `server.py`: `[sys.executable, forge_script, ...]`. The server is already running under the correct Python — use it directly
- Pattern: the distill handler already did this correctly for `run.py`; apply the same to every forge subprocess call

### macOS Arch Build Race Condition (pkg)
- Symptom: arm64 and x64 pkg builds intermittently fail or corrupt each other in CI
- Cause: running both arch targets in a parallel matrix shares the same pkg staging directories
- Fix: build macOS arch targets sequentially (two sequential CI steps, not a matrix)

### Edit Tool Duplicate Match On Insertion
- Symptom: Edit tool reports "not unique in the file" when inserting near a commonly repeated string
- Cause: the old_string context was too short and matched multiple locations
- Fix: always include a longer unique surrounding context (preceding/following unique lines) when inserting into dense files

### Consistency Check After Fix — AI Call Failure Swallowed
- Design decision: `_run_consistency_check()` is wrapped in try/except; a fix always completes even if the downstream AI call fails
- This is intentional — consistency check is advisory, not blocking

---

## Success Log

- Modular source layout (compiler + runtime + dashboard sources); single built `forge` artifact
- `build_forge.py` reduced to ~260 lines — pure compiler with zero magic strings
- `build_constants.py` centralizes all build-time constants; no drift between build and codegen
- `forge_cli.py.tmpl` is the actual CLI template — fully wired, no dead file
- Data-driven `AGENT_CONTENT` and `GATE_CONTENT` dicts replace 24-branch if/elif dispatch chains
- All AI tool and model config lives in `src/data/tools.json` — single edit updates both server and runtime
- All pipeline config lives in `src/data/stage_pipeline.json` — agent, gate, inputs, directories
- AI prompt templates extracted to `src/data/prompts/` and injected at build time
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
- macOS: `.pkg` installer with postinstall script auto-clears quarantine — zero manual steps for users
- Windows: proper 6-size ICO (16/32/48/64/128/256 px) via binary construction
- GitHub Pages: single clean deployment from `/docs` branch, no redundant workflow
- Electron wrapper renamed to `desktop/` — resolves Node.js module name conflict permanently
- All Electron modules listed in `files` array — no silent asar exclusions
- macOS CI: sequential arch builds — no pkg race condition
- Beta release infrastructure: versioned beta tags, asset-overwrite support, download page auto-detection
- README, LICENSE, CLAUDE.md, AGENT.md all production-grade
- CLI warning strip: `_strip_cli_warnings()` filters diagnostic noise from AI subprocess stdout before persisting doc content
- Knowledge Base pipeline: export reviewed docs to separate git repo as PR, AI distillation to global patterns/decisions/learnings, sync ref for generation context
- Consistency check after fix: one AI call checks all downstream reviewed docs for drift after a critique fix; marks affected docs as `needs_review`
- Manual code review: diff viewer + human verdict (approve/request_changes) with audit trail in build-review.json before push
- `action` dispatch pattern in POST handlers: single endpoint per resource, multiple action values — avoids URL proliferation
- CI auto-release: `check-version` job reads `desktop/package.json` version, creates git tag + GitHub Release if version not found — push to main is sufficient, no manual tag needed
- Batch stage generation (`FORGE_STAGE_BATCH=1`): `batch_runner.py` emits a whole stage's docs in one AI call (shared context sent once, not N times), wired into `stage_runner` as a fast-path with all-or-nothing writes and automatic fallback to the per-file loop on any non-zero exit — validated hermetically (stubbed AI) for the success, partial-output, defer, and bad-args paths
- Batch generation Settings toggle: Settings -> AI Runtime -> "Batch generation" persists `stage_batch` to `project-state.json`; the server injects `FORGE_STAGE_BATCH=1` into the generation subprocess env (authoritative over ambient env — OFF clears any inherited value), so the per-file vs. batch path is a UI choice, not just an env flag
- Build concurrency control (Phase 1): Settings -> AI Runtime -> "Max parallel build steps" persists `build_concurrency` (1-4, clamped) to `project-state.json`; the parallel DAG scheduler reads it for `ThreadPoolExecutor(max_workers)`, authoritative over ambient `FORGE_BUILD_CONCURRENCY` — exposes the existing build-concurrency cap as a UI knob for rate-limit management
- Retry failed build steps (Phase 1): `POST /api/build-system {step:"failed"}` re-runs only `error`-status steps whose deps are complete, seeding the DAG scheduler's done-set with already-complete steps so dependents are runnable without re-running them; a "Retry failed" button appears in the Build view when any step errored — re-run only what broke, not the whole build
- Build profiles (Phase 2): `build_profile` (fast/balanced/thorough/custom) bundles the three real build knobs — per-step model tier, scheduler concurrency, post-build validation. Server-resolved at build + preview time via `_resolve_build_profile` / `_profile_step_model` / `_profile_concurrency` (server.py): fast = mechanical steps (infra, tests) -> tool `fast_model`, concurrency 4; balanced = global model, concurrency 2; thorough = global model, concurrency 1, `FORGE_VALIDATE_BUILD=1`; custom = the individual `build_step_models` + `build_concurrency` settings (so existing power-user configs are preserved — absent `build_profile` resolves to `custom` when overrides exist, else `balanced`). Selector lives in the Build view header + Settings -> AI Runtime
- Persistent build cache (Phase 3/D1): content-addressed store at `~/.forge/build-cache/<input_hash>/` (build_runner.py `_build_cache_save` / `_build_cache_restore` / `_build_cache_gc`). Unlike the in-place skip-unchanged check, this survives a `15-build` clean or a fresh checkout — restore hook fires after an in-place miss, save hook after a successful non-degenerate build. Backend's restore re-establishes the shared `api-contract.md` downstream steps read. LRU-capped (`_BUILD_CACHE_MAX_ENTRIES`); disable with `FORGE_BUILD_CACHE=0`; `FORGE_FORCE_REBUILD=1` bypasses + overwrites. Cleared via `build_runner.py --clear-cache` or `POST /api/build-system {action:"clear_cache"}` (Build view "Clear cache" button). Validated hermetically: generate->store->clean->restore (0 AI calls, `cached:true`), and clear->regenerate
- Remote build cache sync (Phase 3/D2): `build_cache_repo` ({url, branch} in `project-state.json`) optionally shares the cross-run cache across machines/CI. `_run_sync_build_cache` (server.py) union-syncs the local store with the git repo — entries are immutable (keyed by input_hash) so the merge is conflict-free: pull = copy remote entries missing locally, push = copy local entries missing remotely, then commit+push (rebase+retry once on rejection). Reuses the KB git plumbing (PAT auth via `x-access-token`, `_cache_auth_url` injects the token for github https and passes `file://`/ssh through). Advisory — invoked explicitly via `POST /api/build-system {action:"sync_cache"}` (Build view "Sync cache" button, shown when a repo is configured), never inline in a build. The cache dir name is centralized in `constants.py` (`BUILD_CACHE_DIRNAME`) so build_runner + server agree. Validated against a local bare repo: A push -> B pull -> B push -> A pull, bidirectional, no GitHub needed

---

## Security And Hygiene

Non-negotiable rules:
- Do not commit `.projects/` runtime state
- Do not expose `project-state.json` without checking for tokens
- Do not paste tokens, repo credentials, AI keys, or environment values into docs, logs, or chat
- Generated build artifacts may include `.env.example` — review before sharing
- `configured-secret` metadata only — never plaintext secret values in state
- When adding a new AI model, edit `src/data/tools.json` then rebuild — no manual edits to `server.py` or `forge_cli.py.tmpl`

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
