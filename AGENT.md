# AGENT.md — Forge OS Handover Guide

## Mental Model

This repository is the Forge root orchestrator. Three layers:

1. **Root orchestrator** — source code, compiler, dashboard source, built `forge` executable, Electron desktop app
2. **Managed projects** — generated/controlled projects under `.projects/<project-slug>/`
3. **Validation projects** — external test beds such as `test-projects/saas-todo/`

The root `forge` executable is the user-facing CLI artifact. Source is modular — never edit generated artifacts directly.

---

## Source Of Truth Rules

Priority order (highest wins):

1. Current source under `src/`, `desktop/`
2. Built `./forge` behavior
3. Generated runtime under `.forge/scripts/*` and `<project>/.forge/scripts/*`
4. Actual project state under `.forge/` and `.projects/index.json`
5. This documentation

Do not manually edit generated runtime files. The next `upgrade` overwrites them.

---

## Build System Architecture

`src/build_forge.py` is a pure compiler (~260 lines). All build-time string constants live in `src/build_constants.py`. All AI tool/model config lives in `src/data/tools.json`. All pipeline config (stage agents, gates, inputs, directories) lives in `src/data/stage_pipeline.json`.

The compiler:
1. Reads data from `src/data/*.json`, `src/data/agents/*.md`, `src/data/gates/*.md`, `src/data/prompts/`
2. Injects generated Python dicts into `server.py` and `build_runner.py` via placeholder sentinels
3. Renders `src/runtime/forge_cli.py.tmpl` via `str.format()` with all injected blocks
4. Writes `./forge`
5. Hot-deploys `server.py`, `dashboard.html`, `constants.py` to all live `.forge/scripts/` directories

---

## Command Playbook

All commands run from repo root unless stated.

### Standard rebuild + upgrade cycle
```bash
python3 src/build_forge.py
./forge upgrade
./forge --project "$PWD/.projects/task-flow" upgrade
./forge --project "$PWD/test-projects/saas-todo" upgrade
```

### Restart dashboard
```bash
screen -S forge-dashboard -X quit >/dev/null 2>&1 || true
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill
screen -dmS forge-dashboard ./forge dashboard 8080
curl -sS -o /tmp/forge-dashboard.html -w '%{http_code} %{size_download}\n' http://127.0.0.1:8080/
```
Expected: `200 <non-zero-size>`

### Syntax check before committing
```bash
python3 -m py_compile src/build_forge.py src/runtime/server.py src/runtime/build_runner.py
```

### Verify binary
```bash
./forge version
./forge
```

### Run dashboard from specific project
```bash
./forge --project "$PWD/.projects/task-flow" dashboard 8080
```

### Commit and push pattern
```bash
git add <files>
git commit -m "type(scope): description

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin main
```

---

## Hot-Deploy Behaviour

`python3 src/build_forge.py` copies `server.py`, `dashboard.html`, and `constants.py` to ALL live `.forge/scripts/` directories it finds, including:
- `<repo_root>/.forge/scripts/`
- `<repo_root>/.projects/*/.forge/scripts/`
- `<repo_root>/test-projects/*/.forge/scripts/`
- `<parent_dir>/*/.forge/scripts/`
- `~/.forge/scripts/` ← Electron app's runtime location

**Critical**: `~/.forge/scripts/` only gets updated if it already exists (Electron must have been run at least once). If a server-side fix is not reaching the Electron app, verify this directory exists.

---

## Adding A New AI Model

1. Edit `src/data/tools.json` — add the model ID to the relevant tool's `models` array
2. Rebuild: `python3 src/build_forge.py`
3. Upgrade: `./forge upgrade`
4. Restart dashboard

Both `KNOWN_TOOLS` (server) and `_ALLOWED_MODELS` (runtime) are generated from the same `tools.json` source. No manual edits to `server.py` or `forge_cli.py.tmpl` are needed.

---

## Project Workspace Model

State:
- `.projects/index.json` — project registry, active project ID, archive status
- `.projects/<slug>/.forge/` — per-project runtime state

Project lifecycle APIs:
- `GET /api/projects` — list
- `POST /api/projects` — create under `.projects/<slug>/`
- `POST /api/projects/select` — switch active (also backfills `project_name` into state)
- `POST /api/projects/archive` — archive
- `POST /api/projects/restore` — restore archived
- `DELETE /api/projects` — permanently delete (archived only)

Design decisions:
- Archive first, delete only after archive — prevents accidental destructive deletes
- `.projects/` is gitignored (generated state, runtime files, sensitive config)
- On `select`, if `project-state.json` has empty `project_name`, it is backfilled from the index entry `name` field

---

## Project Name Resolution

When `state.project_name` is empty, `compute_full_state()` resolves:
1. Active project `name` from `.projects/index.json`
2. `os.path.basename(REPO_ROOT)` (directory slug)

