# Forge OS — Developer Reference

> Version: 0.2.0 · Python 3 stdlib only · Zero external dependencies

---

## Product Overview

Forge OS is a **documentation-first PDLC automation framework**. It treats Markdown files as executable state — AI agents read, generate, and gate-check structured documents across an 11-stage product lifecycle, from raw idea to marketing copy.

The lifecycle moves in one direction: **Input → Generate → Review → Build → Deploy**. Each stage produces artifacts that feed the next. Gates enforce human review before progression.

---

## Architecture: The God Script Pattern

All logic lives in **one file**: `src/build_forge.py`.

This file is not a runtime script — it is a **build script** that writes every other file at build time. Running it produces:

- `forge` — the CLI binary (a standalone Python script with all logic embedded)
- `.forge/` — the live project environment (written on `./forge init`)

```
src/build_forge.py          ← Edit everything here
    │
    ├── TEMPLATE            ← The forge CLI template (str.format()-based)
    ├── SERVER_PY_CONTENT   ← Raw string, embedded into TEMPLATE as {SERVER_PY_CONTENT}
    ├── DASHBOARD_HTML      ← Read from src/dashboard.html at build time
    ├── AGENTS              ← Dict of agent persona markdown strings
    ├── STAGE_OUTPUT_FILES  ← Dict mapping stage key → list of output file paths
    └── build_forge()       ← Writes everything to forge binary
```

**Rule**: Never edit files inside `.forge/` directly. They are overwritten on every `./forge upgrade`. Always edit `src/build_forge.py` (server, CLI logic, agents) or `src/dashboard.html` (UI), then rebuild.

---

## Build & Deploy Cycle

```bash
# 1. Edit source
vim src/build_forge.py         # server logic, CLI, agents
vim src/dashboard.html         # dashboard UI

# 2. Rebuild forge binary
python3 src/build_forge.py     # outputs: "forge built successfully."

# 3. Apply to a project
./forge --project <path> upgrade   # updates .forge/scripts/, preserves docs & state

# 4. Restart server
pkill -f "server.py"
./forge --project <path> dashboard 8080
```

For rapid iteration use the dev shortcut:
```bash
./forge dev 8080
# Does: build → init → symlink src/dashboard.html → serve
# The symlink means dashboard edits are live without rebuilding
```

---

## CLI Reference

| Command | Description |
|---|---|
| `./forge init` | Fresh environment setup under `.forge/` |
| `./forge --project <path> init` | Initialize a specific project directory |
| `./forge generate <stage> [input-file]` | Run AI agent for a stage |
| `./forge pipeline [input-file]` | Run all 11 stages in sequence |
| `./forge dashboard [port]` | Start the web UI (default: 8080) |
| `./forge upgrade` | Update runtime scripts, preserve project data |
| `./forge dev [port]` | Build + init + symlink + serve (dev mode) |
| `./forge version` | Print version |

**Multi-project support**: Every command accepts `--project <path>` to target a directory other than the current one. The CLI passes `AEOS_REPO_ROOT` as an env var to the server subprocess.

---

## Directory Structure (inside `.forge/`)

```
.forge/
├── 00-raw-input/           ← User-authored input files (never cleared by reset)
├── 00-context/             ← Stage 1: product vision, personas, positioning
├── 01-requirements/        ← Stage 2: BRD, PRD, metrics
├── 02-design/              ← Stage 3: UX, design system, screen specs
├── 03-analysis/            ← Stage 4: domain model, user journeys, risks
├── 04-architecture/        ← Stage 5: system design, APIs, data model
│   └── adr/                ← Architecture Decision Records
├── 05-delivery/            ← Stage 6: roadmap, epics, sprint plan
├── 06-engineering/         ← Stage 7: backend/frontend/integration specs
├── 07-quality/             ← Stage 8: test strategy, acceptance criteria
├── 08-operations/          ← Stage 9: runbooks, monitoring, incident response
├── 09-release/             ← Stage 10: release notes, rollout plan
├── 10-marketing/           ← Stage 11: GTM, positioning, content
├── 11-agents/              ← Agent persona definitions (markdown)
├── 12-gates/               ← Gate checkpoint files (PENDING / PASSED)
├── 13-decisions/           ← Decision log, change log, ADR index
├── 14-assets/              ← Logos, mockups, diagrams, screenshots
├── runs/
│   ├── status.json         ← Live generation status (polled by dashboard)
│   └── run-log.md
├── scripts/
│   ├── server.py           ← HTTP server (generated from SERVER_PY_CONTENT)
│   ├── dashboard.html      ← Dashboard UI (generated from src/dashboard.html)
│   ├── run.py              ← Single-file agent runner
│   ├── stage_runner.py     ← Stage orchestration
│   └── validate_gates.py   ← Gate evaluation
├── reviews.json            ← Per-file review status map {"path": "reviewed"}
└── project-state.json      ← Project settings, builds, issues, git, envs
```

