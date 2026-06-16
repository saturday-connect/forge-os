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

> **Feature flag — Build + Deploy (initial release: OFF).** The `Build` and `Deploy` stages and all related UI + API endpoints are gated behind one flag, so the initial version ships the documentation lifecycle only: **Projects → Input → Generate → Review**. Resolution order: `FORGE_ENABLE_BUILD_DEPLOY` env (`1`/`0`) > project-state `build_deploy_enabled` > default `BUILD_DEPLOY_ENABLED_DEFAULT = False` (`constants.py`). Nothing is removed — flip the flag on and Build/Deploy return.
> - **Server:** `_resolve_build_deploy_enabled()` surfaces it in `/api/state`; `compute_full_state` caps `phase` at `review` when off; `_bd_guard()` returns `403` from every build/deploy endpoint (`build-system`, `build-log`, `build-preview`, `build-file`, `pr-status`, `build-review`, `build`, `secrets`, and the `env_config`/`env_save`/`deploy` actions).
> - **Frontend:** `renderAll` toggles `body.bd-off` and skips `renderBuild`/`renderDeploy`; `bdEnabled()` / `lifecyclePhases()` filter the lifecycle strip to 3 stages; `switchView` redirects `build`/`deploy` → `overview`; CSS hides nav `[data-view=build|deploy]`, `#view-build`/`#view-deploy`, and `.bd-only` (the Settings build profile, build-cache repo, and custom per-step/concurrency controls). Generate's per-stage models + batch toggle stay.

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
- After any source change: `python3 src/build_forge.py` — it rebuilds `./forge` and hot-deploys to every live `~/.forge/projects/*/scripts/` runtime (no manual `./forge upgrade` needed; that command stays for refreshing a standalone/legacy `.forge`).
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
```

That single command rebuilds `./forge` **and** hot-deploys `server.py`, `dashboard.html`, `constants.py`, `build_runner.py`, and `batch_runner.py` to every live `.forge/scripts/` directory it can find — including the Electron-managed runtimes under `~/.forge/projects/*/scripts/`. A local rebuild therefore updates running servers with no manual `./forge upgrade` step. (The legacy repo-root `.forge`, `.projects/task-flow`, and `test-projects/saas-todo` upgrade targets no longer exist — see the Failure Log.)

Smoke-test the dashboard against a throwaway managed project (the project root must pre-exist — `init` writes the `.forge` dotfile into it and the data dir under `~/.forge/projects/<uuid>/`):

```bash
mkdir -p /tmp/forge-smoke && ./forge --project /tmp/forge-smoke init
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill 2>/dev/null || true
./forge --project /tmp/forge-smoke dashboard 8080 &
sleep 2
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/            # expect 200
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/api/state   # expect 200
```

`--project <path>` goes before the command. Expected successful response: `200`.

---

## Validation Workflow

After any source change:

```bash
python3 src/build_forge.py
python3 -m py_compile src/build_forge.py src/runtime/server.py src/runtime/build_runner.py src/runtime/batch_runner.py
# build_forge.py already hot-deploys to every ~/.forge/projects/*/scripts/ — no per-project upgrade.
# Smoke-test against a throwaway managed project:
mkdir -p /tmp/forge-smoke && ./forge --project /tmp/forge-smoke init
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill 2>/dev/null || true
./forge --project /tmp/forge-smoke dashboard 8080 &
sleep 2
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/            # expect 200
```

For runtime changes affecting AI-dependent paths (generate/build/collaboration), prefer the **hermetic harness** discipline (stub the AI call, isolated temp project, local bare git repo) over a manual UI pass — see the Failure Log. UI sanity pass, when warranted, must cover: Projects, Overview, Input, Generate, Review, Build, Deploy, Issues, Settings.

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

**GitHub Pages**: Configured to deploy from the `/docs` folder on `main` directly — no Actions workflow needed or present (no `docs` branch exists). The old `static.yml` workflow was deleted to prevent duplicate deployments. The site is a single `docs/index.html` (inline CSS/JS) + `docs/assets/`. The version banner and download buttons are **fetched live from the latest GitHub release** (`api.github.com/repos/.../releases`, reads `tag_name` + `browser_download_url`) — never hardcode the version in the buttons; only the static JSON-LD `softwareVersion` is hand-maintained.

**Docs-vs-release hygiene**: a docs-only change must NOT bump `desktop/package.json` (the version-bump-to-release flow would cut a spurious desktop release). Pushing `docs/` to `main` still triggers `build-desktop.yml` (it builds but `check-version` skips the release). Add `paths-ignore: ['docs/**']` to the workflow to skip the app build on docs-only commits.

---

## Root And Project Directory Structure

Root-level source and orchestration:

```text
.forge/                      root runtime state for orchestrator dashboard (when run from repo root)
.projects/                   managed project workspace, gitignored
.projects/index.json         managed project registry
.projects/<slug>/.forge/     per-project generated runtime state
src/                         source for compiler, runtime, dashboard
forge                        built executable
~/.forge/projects/<uuid>/    Electron/CLI-managed project runtimes (the live runtimes build_forge.py hot-deploys to)
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
| Build | Build-system generation, git branch/commit/push/PR automation — **gated by the Build+Deploy flag (off by default)** |
| Deploy | Environment config, CI/CD workflow generator, GitHub secrets status — **gated by the Build+Deploy flag (off by default)** |
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
| `POST` | `/api/review` | Mark file reviewed or needs review. When `auto_push_on_review` is set and the mark transitions the project into review-complete (every generated doc reviewed), fires a fire-and-forget background push (role-gated: skipped for viewers; deduped; never blocks) |
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
| `POST` | `/api/knowledge/discover` | List shared projects from the KB discovery registry (`registry.json`) |
| `GET/POST/DELETE` | `/api/projects` | Managed project lifecycle |
| `POST` | `/api/projects/select` | Select active project (backfills name). When the project has `auto_pull_on_open` set and a docs repo, fires a fire-and-forget background pull (advisory; never blocks the response, deduped against a concurrent auto-pull) |
| `POST` | `/api/projects/archive` | Archive project |
| `POST` | `/api/projects/restore` | Restore project |
| `POST` | `/api/projects/share` | Action dispatch (`share` default, `unshare`, `invite`, `access`; unknown → 400). Share: provision a per-project docs repo (auto-create, else link; org shares attempt GitHub `internal` visibility, falling back to private with a `visibility_note`), mirror-push docs + manifest, list org/public shares in the KB discovery registry (private shares are de-listed, link-only). Unshare: de-list from the registry, clear local share state (`docs_repo_url` kept as `last_docs_repo_url`; the docs repo is not deleted). Invite: `{username, permission: pull\|push\|admin}` → GitHub collaborators API (201 → invited, 204 → updated; inputs validated server-side). Access: list direct collaborators + pending invitations, and resolve+cache the caller's `role` (admin/member/viewer from the repo `permissions`) |
| `POST` | `/api/projects/join` | Clone a shared docs repo into a new managed project (resolves repo by slug from the registry). A failed clone is classified by `_classify_clone_error` → `_clone_error_payload`: `reason: "bad_credentials"` (token invalid/expired → "update it in Settings", distinct from access) or `reason: "access_denied"` (token valid, lacks repo access → request-access flow; GitHub reports invisible private repos as not-found, and "write access … not granted" is the same signal); file://, ssh, and network errors stay plain errors |
| `POST` | `/api/projects/sync` | Sync the active project's stage docs with its docs repo (`direction: pull` default, `push`; unknown → 400). Pull: additive overlay, remote-wins — changed local files are snapshotted into the version store before overwrite (nothing lost), and a changed reviewed doc flips to `needs_review`. Push: pull-first, then mirror local → remote (local-wins; overwritten/deleted remote content snapshotted first), rejected push retries once (reset+re-mirror). Both stamp `last_synced_at`; a denied clone returns `reason: "access_denied"` like join |