The JS dashboard has a final fallback of `"My Project"` but this should never be reached in normal operation.

---

## Security Controls

### Thread Safety
Three module-level locks in `server.py`:
- `_state_lock` — protects `project-state.json` R/W
- `_reviews_lock` — protects `reviews.json` R/W
- `_index_lock` — protects `projects/index.json` R/W

Background threads (generate, review, build, fix, distill, build-system) run concurrently. Always acquire the relevant lock before reading or writing shared state.

### Path Traversal
Version handlers validate `ver_id` with `re.fullmatch(r'\d{8}-\d{6}', ver_id)` and check constructed paths start with `FORGE_DIR/versions/`.

### Model Allowlist
Two-layer validation:
1. Server: `KNOWN_TOOLS` in `server.py` (generated from `src/data/tools.json`)
2. Runtime: `_ALLOWED_MODELS` in compiled `forge` binary (also generated from `src/data/tools.json`)

Both layers are compiled from the same source — editing `tools.json` and rebuilding updates both.

### Electron IPC
- `setup-git-config`: type + length + email format checks
- `setup-ssh-unlock`: type + 1024-char cap
- `setup-save`: object type + 8 KB size cap

### Request Size
4 MB cap on all `do_POST` and `do_DELETE` body reads.

---

## Dashboard Architecture

Project landing page plus 9 operational views:

| View | Purpose |
|---|---|
| Projects | Create, select, archive, restore, delete managed projects |
| Overview | Phase strip, attention cards, stage matrix, sidebar stats + gates |
| Input | Raw markdown input files |
| Generate | Stage and all-stage AI generation |
| Review | File tree, rendered/raw viewer, critique/regenerate, gates, versions |
| Build | Build-system generation, git branch/commit/push/PR flow |
| Deploy | Environment cards, CI/CD workflow generator, GitHub secrets status |
| Issues | Lightweight issue tracker |
| Knowledge | Knowledge base pipeline — export, distill, sync |
| Settings | Product, AI tool/model, git, environments, danger zone |

---

## Design System State

Direction: Revolut-inspired. Sources of truth: `src/dashboard/DESIGN.md`, `src/dashboard/styles.css`.

Active tokens:
- `--primary: #4ADE80` — green
- `--accent: #494fdf` — cobalt violet (scarce)
- `--purple: #8B5CF6`
- Canvas: `#060D06`

Component sizing rules:
- Buttons: base 36px, sm 30px, xs 26px min-height
- Inputs: 40px min-height (38px compact)
- `.view-title`: 18px, not 40–64px (that is marketing scale)
- Cards: 20px border-radius

Critical rule: marketing design contracts cannot be applied literally to a dense dashboard. Adapt tokens and component rules for control density and readability.

---

## Desktop App (Electron)

The Electron app wrapper lives in `desktop/` — **not** `electron/`. The `electron/` directory name conflicts with Node.js package resolution and causes `not a file` errors in electron-builder.

The app spawns `server.py` from `~/.forge/scripts/server.py` (not from the repo). Environment:
- `FORGE_DATA_DIR` → active project's `.forge/` directory
- `FORGE_PROJECTS_ROOT` → `~/.forge/projects/`
- `FORGE_ORCHESTRATOR_ROOT` → `~/.forge/`

This means server fixes only reach Electron users when:
1. `~/.forge/scripts/server.py` is updated via hot-deploy (automatic on rebuild if dir exists), OR
2. The user runs `./forge upgrade` manually

### Asar Bundle
`desktop/package.json` `files` is an explicit allowlist. Every module required at runtime must appear:
```json
"files": [
  "main.js", "preload.js", "auth.js", "github.js", "org.js",
  "auth-preload.js", "setup-preload.js", "auth-window.html", "setup-window.html",
  "assets/**/*"
]
```
Omitting a file from this list silently excludes it from the asar bundle and causes a `Cannot find module` crash at runtime.

### macOS Distribution

macOS builds three targets: `dmg`, `pkg`, `zip`.

The `.pkg` installer runs `desktop/scripts/pkg/postinstall` which automatically executes `xattr -cr` on the installed app — users who install via `.pkg` get a working app with no manual intervention.

`entitlements.mac.plist` **must exist** at `desktop/assets/entitlements.mac.plist`. Its absence causes a malformed bundle and the "damaged" Gatekeeper error.

Required entitlements: JIT, unsigned memory, library validation disable, network client+server, file access.

Notarization: `desktop/scripts/notarize.js` is wired as `afterSign` hook. It is silent unless `APPLE_ID`, `APPLE_ID_PASSWORD`, `APPLE_TEAM_ID` are set in the environment (GitHub secrets). The hook also checks `CSC_LINK` is non-empty before notarizing.

User workaround for unsigned builds: `xattr -cr "/Applications/Forge OS.app"` or install via `.pkg`.