---

## State Files

### `runs/status.json`
Polled every 3 seconds by the dashboard. Written by the server during generation.
```json
{ "status": "running|idle", "stage": "context", "updated_at": "ISO8601" }
```

### `reviews.json`
Flat map of reviewed file paths. Absence = `needs_review`.
```json
{ "00-context/business-model.md": "reviewed" }
```

### `project-state.json`
Persistent project configuration. Survives `upgrade` and `reset`.
```json
{
  "project_name": "",
  "builds": [],
  "issues": [],
  "git": {
    "repo_url": "", "username": "", "email": "",
    "token": "", "default_branch": "main", "branch_prefix": "forge"
  },
  "environments": {
    "staging":    { "url": "", "branch": "staging", "status": "", "deployed_at": "" },
    "production": { "url": "", "branch": "main",    "status": "", "deployed_at": "" }
  },
  "tool": "claude",
  "model": ""
}
```

---

## API Reference (server.py)

All endpoints served at `http://localhost:<port>`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serve `dashboard.html` |
| `GET` | `/api/state` | Full project state (tree, gates, phase, builds, issues, envs) |
| `GET` | `/api/file?path=<rel>` | Return raw file content |
| `GET` | `/api/raw-input?name=<file>` | Return raw input file content |
| `POST` | `/api/raw-input` | `{name, content}` — create/update raw input file |
| `DELETE` | `/api/raw-input` | `{name}` — delete raw input file |
| `POST` | `/api/generate` | `{stage: "all"\|"context"\|...}` — start generation thread |
| `POST` | `/api/build` | Start git branch + commit + push + PR in background |
| `POST` | `/api/review` | `{path, status: "reviewed"\|"needs_review"}` — update review + sync gates |
| `POST` | `/api/fix` | `{path, critique}` — trigger targeted agent regeneration |
| `POST` | `/api/gate` | `{gate}` — manually toggle gate to PASSED |
| `POST` | `/api/issue` | `{id?, type, title, description, priority}` — create/update issue |
| `POST` | `/api/settings` | `{project_name, tool, model, git, environments}` — save settings |
| `POST` | `/api/reset` | Clear all generated docs, reviews, and gate statuses (keep raw input + project-state) |

### `/api/state` Response Shape
```json
{
  "version": "0.2.0",
  "phase": "input|generate|review|build|deploy",
  "project_name": "",
  "tree": { "00-context": [{"name": "...", "status": "needs_review|reviewed|empty", "size": 0, "modifiedAt": 0}] },
  "gates": { "context-gate": "PENDING|PASSED" },
  "stageReviewSummary": { "00-context": { "total": 6, "generated": 4, "reviewed": 2 } },
  "processing": { "status": "idle|running", "stage": "" },
  "rawInputs": [{"name": "raw-input.md", "size": 1024, "modifiedAt": 0}],
  "builds": [],
  "issues": [],
  "environments": {},
  "git": {},
  "tool": "claude",
  "model": ""
}
```

---

## Phase Computation

The lifecycle **phase** is computed dynamically from actual file state — never stored. Logic in `/api/state`:

| Phase | Condition |
|---|---|
| `input` | No raw input files, or all stage files are empty |
| `generate` | Raw inputs exist but generated docs < 50% |
| `review` | Generated docs ≥ 50% but not all reviewed |
| `build` | All generated docs reviewed, no builds yet |
| `deploy` | At least one build exists |

---

## Gate System

Gates live in `.forge/12-gates/<name>.md`. Each gate file has a `## Status` section containing `PENDING` or `PASSED`.

**Gate evaluation** (`evaluate_gate(gate_name)`): reads all files in the stage mapped to that gate, checks `reviews.json`, returns `PASSED` if every generated (non-empty) file is reviewed.

**Gate → Stage mapping** (`GATE_STAGE_MAP`):
```python
"context-gate"      → "00-context"
"prd-gate"          → "01-requirements"
"design-gate"       → "02-design"
"architecture-gate" → "04-architecture"
"engineering-gate"  → "06-engineering"
"qa-gate"           → "07-quality"
"release-gate"      → "09-release"
"marketing-gate"    → "10-marketing"
```

**Gate status parsing** uses a line-scan (not regex) to find the value after `## Status`. This avoids `\n` escaping bugs inside Python template strings.

---

## Dashboard Architecture

8 views, all rendered from a single `state` object polled every 3 seconds:

| View | Key | Purpose |
|---|---|---|
| Overview | `1` | Lifecycle stepper, stats, next-action guidance |
| Input | `2` | Create/edit/delete raw input `.md` files |
| Generate | `3` | Per-stage and "Generate All" AI pipeline triggers |
| Review | `4` | 3-panel: file tree · content viewer · AI critique |
| Build | `5` | Git branch/commit/push/PR creation |
| Deploy | `6` | Staging + production environment cards |
| Issues | `7` | Inline bug/feature tracker |
| Settings | `8` | Product name, AI tool, git config, environments, danger zone |

Keyboard shortcuts: `1`–`8` switch views. Disabled when focused on inputs.

**Icon system**: All icons are inline SVG from Heroicons 2.0 outline style (24×24 viewBox, `stroke-width: 1.75`). The JS `icon(name, size)` helper renders from the `ICONS` constant. No emoji anywhere in the UI.

**Template escaping rule**: `src/build_forge.py` uses `TEMPLATE.format(...)`. Inside TEMPLATE, all literal `{` and `}` must be escaped as `{{` and `}}`. `SERVER_PY_CONTENT` is defined as a raw string (`r"""..."""`) **outside** TEMPLATE and passed as a format argument — this avoids needing to escape every dict literal and f-string in server code.

---

## Adding New Features Checklist

### New API endpoint
1. Add handler block in `SERVER_PY_CONTENT` (in `src/build_forge.py`) before the `404` fallthrough
2. Rebuild: `python3 src/build_forge.py`
3. Upgrade project: `./forge --project <path> upgrade`
4. Add JS call in `src/dashboard.html`

### New stage output file
1. Add path to `STAGE_OUTPUT_FILES[stage]` in `src/build_forge.py`
2. Rebuild and re-init (`./forge init` creates empty stubs via `files_to_touch`)

### New dashboard view
1. Add nav item in `<nav id="sidebar">` with `data-view="<name>"` and `onclick="switchView('<name>')"`
2. Add `<div class="view" id="view-<name>">` in `#main`
3. Add render function `render<Name>()` and call it from `renderAll()`
4. Add to `viewKeys` array for keyboard shortcut

### New agent persona
1. Add entry to `AGENTS` dict in `src/build_forge.py`
2. Add agent name to the `agents` list inside `cmd_init()`
3. Rebuild and re-init

---

## Known Bugs Fixed (Session Log)

