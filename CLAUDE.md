Project: Forge Engineering OS (AEOS)
Mission
Forge is a documentation-first PDLC automation framework. It uses AI agents to generate structured Markdown artifacts across 11 stages (Context -> Marketing), treating documentation as executable state.

Core Development Rules
The "God Script": All primary logic (CLI template, Agent personas, Dashboard HTML/CSS/JS, Runner scripts) resides in src/build_forge.py.
Single Source of Truth: To change any runtime behavior in the .forge/ directory, you MUST edit src/build_forge.py and then run python3 src/build_forge.py && ./forge init.
Zero Dependencies: Maintain the zero-dependency architecture (Python standard library only).
Directory Structure
src/build_forge.py: The master build script.
forge: The generated CLI executable.
.forge/: The live OS environment (git-ignored usually, but contains the state).
00-context/ to 10-marketing/: Stage artifacts.
11-agents/: Agent persona definitions.
12-gates/: Pipeline checkpoints.
scripts/: Embedded runtime (run.py, stage_runner.py, server.py).
runs/status.json: Live execution state for the dashboard.
Key Workflows for AI Developers
Adding a New File to a Stage:
Update the STAGE_OUTPUT_FILES dictionary in src/build_forge.py.
Rebuild and re-init.
Refining Agent Personas:
Edit the relevant key in the AGENTS dictionary in src/build_forge.py.
Modifying the Dashboard:
Edit DASHBOARD_HTML_CONTENT or SERVER_PY in src/build_forge.py.
Note: CSS/JS braces must be escaped as {{ and }} inside the Python TEMPLATE string if they are part of a .format() call.
CLI Usage
./forge init: Fresh setup of the environment.
./forge generate <stage> [input-file]: Runs the agent pipeline for a stage.
./forge dashboard [port]: Starts the management UI (default 8080).
Dashboard Integration
The dashboard communicates via a JSON API provided by server.py:

/api/state: Returns the file tree, gate statuses, and live processing info.
/api/file?path=...: Retrieves file content.
/api/gate: Toggles gate status.
/api/fix: Triggers a targeted agent run with a user critique.