### Windows Distribution

`icon.ico` must contain a 256×256 image. Do NOT use Pillow's `Image.save(format="ICO")` — it produces single-size output. Use manual binary ICO construction with `struct.pack`.

Current file: 6 sizes (16/32/48/64/128/256 px), PNG-compressed, 32-bit RGBA.

---

## CI/CD

Single workflow: `.github/workflows/build-desktop.yml`

Working directory: `desktop/` (not `electron/`).

macOS arch targets (arm64 + x64) are built **sequentially** — not in a parallel matrix — to avoid pkg packaging race conditions.

Non-tag pushes → upload workflow artifacts (14-day retention).
Tag pushes (`v*`) → publish to GitHub Releases.

CI guard for empty `CSC_LINK`: `CSC_IDENTITY_AUTO_DISCOVERY: false` in workflow env prevents electron-builder from crashing when no signing certificate is configured.

**GitHub Pages**: branch-based from `/docs`. No Actions workflow. `static.yml` was deleted — having both caused duplicate deployments.

---

## Validation Workflow

Minimum after any change:

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

Browser sanity: Projects, Overview, Input, Generate, Review, Build, Deploy, Issues, Settings.

Acceptable finding: project absolute paths intentionally ellipsized in cards.

---

## Failure Log And Takeaways

**Server not reachable**
- Causes: server not running, wrong project target, stale port, runtime not upgraded
- Fix: rebuild → upgrade → kill port → restart in screen → verify with curl

**Stale generated dashboard**
- Cause: source changed without regenerating artifacts
- Fix: `python3 src/build_forge.py` → `./forge upgrade` → project upgrades

**Blank page after design experiment**
- Cause: layout instability + stale browser tab
- Fix: revert source, rebuild, upgrade, restart, open fresh tab

**Review panel overflow**
- Cause: fixed panel width + global `white-space: nowrap`
- Fix: widen panel, control button sizing, ellipsize labels

**Marketing design over-application**
- Cause: sparse landing-page design contract applied to dense dashboard
- Fix: preserve intent through tokens; adapt for dashboard density

**icon.ico too small (Windows CI)**
- Cause: ICO contained only 16×16 (400 bytes); electron-builder requires ≥256×256
- Fix: manual binary ICO construction with `struct.pack`; Pillow's ICO saver is broken for multi-size

**Duplicate GitHub Pages deployment**
- Cause: `static.yml` Actions workflow + branch-based Pages both active simultaneously
- Fix: delete `static.yml`; branch-based Pages from `/docs` needs no workflow

**"Unnamed Project" / "My Project" in dashboard**
- Cause 1: empty `project_name` in `project-state.json`
- Cause 2: hot-deploy missing `~/.forge/scripts/` so Electron server was stale
- Fix: 3-level fallback + `~/.forge/scripts/` in hot-deploy + backfill on select

**New model not visible in tool selector**
- Old pattern: model added to `server.py` but not `forge_cli.py.tmpl` (or vice versa)
- Current: both generated from `src/data/tools.json` — one edit + rebuild fixes both
- If a model is invisible: check `tools.json` entry, rebuild, upgrade

**macOS "Forge OS is damaged and can't be opened"**
- Cause: missing `entitlements.mac.plist` → malformed bundle; plus unsigned/unnotarized app quarantined by Gatekeeper
- Fix: create plist, add notarize hook, configure Apple secrets; auto-cleared by `.pkg` postinstall; user workaround: `xattr -cr`

**Git worktree config compatibility**
- Symptom: `core.repositoryformatversion does not support extension: worktreeconfig`
- Takeaway: prefer operating in main repo; only use worktrees if necessary

**Template extraction escape bug**
- Symptom: `SyntaxError: unexpected character after line continuation character` in generated `forge`
- Cause: raw file slicing preserves escaped bytes (`r\"\"\"`) instead of decoded values (`r"""`)
- Fix: use `ast.literal_eval()` to properly decode Python string escapes when extracting embedded string content

**`{agent}` KeyError in template format()**
- Symptom: `KeyError: 'agent'` during `python3 src/build_forge.py`
- Cause: `{agent}` inside template was consumed by `str.format()` before the f-string context could use it
- Fix: double all literal braces in `forge_cli.py.tmpl` that should pass through format(): `{{agent}}`, `{{gate}}`

**Electron `not a file` CI error**
- Symptom: `⨯ /path/forge-os/electron not a file` in electron-builder CI output
- Cause: directory named `electron/` conflicts with Node.js module resolution
- Fix: renamed to `desktop/`; any name except `electron/` works

**Missing asar modules (Cannot find module)**
- Symptom: Electron launches then crashes with `Error: Cannot find module './auth'`
- Cause: `package.json` `files` array is an explicit allowlist; unlisted modules are silently excluded
- Fix: add all required modules to `files`: auth.js, github.js, org.js, auth-preload.js, setup-preload.js, auth-window.html, setup-window.html