| Bug | Root Cause | Fix |
|---|---|---|
| Port not passed to server | `cmd_dashboard` called `subprocess.run` without port arg | Pass `str(port)` as argv; server reads `sys.argv[1]` |
| Server reading wrong `.forge/` | `AEOS_REPO_ROOT="."` resolved to repo root, not project | `cmd_dashboard` computes absolute `project_root` and passes via env var |
| Marketing gate false PASSED | `"PASSED" in content` matched "Change Status to PASSED" in gate notes | Added `parse_gate_status()` with line-scan instead of `in` check |
| Orange dots on empty files | `stageReviewSummary.total` counted all files including 0-byte stubs | Added `generated` field (non-empty files only); dashboard uses it for progress |
| `[AEOS]` visible in output | Log prefix and argparse description used old internal name | Renamed to `[Forge]` and `Forge Pipeline Runner` |
| `\n` in TEMPLATE caused SyntaxError | `r'^##\s+Status\s*\n...'` inside non-raw TEMPLATE string produced literal newline in generated file | Replaced regex with line-split loop |
| `{{}}` escaping complexity in SERVER_PY | SERVER_PY was inside TEMPLATE requiring double-brace escaping on every dict | Moved `SERVER_PY_CONTENT` outside TEMPLATE as raw string; passed as format arg |
| `FORGE_VERSION` undefined in server | Defined in CLI context, not available to server subprocess | Passed as `FORGE_VERSION` env var from `cmd_dashboard` |
| Dev symlink overwritten by upgrade | `cmd_init` writes static file, breaking the `src/dashboard.html` symlink | `cmd_dev()` re-establishes symlink after init |

---

## Design Decisions

**Why a God Script?** Single distributable artifact. `forge` binary is self-contained — copy one file to any machine with Python 3 and it works. No pip, no venv, no package.json.

**Why `str.format()` not a real template engine?** Zero-dependency constraint. `str.format()` with `{{}}` escaping is sufficient and ships with Python.

**Why `src/dashboard.html` as a separate file?** The dashboard grew large enough that editing it inside a Python string was impractical (no syntax highlighting, constant `{{}}` escaping mistakes). It is read at build time via `open()` and embedded verbatim.

**Why background threads for generation/build?** The HTTP server is single-threaded. Long-running subprocess calls (AI generation, git push) would block all polling. Daemon threads allow the server to keep responding to `/api/state` polls every 3 seconds.

**Why line-scan for gate status, not regex?** Regex containing `\n` inside a Python non-raw TEMPLATE string gets `\n` interpreted at string-parse time, producing a broken newline in the generated `server.py`. Line-scan avoids any special characters.

**Why truncate on reset instead of delete?** Preserving empty files means the file tree remains consistent with what `./forge init` created. The dashboard shows "Not started" for 0-byte files without needing re-init.

---

## Environment Variables (server.py)

| Variable | Set by | Purpose |
|---|---|---|
| `AEOS_REPO_ROOT` | `cmd_dashboard` | Absolute path to the project root (parent of `.forge/`) |
| `FORGE_VERSION` | `cmd_dashboard` | Version string shown in `/api/state` and dashboard |
| `FORGE_SCRIPT` | `cmd_dashboard` | Absolute path to the `forge` binary (for subprocess generation) |

---

## Current Version Changelog

### v0.2.0
- Extracted `SERVER_PY_CONTENT` outside `TEMPLATE` (eliminated `{{}}` escaping in server code)
- Extracted `src/dashboard.html` as separate editable file; embedded at build time
- Full 8-view lifecycle dashboard: Overview, Input, Generate, Review, Build, Deploy, Issues, Settings
- New API endpoints: `/api/raw-input`, `/api/generate`, `/api/build`, `/api/issue`, `/api/settings`, `/api/reset`
- Dynamic phase computation from file state
- `00-raw-input/` directory and `project-state.json` created on init
- `FORGE_VERSION` env var threading (CLI → server → dashboard)
- `./forge upgrade` and `./forge version` commands
- `./forge --project <path>` multi-project support
- Production SVG icon system (Heroicons 2.0 outline); all emoji removed
- Danger Zone: pipeline reset with typed confirmation dialog
- Product name field in Settings; reflected in topbar and Overview
- Gate status computed from review coverage (not manual toggle)
- Fixed false PASSED gates, false amber on empty files, AEOS branding remnants

### v0.1.0
- Initial agent framework and task orchestration templates
- 11-stage pipeline scaffolding
- Basic CLI: `init`, `generate`, `pipeline`, `dashboard`
- `runs/status.json` polling
- Gate files and `reviews.json`