`GET /api/projects` attaches a per-project `collaboration` summary (`shared`/`visibility`, `joined`, `docs_repo_url`, `role`, `last_synced_at`, `error`, `sync_error`) read from each project's own state file; `GET /api/state` exposes the active project's full `collaboration` block plus a live `syncing` flag (computed from the in-memory auto-sync inflight set, keyed by normalized docs-repo URL).

---

## State Files

```text
.forge/project-state.json       project settings (incl. auto_pull_on_open, auto_push_on_review), git, environments, builds, issues, collaboration (docs_repo_url, visibility, shared_at/joined_at, last_docs_repo_url + unshared_at after unshare, last_error, visibility_note when org-internal fell back to private, role + role_checked_at cached from GitHub, last_synced_at, last_sync_status + last_sync_error from the last auto-sync, share_note when the docs share succeeded but the discovery-registry listing did not)
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

The shared **discovery registry** lives in the KB repo at its root as `registry.json` (an external repo file, not under `.forge/`): a list of `{slug, name, visibility, docs_repo_url, code_repo_url, docs_path, doc_count, updated_at}` entries, one per org/public-visible project. `/api/projects/share` and `/api/knowledge/export` upsert it (merge-safe by slug, so neither writer clobbers the other's fields); `/api/knowledge/discover` reads it via the GitHub contents API. Registry writes retry once on a rejected push (reset to remote tip + re-apply the slug-keyed mutation — the mutate re-run is the merge, since two writers always conflict textually on one JSON file). Each shared project's docs repo also carries a self-describing `forge-project.json` manifest at its root. Confidential projects are never listed here — a private share (including an org/public → private re-share) actively de-lists its entry, and `/api/knowledge/discover` filters legacy private rows; private shares are joined by URL, with access enforced by GitHub repo permissions.

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

### Build Step Blocks On Missing Source Docs
- Symptom: `run_step` exits without calling the AI; `build-system.json` shows `status: error`, message "No source documents found"
- Cause: `collect_docs(meta)` returned empty — the step's `source_dirs` (e.g. `01-requirements`) had no `.md` files. Build steps are hard-gated on upstream specs and on `_STEP_REQUIRES` (e.g. integration needs backend built first)
- Implication: exercising `run_step` (in tests or real builds) requires seeded/generated spec docs; an empty project errors *before* any cache or AI logic runs

### Stale Validation Paths In This File
- Symptom: the documented `./forge upgrade`, `test-projects/saas-todo`, and `.projects/task-flow` targets report "Forge not initialized" — those dirs don't exist on this machine
- Cause: the real live runtimes are the Electron-managed projects under `~/.forge/projects/<uuid>/scripts/`; `build_forge.py` hot-deploys there (≈15 dirs), not to a repo-root `.forge`
- Takeaway: validate against `~/.forge/projects/*/scripts/` (or `init` a throwaway project). **Resolved:** the Build And Deploy Cycle + Validation Workflow sections were corrected to the throwaway-`init` + `--project … dashboard` smoke test (verified to return `200`); the dead `./forge upgrade` / `test-projects` / `task-flow` targets are gone

### Docs-Only Push Triggers A (Non-Releasing) CI Build
- Symptom: editing only `docs/` and pushing to main starts the full `build-desktop.yml` matrix
- Cause: the workflow triggers on any push to main. `check-version` then sees the current version already released and skips the *release*, but the build matrix still runs and uploads 14-day artifacts — wasted CI
- Fix: add `paths-ignore: ['docs/**']` to the push trigger so docs-only commits skip the app build. Also: a docs change must NOT bump `desktop/package.json` (that would cut a spurious release — the version-bump-to-release flow ties releases to the manifest version)

### Cross-Run Build Cache + AI Nondeterminism
- Design: the cache is content-addressed by `input_hash = sha256(tool\0model\0prompt)`; identical inputs restore the stored output at 0 tokens
- Note: AI output for identical inputs can differ run-to-run, so a store entry is "a valid output," not "the only output." `FORGE_FORCE_REBUILD=1` skips restore AND overwrites the entry, so a forced rebuild refreshes the cache rather than leaving a stale entry. The cross-run store hash and `run.py`'s single-file gen-cache hash are independent (different prompts), so toggling batch/per-file or local/remote modes can cause one redundant regen, then re-converges

### Testing AI-Dependent Runtime Without Spending Tokens
- Pattern established this session: validate generation/build orchestration by **stubbing the AI call** (`build_runner.invoke_ai` / a no-op `build_runner.py`) and running against an **isolated temp copy** of a managed project; for git-backed features, point at a **local bare repo** (`git init --bar`e + `file://`). Assert on observable effects (files written, env vars passed to the subprocess, exit codes, `build-system.json` fields, cache entries) — never on model output
- This made every beta.110–116 change verifiable with zero AI/credential cost; reuse it for future generate/build changes

### Collaboration Auth/Access Errors Surfaced Raw (beta.130)
- Symptom: users hit `GitHub API error 401: Bad credentials`, a clone `remote: Write access to repository not granted`, and `GitHub API error 404` (list-collaborators) — raw, unactionable. Confusing because "it's my repo" (ownership is irrelevant if the credential is rejected)
- Causes: **401 = invalid/expired token** (the credential GitHub receives is rejected — NOT a repo-access problem); **clone "write access not granted" / not-found = token valid but lacks access** to that repo; **collaborators 404 = lacking push access** (GitHub returns 404, not 403, to hide repo existence)
- Fix: `_gh_api_error` maps 401→"token invalid/expired, update in Settings", 403→scope/SSO, 404→no-access; `_classify_clone_error` splits clone failures into `bad_credentials` (fix token) vs `access_denied` (request access) — the two must stay distinct or the UI sends users to the wrong remedy
- Diagnostic method that worked: read the user's actual `project-state.json` `collaboration` block (found shared→unshared today, re-share cloning the existing repo) and the real index (2 projects, not the test pollution) — runtime state over guessing

### Hermetic Harnesses Polluting `~/.forge` via Real `forge init`
- Symptom: ~95 orphan project dirs accumulated under `~/.forge/projects/` from test runs (Shared Proj, Plain Proj, etc.)
- Cause: harnesses that run the real `forge init` subprocess (those passing `FORGE_SCRIPT`) create their data dir under `~/.forge/projects/<uuid>/` regardless of the temp project root — `init` resolves the data dir from `HOME`, not from `FORGE_REPO_ROOT`
- Fix: set `os.environ["HOME"] = base` (the temp dir) at the top of those harnesses BEFORE importing server / spawning the subprocess, so `~/.forge` resolves in-sandbox consistently across the test process AND the subprocess. Subprocess-only `HOME` is insufficient — the test process expands the index's `~/.forge/...` `data_dir` with the real HOME and mismatches. This is the "isolate side effects" rule: a real `forge init` writes to global `~/.forge`; sandbox `HOME` to contain it

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
- Build DAG view + timing console (Phase 4): the build step dependency graph is centralized as `_BUILD_DAG` (server.py — single source for the parallel scheduler and the UI) and exposed via `GET /api/build-system` (`deps`). The Build view renders a "Build plan" panel (`renderBuildDag` in app.js): dependency waves (backend -> frontend/integration -> tests/infra) with per-step status, duration (`generated_at - started_at`), tokens, and cache badge, live-updating via the existing build polling. All timing/token data already lived in `build-system.json` — no new state. Completes the build-optimization roadmap (Phases 1-4: concurrency/retry, profiles, persistent+remote cache, observability)
- Hermetic test discipline for AI-dependent runtime: every beta.110–116 change validated by stubbing the AI call + isolated temp projects + local bare git repos — zero AI/credential cost (see Failure Log)
- Public site refreshed (docs/index.html): build-optimization feature cards added, stale `beta.28` tags removed, JSON-LD version current; deployed via the `docs/` folder on main without an app version bump
- AI Runtime settings decluttered (beta.117): progressive disclosure — only 3 primary controls stay visible (AI Tool, Default model, Build profile); per-stage model tiering, batch generation, build cache repo, and (Custom-only) per-step tiering + max-parallel move into a collapsed `<details class="settings-advanced">`. Choosing Custom reveals the per-step controls (`updateProfileButtons` toggles `#settings-custom-build`) and auto-opens Advanced. All element IDs preserved so save/seed wiring is unchanged. Verified via DOM eval: AI Runtime card exposes exactly 3 top-level `.form-group`s with Advanced collapsed by default
- Project collaboration (beta.118–120): docs-first sharing across machines with **no central server** — access delegated to GitHub repo permissions. **Share** (`/api/projects/share`) provisions a per-project docs repo (auto-create via GitHub API, else link a pasted URL), pushes the full `.forge` doc set + a `forge-project.json` manifest, and registers `{docs_repo_url, visibility}` in a shared `registry.json` at the KB repo root (merge-safe upsert; the reviewed-docs export coexists without clobbering). **Discover** (`/api/knowledge/discover`) lists the registry via the contents API; **Join** (`/api/projects/join`) clones a shared docs repo into a new managed project (mirrors create-project, overlays docs into the resolved `data_dir`). UI: Share button + visibility dialog (private/org/public) on each project card, and a "Shared with your team" discovery list with Join, on the Projects home. Validated hermetically (local bare repos; only repo-create stubbed) + in-browser (preview screenshots). Three per-phase commits.
- Build + Deploy feature flag (initial release, OFF by default): one flag gates the Build + Deploy stages and ALL related UI + endpoints so v1 ships the documentation lifecycle only (Projects → Input → Generate → Review). Server: `BUILD_DEPLOY_ENABLED_DEFAULT` (constants), `_resolve_build_deploy_enabled` (env `FORGE_ENABLE_BUILD_DEPLOY` > state `build_deploy_enabled` > default) surfaced in `/api/state`, phase capped at `review` when off, `_bd_guard()` 403s all build/deploy endpoints + the `env_config`/`env_save`/`deploy` actions. Frontend: `body.bd-off` + `.bd-only` CSS + `bdEnabled()`/`lifecyclePhases()` + a `switchView` guard hide the nav, the 3-stage lifecycle strip, the views, and the Settings build controls (Generate's per-stage models + batch toggle kept). Gate-not-delete, fully reversible. Validated hermetically (resolver precedence + endpoints 403 off / 200 on) and in-browser (off = 3-stage lifecycle, no Build/Deploy nav; on = restored). Three per-phase commits on `feat/build-deploy-flag`
- Collaboration registry hygiene (beta.123, Phase 3a of the completion plan): five fixes hardening the share/discover/join loop. (1) **Private shares unlisted** — the share path routes private visibility to `_deregister_from_kb` (covers org/public → private downgrades) and `/api/knowledge/discover` filters legacy private rows, closing the metadata leak where confidential names/slugs appeared in the team registry. (2) **Registry write serialization** — `_kb_registry_op` retries a rejected push once via reset-to-remote + re-apply of the slug-keyed mutation (the mutate re-run IS the merge; textual rebase always conflicts on one JSON file). (3) **Mirror re-share** — stage markdown in the docs repo clone is cleared before copying, so local deletions/renames propagate instead of accumulating. (4) **Unshare** — `action: "unshare"` on `/api/projects/share` (allowlist-validated) de-lists + clears the collaboration block, keeping `last_docs_repo_url` for one-click re-share; the share dialog shows current share state, a confirm-guarded Stop sharing, and pre-fills the repo URL (fixing re-share's spurious auto-create 502). (5) **Card pills** — `GET /api/projects` attaches a collaboration summary read from each project's own state file (no index denormalization); cards show Shared/Joined/Share-error pills, making background share failures visible. Validated hermetically (5 harnesses, 23 assertions: local bare repos, race injection via mutate hook, real server subprocess + real `forge init`) + in-browser; per-chunk commits on `feat/collab-registry-hygiene`
- Collaboration access management (beta.124, Phase 3b): the missing access half of docs sharing. (1) **Invite + list collaborators** — `/api/projects/share` gains `invite` (`{username, permission}` → GitHub collaborators API, 201 → invited / 204 → updated, username + permission validated server-side before any network call) and `access` (direct collaborators with admin/push/pull labels + pending invitations); the Share dialog gains an Access section with live list and invite controls. GitHub stays the authorizer — non-admin callers get the 403 verbatim; non-GitHub docs repos (file://, ssh) are rejected cleanly. (2) **Org-internal visibility** — org shares with an org context attempt `visibility: internal` on repo create; non-Enterprise orgs fall back to a private repo with the downgrade recorded as `visibility_note` (state + share response + dialog). (3) **Request-access UX** — denied github.com join clones (not-found IS GitHub's denial signal for invisible repos) return `reason: access_denied` and the UI shows a "No access yet" dialog naming the fix (owner invites via Share → Access) with the repo URL ready to copy, closing the invite/request loop. Validated hermetically (3 harnesses, 15 assertions: stubbed GitHub API asserting exact request shapes, real server subprocess for every validation guard, classifier truth table) + in-browser; per-chunk commits on `feat/collab-access`
- Collaboration sync round-trip (beta.125, Phase 3c): the pull/push half that makes shared docs a two-way channel. (1) **Pull** (`/api/projects/sync {direction: pull}`) — additive overlay, remote-wins: new remote files copied, changed files overwrite local ONLY after the local content is snapshotted into the existing version store (`_snapshot_rel_version`, same layout the generator + `/api/version` use — so a remote-wins pull is fully restorable), local-only files kept (deletions ride push's mirror). A pulled change to a reviewed doc flips it to `needs_review`. (2) **Push** (`{direction: push}`) — pull-first (never blind-clobbers unseen remote work), then mirror local → remote (local-wins; every remote file overwritten or deleted is snapshotted first + stays in git history); rejected push retries once (reset to remote tip, re-mirror) for last-writer-wins with the loser preserved — the same reset+retry shape as the registry writer. (3) **Roles** — `_gh_repo_role` maps the repo `permissions` to admin/member/viewer, cached on the `access` call; the Share dialog gates Invite + Stop sharing to admins and the Sync dialog gates Push to non-viewers, both failing OPEN on an unknown role (UX hint only — the endpoint + GitHub still enforce). (4) **UI** — a Sync button on any project with a docs repo opens a Pull/Push dialog with last-synced time; cards show a Synced timestamp; denials reuse the request-access dialog. Validated hermetically (5 harnesses, 19 assertions: two-project round-trip via `set_project_root`, push race via the `_pre_push_hook` seam, real server subprocess for the endpoint + review-invalidation, stubbed-API role truth table) + in-browser (all role/direction states); per-chunk commits on `feat/collab-sync`
- Collaboration hardening + closure (beta.126, Phase 3d — final): (1) **Re-join duplicate detection** — `_run_join_project` previously cloned a silent duplicate project on a re-join (`ensure_unique_slug`); the join handler now scans non-archived projects (`_find_joined_project`, URL normalized for trailing-slash/`.git` via `_normalize_repo_url`) and short-circuits to `200 {status: "already_joined", project}` so the UI opens the existing project instead. (2) **Structured op logging** — `_log_collab_op` emits one uniform line per collaboration op (`op`, `slug`, `outcome`, `dur_ms`, `detail`; WARNING on error, INFO otherwise) wired into share, join (incl. the already-joined short-circuit), and both sync directions — the round-trip is observable with timings, not just failure-path warnings. (3) **Docs closure** — public site "Team collaboration" card rewritten to the shipped docs-first model (was the old org-config copy), JSON-LD `softwareVersion` refreshed. Validated hermetically (2 harnesses, 10 assertions: re-join via real server subprocess + real `forge init`, log capture in-process + a live sync.pull stderr assertion) + in-browser (already_joined short-circuits with no duplicate). Closes the collaboration roadmap; per-chunk commits on `feat/collab-hardening`
- Collaboration auto-sync, Phase A — pull-on-open (beta.127): opt-in `auto_pull_on_open` (default off, Settings → Git Configuration toggle, persisted in `project-state.json`). Selecting a project with a docs repo fires a fire-and-forget background pull (`_maybe_auto_pull`): reuses the manual `_run_pull_sync` (remote-wins + version snapshot), applies the same review-invalidation + `last_synced_at` stamp so the auto and manual paths converge, dedups against a concurrent auto-pull of the same project (`_autosync_inflight` set + lock), logs `detail=auto`, and never blocks the select response. No token requirement — matching manual sync, `file://`/public repos pull tokenless and a private repo without a token just fails the advisory pull. Validated hermetically (1 harness, 4 assertions: background-thread effect polled via the inflight set, dedup no-op, real server subprocess proving select-triggers-pull, and toggle-OFF-does-not-pull) + in-browser (settings round-trip ON/OFF through `/api/state`). Phase B (push-after-review, needs a debounce/checkpoint policy) deferred. Per-chunk commits on `feat/collab-autosync-pull`
- Collaboration auto-sync, Phase B — push-after-review (beta.128): opt-in `auto_push_on_review` (default off, Settings → Git Configuration toggle). In `/api/review`, the handler snapshots reviews before the mark and fires a fire-and-forget background push (`_maybe_auto_push`: pull-first like the manual endpoint, then mirror local → remote) ONLY on the not-complete → complete transition — so it pushes once when review finishes, never per file. The checkpoint `_autopush_review_complete` is intentionally LOOSER than `compute_full_state`'s `all_reviewed` (every *generated* doc reviewed, ≥1 doc — not all 11 stages populated), otherwise it would almost never fire; an empty project never reports complete. Role-gated (skips a known `viewer`, fails open on unknown — GitHub still enforces), deduped via the shared `_autosync_inflight`, logged `detail=auto`. The auto-sync scaffold was refactored into `_spawn_autosync` (dedup + daemon thread) shared by pull + push, with `_autosync_invalidate_reviews` / `_stamp_last_synced` extracted. Validated hermetically (1 harness, 6 assertions: checkpoint truth table incl. empty-project guard, `_maybe_auto_push` background effect, real server subprocess proving the review-complete transition pushes, toggle-OFF no-push, viewer role-gate no-push) + in-browser (both toggles round-trip independently). Completes auto-sync (both halves) and the collaboration feature. Per-chunk commits on `feat/collab-autosync-push`
- Collaboration auto-sync visibility (beta.129): surfaces the otherwise-silent fire-and-forget auto-sync, and fixes a latent keying bug found while building it. (1) **Unified inflight key** — auto-pull keyed `_autosync_inflight` by the index `project_id`, auto-push by the normalized docs URL, so a pull + push for one project couldn't dedup against each other; both now key by the normalized docs-repo URL (`_spawn_autosync(sync_key, ...)`, the unused `project_id` param dropped from both runners). (2) **Live `syncing` flag** — `_is_autosyncing(repo_url)` checks the inflight set; `_state_collaboration` layers a computed `syncing` onto `/api/state`'s collaboration block; the workspace topbar renders a "Syncing…" chip via the existing 3s poll. (3) **Persisted errors** — `_stamp_last_synced` sets `last_sync_status="ok"` + clears the error; `_record_sync_error` persists `last_sync_status="error"` + `last_sync_error` on every auto-sync failure path (was log-only); the project summary surfaces `sync_error` and the projects-home card shows a red "Sync error" pill. Validated hermetically (1 harness, 4 assertions: inflight/state flag tracking incl. `.git` normalization, error persist+clear round-trip, pull↔push cross-dedup proving the key fix) + in-browser (topbar chip, card pill); per-chunk commits on `feat/collab-autosync-indicator`
- Collaboration auth/access error messages (beta.130): real-world bug — share/sync/join surfaced raw GitHub errors (`401: Bad credentials`, clone `Write access to repository not granted`, collaborators `404`) that didn't tell users what to do. `_gh_api_error` maps API codes to actionable text (401 → token invalid/expired, update in Settings; 403 → scope/SSO; 404 → no-access) across the four collaboration GitHub helpers; `_classify_clone_error` + `_clone_error_payload` split clone failures into `bad_credentials` (fix the token — distinct from access, since owning the repo is irrelevant if the credential is rejected) vs `access_denied` (request-access flow), recognizing the exact "write access … not granted" phrasing that previously slipped through; the Share-error pill and the sync/join handlers all carry the friendly message + routable `reason`. Validated hermetically (1 harness, 6 assertions: classifier truth table incl. the user's exact errors, payload routing, `_gh_api_error` mapping, live sync of an inaccessible repo) + in-browser (bad-credentials sync toast); full 19-harness regression (b3 updated to assert the bad_credentials/access_denied split). Also hardened the hermetic harnesses to sandbox `HOME` so real `forge init` stops polluting `~/.forge` (see Failure Log), and cleaned ~95 accumulated orphan dirs. Per-chunk commits on `fix/collab-access-errors`
- Collaboration real-world hardening (beta.131): five fixes surfaced by a user exercising the feature end-to-end. (1) **Live token update** — `/api/settings` wrote a pasted PAT to the `_pat_signal` file for Electron but never updated the running server's `GIT_PAT`, so a freshly-fixed token kept 401-ing until app restart; `_set_git_pat` (a module-level setter, since `global GIT_PAT` can't be declared inside `do_POST` where GIT_PAT is read earlier) now applies it in-session immediately. (2) **Invite username normalization** — `_normalize_gh_username` accepts `@handle` and profile-URL paste forms (strips `@`, unwraps `github.com/octocat`) and the error says the expected format. (3) **Join by URL** — the discovery list only joined by slug, and private shares are never listed there, so a private/direct share had NO UI join path; an always-visible "Join by URL" block on the Projects home posts `repo_url` to the existing join endpoint (routes access_denied/bad_credentials like the rest). (4) **Members list** — the Share→Access list renders as a proper member roster (count, mapped permissions read/write/admin, pending invitations in amber) instead of plain text. (5) **Share severity** — a docs share that succeeded but whose discovery-registry LISTING failed (commonly: no KB repo) showed a red "Share error"; it's now a soft `share_note` ("Shared — not listed… members can still Join by URL") with `last_error` reserved for real docs-push failures. Validated hermetically (f1–f3 + updated b1: live-PAT session effect via real subprocess, username truth table, share-severity advisory-vs-error) + in-browser (Join-by-URL posts repo_url, members roster render); full 21-harness sweep. Diagnosed throughout by reading the user's real `project-state.json` collaboration block. Single branch `fix/collab-invite-token`

---

## Future Guidance

Direction and known limitations for the next iteration. None of these block current functionality.

### Build optimization (Phases 1-4 shipped)
- **Remote cache (D2) is manual-sync.** Auto-sync (pull-before-build / push-after, fire-and-forget so it never blocks a build) is the natural next step. Keep it advisory.
- **Cache GC is a simple LRU cap** (`_BUILD_CACHE_MAX_ENTRIES = 300`). Add size-based eviction + a remote-cache GC if stores grow large.
- **`FORGE_VALIDATE_BUILD` is only enabled by the `thorough` profile.** A standalone "validate build output" toggle would let `custom` profiles opt in without going thorough.
- **The DAG view is read-only.** Could add per-step log drill-down and a live timing waterfall (data is already in `build-system.json`).

### Collaboration — Phase 3 (access & sync), shipped
The full collaboration feature is shipped: docs-first sharing (beta.118–120), registry hygiene (beta.123), access management (beta.124), the sync round-trip (beta.125 — pull/push with version-snapshot overwrite protection, GitHub-permission→role gating, Sync dialog), and hardening + observability (beta.126 — re-join duplicate detection, structured op logging). Remaining nice-to-haves:
- **Auto-sync is fully shipped + observable**: pull-on-open (beta.127, `auto_pull_on_open`) + push-after-review (beta.128, `auto_push_on_review`) + visibility (beta.129 — live "Syncing…" topbar chip via the `syncing` state flag, persisted `last_sync_error` surfaced as a card pill). All opt-in, advisory, fire-and-forget. Remaining follow-up: a time-based debounce/coalesce only if rapid review marks ever cause redundant pushes (the transition guard already prevents per-file spam — speculative until observed).
- **Conflict policy is remote-wins + version snapshot** (push is local-wins + snapshot). No three-way merge of concurrent edits to the same doc; the loser is always preserved in version history, never auto-merged. A field-level or section-level merge would reduce snapshot churn for large teams.
- **Invitee teams**: invite is per-username; org **team** grants (`PUT /orgs/{org}/teams/{slug}/repos/...`) would suit larger orgs.

### Hygiene / debt
- **Shared string literals between `build_runner` and `server` are deliberately left inline** — investigated for centralization (the `BUILD_CACHE_DIRNAME` precedent) and judged not worth it. The build-status field names (`generated_at`, `started_at`, `tokens_in`/`tokens_out`, `tokens_in_est`, `cache_hit`) are a stable conventional vocabulary reused across the build, generate, and cache payloads — not a single coupled writer↔reader contract (e.g. `phase_id` is written by `build_runner` but `server` reads only the unrelated lifecycle `active_phase_id`). A `BUILD_STATUS_KEYS` group would mislabel cross-context uses and add indirection without real drift protection. External well-known names (`.env`, `package.json`, `docker-compose.yml`, `requirements.txt`) are fixed by their ecosystems and likewise stay inline. The bar stays `BUILD_CACHE_DIRNAME`: centralize a literal only when a rename in one file silently breaks another.

### Method to keep using
- For any generate/build runtime change, **validate hermetically** (stub `invoke_ai` / `build_runner`, isolated temp project, local bare repo) before shipping. It caught the real bug this session (build step blocked on empty source docs) at zero cost.
- Ship in **phases, each its own `beta.NNN` + merge + release**, with a confirm-before-next-phase checkpoint.

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