**Empty CSC_LINK electron-builder crash**
- Symptom: CI signing step crashes even when no certificate is intended
- Cause: empty string `CSC_LINK` env var treated as invalid certificate input
- Fix: `CSC_IDENTITY_AUTO_DISCOVERY: false` in CI env; notarize hook checks `process.env.CSC_LINK` non-empty

**macOS arch build race condition (pkg)**
- Symptom: arm64 and x64 pkg builds corrupt each other in parallel CI matrix
- Cause: shared pkg staging directories
- Fix: build arch targets sequentially in CI

**Edit insertion duplicate match**
- Symptom: Edit tool rejects with "not unique in the file"
- Cause: old_string context was too short, matched multiple locations
- Fix: always include several surrounding unique lines as context when inserting into dense files

**Consistency check exception swallowing is intentional**
- `_run_consistency_check()` in server.py is wrapped in try/except by design — a fix always completes even if the downstream AI check fails
- Advisory, not blocking

---

## Success Log

- Modular source layout; single built `forge` artifact
- `build_forge.py` is a ~260-line pure compiler — no magic strings, no inline templates
- `build_constants.py` centralizes all build-time constants
- `forge_cli.py.tmpl` is the real CLI template, fully wired
- `src/data/tools.json` is the single source for all AI tool/model config
- `src/data/stage_pipeline.json` centralizes all stage agent/gate/input/directory config
- AI prompts extracted to `src/data/prompts/` and injected at build time
- Data-driven `AGENT_CONTENT` and `GATE_CONTENT` dicts replace 24-branch if/elif chains
- Project-first dashboard with full create/select/archive/restore/delete lifecycle
- Thread-safe state I/O with three module-level locks
- Security hardening: path traversal, model allowlist, IPC validation, 4 MB request cap
- Structured logging with typed exception handling throughout `server.py`
- Hot-deploy includes `~/.forge/scripts/` for Electron users
- Overview command center: phase strip, attention cards, stage matrix, stats sidebar
- Deploy section: env cards, CI/CD workflow generator, secrets status
- Design system cleanup: tokens normalized, hero typography scaled down for dashboard
- GPT-5.5 in Codex and OpenAI tool selectors with allowlist enforcement
- macOS: `entitlements.mac.plist` created, notarization hook ready for Apple secrets
- macOS: `.pkg` installer with postinstall script auto-clears quarantine
- Windows: proper 6-size ICO (16/32/48/64/128/256 px)
- GitHub Pages: single clean deployment from `/docs` branch (no Actions workflow)
- `desktop/` rename resolves Node.js module name conflict permanently
- All Electron modules listed in asar `files` allowlist
- macOS CI: sequential arch builds prevent pkg race condition
- Beta release infrastructure: versioned tags, asset overwrite, download page auto-detection
- README, LICENSE, CLAUDE.md, AGENT.md, GEMINI.md all production-grade
- CLI warning strip: diagnostic noise filtered from AI subprocess stdout before persisting doc content
- Knowledge Base pipeline: export/distill/sync to separate KB repo with PR-based review governance
- Consistency check after fix: one AI call finds downstream doc drift; marks affected files needs_review
- Manual code review before push: per-file diff viewer + human verdict audit trail in build-review.json
- CI auto-release on version bump: push to main triggers tag + release when package.json version is new

---

## Handover Checklist

Run at takeover:

```bash
pwd
git status --short
git log --oneline -5
./forge version
./forge
python3 src/build_forge.py
python3 -m py_compile src/build_forge.py src/runtime/server.py
curl -sS http://127.0.0.1:8080/api/state | python3 -c "import sys,json; d=json.load(sys.stdin); print('project:', d.get('project_name'), '| phase:', d.get('phase'))"
```

Inspect:
- `src/build_forge.py` — compiler entry point
- `src/build_constants.py` — all build-time constants
- `src/data/tools.json` — AI tool and model registry
- `src/data/stage_pipeline.json` — stage agents, gates, inputs, directories
- `src/runtime/forge_cli.py.tmpl` — CLI template, `invoke_model()`, agent/gate loops
- `src/runtime/server.py` — API handlers, security controls, thread locks
- `src/runtime/constants.py` — all runtime constants (shared by server, build_runner, template)
- `src/dashboard/DESIGN.md` — design contract
- `src/dashboard/styles.css` — design tokens
- `.projects/index.json` — registered projects and active selection
- `desktop/package.json` — build config, files allowlist, targets, afterSign hook

Security check before sharing any state artifact:
- `.projects/<slug>/.forge/project-state.json` may contain tokens from testing
- `.forge/runs/*.json` may contain file paths and build output

Decision rule: if docs and runtime disagree, trust runtime, update docs, record the drift.
