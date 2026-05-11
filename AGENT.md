# AGENT.md — Forge Orchestrator Handover Guide

## System Mental Model
- This repository is the Forge root orchestrator.
- `forge` is the built executable script that users run.
- `src/build_forge.py` is the builder source that generates `forge`.
- `src/dashboard.html` is the dashboard UI source embedded into runtime.
- `test-projects/*` are consumer/generated projects used to validate orchestrator behavior.
- In each target project, `.forge/` is runtime state and generated control-plane data.

Practical rule:
- Edit orchestrator behavior in root sources, then rebuild `forge`.
- Do not manually edit generated files in a test project unless doing diagnostics.

## Source Of Truth Rules
- Primary runtime truth: `forge` script behavior and generated `.forge/scripts/server.py`.
- Secondary truth: actual state files in target project `.forge/`.
- Reference docs: `CLAUDE.md` is helpful but can drift.

Conflict policy:
- If `CLAUDE.md` and runtime disagree, trust runtime and record the drift.

## Command Playbook
Run from repo root unless noted.

Core lifecycle:
```bash
python3 src/build_forge.py
./forge --project test-projects/saas-todo init
./forge --project test-projects/saas-todo upgrade
./forge --project test-projects/saas-todo generate context
./forge --project test-projects/saas-todo pipeline
./forge --project test-projects/saas-todo dashboard 8080
./forge dev 8080
./forge version
```

Command surface (runtime-verified):
- `version`
- `init`
- `upgrade`
- `generate [stage]`
- `pipeline`
- `dashboard [port]`
- `dev [port]`

Notes:
- Use `--project <path>` to target a specific generated project.
- `./forge` with no command prints usage.
- `./forge --help` is not a supported command.

## Dashboard And API Map
The dashboard has 8 views: Overview, Input, Generate, Review, Build, Deploy, Issues, Settings.

Operational endpoints used in runtime:
- `GET /api/state`: aggregate project state, phase, stage summaries, build status.
- `GET/POST/DELETE /api/raw-input`: manage raw input markdown files.
- `POST /api/generate`: run one stage or all stages.
- `POST /api/review`: mark file reviewed/needs_review and synchronize gate statuses.
- `POST /api/fix`: targeted regeneration using critique.
- `POST /api/build`: branch/commit/push/PR automation for generated output.
- `POST /api/settings`: persist project/tool/git/environment settings.
- `POST /api/issue`: create or update tracked issues.
- `POST /api/reset`: clear generated/review state and reset gates.
- `GET /api/build-system`, `POST /api/build-system`: build-system status and step execution.
- `GET /api/build-file`: fetch generated build artifact file content.
- `GET/POST /api/build-review`: pre-push review lifecycle.
- `GET/POST /api/secrets`: secret requirements and secret value updates.
- `GET /api/tools`, `GET /api/versions`, `GET /api/version`, `POST /api/version/restore`, `GET /api/pr-status`.

Key state files to inspect in target project:
- `.forge/project-state.json`
- `.forge/reviews.json`
- `.forge/runs/status.json`
- `.forge/runs/build-system.json`
- `.forge/runs/build-review.json` (when build-review flow is active)

## Test-Project Workflow (`test-projects/saas-todo`)
Purpose:
- Validate orchestrator flows end to end.
- Validate generated artifact layout under `.forge/15-build/*` and copied project directories (`backend`, `frontend`, `integration`, `tests`, `infra`).

Safe workflow:
1. Rebuild root `forge` after source changes.
2. Run `./forge --project test-projects/saas-todo upgrade`.
3. Start dashboard for that project.
4. Verify `/api/state` and build-system statuses reflect expected changes.
5. Validate generated output directories without rewriting root orchestrator sources.

Do not:
- Treat test-project committed artifacts as orchestrator source-of-truth.
- Modify generated `.forge/scripts/*` manually and assume persistence.

## Drift Register (Current)
Observed drift between `CLAUDE.md` and runtime:
- `CLAUDE.md` focuses on the 11-stage documentation pipeline; runtime additionally supports build-system and code-generation flows via `.forge/15-build/*`.
- Runtime endpoint surface is broader than the documented list (for example `build-system`, `build-file`, `build-review`, `secrets`, version endpoints, PR status).
- Runtime build lifecycle includes copying generated code into project directories and PR automation.

Operational impact:
- Agents relying only on `CLAUDE.md` will miss active production paths.
- Always verify against runtime before changing workflow assumptions.

## Security And Hygiene
Non-negotiable:
- Treat `.forge/project-state.json` as sensitive operational state.
- Never expose or copy tokens/secrets into docs, commits, logs, issues, or chat outputs.
- When sharing diagnostics, redact credentials and repository auth values.
- Do not commit plaintext secrets in orchestrator repo or test projects.

Current risk to address:
- Existing test project state may include plaintext credentials in persisted JSON.
- Any handoff or support workflow must sanitize before sharing artifacts.

## Handover Checklist
Run this sequence at start of any takeover:
1. Confirm runtime command surface with `./forge` and `./forge version`.
2. Inspect builder sources: `src/build_forge.py` and `src/dashboard.html`.
3. Inspect generated runtime in target project: `.forge/scripts/server.py`.
4. Compare expected vs actual API endpoints and build flows.
5. Check `.forge/project-state.json` for secret hygiene before any sharing.
6. Record any doc/runtime drift before implementation.
7. Apply `Runtime > Docs` rule for all execution decisions.

## Boundaries
- This file is an operator guide for incoming agents.
- It is not a replacement for detailed product docs or architecture specs.
- Keep `CLAUDE.md` unchanged; use it as context, not runtime authority.
