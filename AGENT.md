# AGENT.md - Forge Orchestrator Handover Guide

## Current Mental Model

This repository is the Forge root orchestrator. It is not just a library installed inside one project anymore.

Forge now has three layers:

- Root orchestrator: source code, compiler, dashboard source, and the built `forge` executable.
- Managed projects: generated/controlled projects under `.projects/<project-slug>`.
- Validation projects: external test beds such as `test-projects/saas-todo`.

The root `forge` executable is still the user-facing artifact, but the source is no longer a single dashboard blob. The maintainable source layout is modular:

- `src/build_forge.py`: compiler, stage metadata, agent contracts, gate contracts, compatibility assembly.
- `src/runtime/forge_cli.py.tmpl`: CLI template used to build `forge`.
- `src/runtime/server.py`: generated dashboard API server copied into `.forge/scripts/server.py`.
- `src/runtime/build_runner.py`: build-system runner copied into `.forge/scripts/build_runner.py`.
- `src/dashboard/index.html`: dashboard HTML shell.
- `src/dashboard/styles.css`: dashboard styling source.
- `src/dashboard/scripts/*.js`: ordered dashboard client behavior.
- `src/dashboard/scripts.txt`: script assembly order.
- `src/dashboard/DESIGN.md`: current dashboard design contract.
- `src/dashboard.html`: generated compatibility snapshot. Do not hand-edit this as source.

Practical rule:

- Edit `src/*` source files.
- Run `python3 src/build_forge.py`.
- Run `./forge upgrade` for the root runtime.
- Run `./forge --project <project-path> upgrade` for each managed/test project that must receive the updated runtime.

## Source Of Truth Rules

Runtime truth wins over docs.

Priority order:

1. Current source under `src/`.
2. Built `./forge` behavior.
3. Generated runtime under `.forge/scripts/*` and `<project>/.forge/scripts/*`.
4. Actual project state under `.forge/` and `.projects/index.json`.
5. Documentation such as `CLAUDE.md`.

Do not manually edit generated runtime files and expect persistence. The next `upgrade` overwrites them.

## Command Playbook

Run from repo root unless stated otherwise.

Build root executable:

```bash
python3 src/build_forge.py
```

Upgrade root runtime:

```bash
./forge upgrade
```

Upgrade a managed project:

```bash
./forge --project "$PWD/.projects/task-flow" upgrade
```

Upgrade validation project:

```bash
./forge --project "$PWD/test-projects/saas-todo" upgrade
```

Run dashboard from root orchestrator:

```bash
./forge dashboard 8080
```

Run dashboard from a specific project:

```bash
./forge --project "$PWD/.projects/task-flow" dashboard 8080
```

Restart current dashboard server:

```bash
screen -S forge-dashboard -X quit >/dev/null 2>&1 || true
lsof -tiTCP:8080 -sTCP:LISTEN | xargs -r kill
screen -dmS forge-dashboard ./forge dashboard 8080
curl -sS -o /tmp/forge-dashboard.html -w '%{http_code} %{size_download}\n' http://127.0.0.1:8080/
```

Verify command surface:

```bash
./forge version
./forge
```

Current command surface:

- `version`
- `init`
- `upgrade`
- `generate [stage]`
- `pipeline`
- `dashboard [port]`
- `dev [port]`

Notes:

- `--project <path>` is accepted before the command.
- `./forge --help` is not the primary help path; `./forge` with no command prints usage.

## Project Workspace Model

The dashboard is now project-first.

Root-level managed project state lives under:

- `.projects/index.json`: project registry, active project, archive status.
- `.projects/<slug>/.forge/`: per-project runtime state.

Project lifecycle APIs:

- `GET /api/projects`: list active/archived projects and active selection.
- `POST /api/projects`: create a managed project under `.projects/<slug>`.
- `POST /api/projects/select`: switch active project.
- `POST /api/projects/archive`: archive a project.
- `POST /api/projects/restore`: restore an archived project.
- `DELETE /api/projects`: permanently delete archived project only.

Design decision:

- Archive first, delete only after archive. This avoids accidental destructive deletes from the main active-project surface.
- `.projects/` is gitignored because it contains generated project state, runtime files, and potentially sensitive configuration.

Current known managed projects:

- `.projects/task-flow`: active project used heavily during dashboard validation.
- `.projects/test`: accidental/lightweight test project from UI interaction. Do not delete unless the user asks.
- `.projects/demo-project`: existing managed project if present in the registry.

## Dashboard Architecture

The dashboard has a project landing page plus 8 operational views:

- Projects: create, select, archive, restore, delete managed projects.
- Overview: lifecycle summary and next action.
- Input: raw markdown input files.
- Generate: stage and all-stage generation.
- Review: file tree, rendered/raw viewer, critique/regenerate, gates and versions.
- Build: build-system generation, review, git branch/commit/push/PR flow.
- Deploy: environment cards and GitHub secret/variable status.
- Issues: lightweight issue tracker.
- Settings: product, AI runtime, git, environments, danger zone.

Primary API map:

- `GET /api/state`
- `GET/POST/DELETE /api/raw-input`
- `POST /api/generate`
- `POST /api/review`
- `POST /api/fix`
- `POST /api/build`
- `GET/POST /api/build-system`
- `GET /api/build-file`
- `GET/POST /api/build-review`
- `GET/POST /api/secrets`
- `GET/POST /api/versions`, `GET /api/version`, `POST /api/version/restore`
- `POST /api/settings`
- `POST /api/issue`
- `POST /api/reset`
- `GET /api/tools`
- `GET /api/pr-status`

## Current Design System State

The dashboard has been through multiple design-system trials. The final active source is Revolut-inspired and lives in:

- `src/dashboard/DESIGN.md`
- `src/dashboard/styles.css`

Final design direction:

- True black root/project surface.
- White operational dashboard surfaces.
- Cobalt violet `#494fdf` as scarce brand accent.
- Pill buttons and tabs.
- 20px cards, 12px inputs.
- Aeonik-style display stack with Inter fallback.
- No decorative shadows as a core pattern.

Important lesson:

- Treat DESIGN.md as a design contract, not a direct paste-to-runtime implementation. Some marketing-site rules need dashboard adaptation for control density, readable contrast, and accessible hit areas.

## Validation Workflow

Minimum validation after dashboard/source changes:

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

Browser sanity checks must cover:

- Projects page.
- Overview.
- Input.
- Generate.
- Review.
- Build.
- Deploy.
- Issues.
- Settings.

Known acceptable scan finding:

- Project absolute paths are intentionally ellipsized. Do not treat path `scrollWidth > clientWidth` as a bug when `overflow: hidden; text-overflow: ellipsis` is expected.

## Failure Log And Takeaways

Server not reachable:

- Symptom: browser showed site cannot be reached.
- Common causes: server not running, wrong project target, stale process on port 8080, generated runtime not upgraded after source changes.
- Fix pattern: rebuild, upgrade, kill port listener, restart in `screen`, verify with `curl`.

Stale generated dashboard:

- Symptom: browser showed old dropdown/project prompt behavior after source edits.
- Root cause: editing source without regenerating `src/dashboard.html` and `.forge/scripts/dashboard.html`.
- Fix: edit `src/dashboard/*`, run `python3 src/build_forge.py`, then `./forge upgrade` and project upgrades.

Blank page after design experiment:

- Symptom: HTTP returned 200 but browser rendered blank/loading.
- Root cause: design experiment introduced layout/runtime instability while generated browser tab was stale/hung.
- Fix: revert to known-good source, rebuild, upgrade, restart server, open a fresh browser tab.

Review panel overflow:

- Symptom: `Regenerate with critique` button clipped in the Review side panel.
- Root cause: fixed-width side panel plus global button `white-space: nowrap` and uppercase letter spacing.
- Fix: widen review panel, allow controlled button sizing, ellipsize filenames/metadata, and re-run layout scan.

Design system direct translation risk:

- Symptom: Package Tracking trial created poor dashboard behavior and contrast issues.
- Root cause: marketing/onboarding design contract was applied too literally to a dense production dashboard.
- Fix: adapt design tokens to dashboard function; preserve control readability and density.

Chrome/browser automation instability:

- Symptom: active user tab changed or hung during verification.
- Fix: use a fresh tab or headless Chrome sanity script for repeatable checks; do not fight the user's active browser state.

Worktree config issue:

- Symptom: Git tooling error: `core.repositoryformatversion does not support extension: worktreeconfig`.
- Takeaway: Codex worktrees may surface per-worktree Git config compatibility issues. Disable only if you know no per-worktree config is required; otherwise prefer operating in the main repo when possible.

## Success Log

Completed and currently working:

- Modular source layout split from monolithic dashboard/server editing.
- Root `forge` rebuild from source modules.
- Project-first dashboard with create/select/archive/restore/delete lifecycle.
- `.projects/` gitignored for managed runtime projects.
- Runtime project APIs added and verified.
- Dashboard server restart flow stabilized with `screen` and port cleanup.
- Multiple generated runtime targets upgraded successfully.
- Revolut-inspired final dashboard skin applied.
- UI sanity scan across all major views passes, with only intentional project-path ellipsis remaining.

## Security And Hygiene

Non-negotiable:

- Treat `.forge/project-state.json` as sensitive operational state.
- Do not expose or commit git tokens, AI keys, environment secrets, or generated secret values.
- `.projects/` can contain project state and must remain gitignored.
- Prefer `secrets_configured` metadata over storing secret values.
- When sharing logs or docs, redact repository auth values and environment credentials.

Current risk:

- Existing project-state files may contain plaintext values from earlier testing. Inspect before sharing or committing any state artifact.

## Handover Checklist

At takeover, run:

```bash
pwd
git status --short
./forge version
./forge
python3 src/build_forge.py
curl -sS http://127.0.0.1:8080/ >/dev/null || true
```

Then inspect:

- `src/README.md`
- `src/build_forge.py`
- `src/runtime/server.py`
- `src/runtime/forge_cli.py.tmpl`
- `src/dashboard/DESIGN.md`
- `src/dashboard/styles.css`
- `.projects/index.json`
- `.projects/task-flow/.forge/project-state.json` only after considering secret hygiene.

Decision rule:

- If docs and runtime disagree, trust runtime, update docs, and record the drift.
