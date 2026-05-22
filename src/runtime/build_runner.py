#!/usr/bin/env python3
'''Build system runner - generates production-grade code from reviewed spec documents.
Two-pass strategy: backend generates API contract first, then frontend/integration consume it.
Usage: python3 scripts/build_runner.py <step>
'''
import os, sys, json, subprocess, tempfile
from datetime import datetime
from constants import (
    BUILD_STEP_DIRS,
    DIR_AGENTS,
    DIR_BUILD,
    FILE_API_CONTRACT,
    FILE_BUILD_SYSTEM,
    FILE_ENCODING,
    FORGE_PHASE_ID_ENV,
    FORGE_PHASE_NAME_ENV,
    GEMINI_ARG_MODEL,
    GEMINI_ARG_PROMPT,
    GEMINI_ARG_SKIP_TRUST,
    CLAUDE_ARG_PROMPT,
    CLAUDE_ARG_OUTPUT_FORMAT,
    CLAUDE_OUTPUT_TEXT,
    GENERATE_TIMEOUT_SECS,
    MARKDOWN_EXTENSION,
    SOURCE_MARKER,
    SOURCE_MARKER_END,
    STATUS_COMPLETE,
    STATUS_ERROR,
    STATUS_RUNNING,
    TOOL_CLAUDE,
    TOOL_GEMINI,
    DEFAULT_TOOL,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get("FORGE_REPO_ROOT", os.path.dirname(os.path.dirname(SCRIPT_DIR)))
_forge_data = os.environ.get("FORGE_DATA_DIR")
FORGE_DIR = os.path.expanduser(_forge_data) if _forge_data else os.path.dirname(SCRIPT_DIR)
BUILD_STATUS_FILE = os.path.join(FORGE_DIR, FILE_BUILD_SYSTEM)

# Phase context — set by server when a phase is active
ACTIVE_PHASE_ID   = os.environ.get(FORGE_PHASE_ID_ENV, "").strip()
ACTIVE_PHASE_NAME = os.environ.get(FORGE_PHASE_NAME_ENV, "").strip()

# Phase-scoped api-contract path: 15-build/<phase-id>/api-contract.md or global fallback
API_CONTRACT_FILE = os.path.join(
    FORGE_DIR,
    DIR_BUILD, ACTIVE_PHASE_ID, "api-contract.md"
) if ACTIVE_PHASE_ID else os.path.join(FORGE_DIR, FILE_API_CONTRACT)

# Build order matters: backend must run before frontend/integration/tests
STEPS = {}  # __FORGE_BUILD_STEPS__

_LOG_PREFIX = "[BUILD]"


def load_build_status():
    if os.path.exists(BUILD_STATUS_FILE):
        try:
            with open(BUILD_STATUS_FILE, encoding=FILE_ENCODING) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_step_status(step, status_val, files=None, error=None):
    status = load_build_status()
    existing = status.get(step, {})
    status[step] = {
        "status": status_val,
        "files": files if files is not None else existing.get("files", []),
        "generated_at": datetime.now().isoformat() if status_val == STATUS_COMPLETE else existing.get("generated_at", ""),
        "error": error,
        "phase_id": ACTIVE_PHASE_ID or None,
    }
    with open(BUILD_STATUS_FILE, "w", encoding=FILE_ENCODING) as f:
        json.dump(status, f, indent=2)

def collect_docs(meta):
    docs = []
    for dir_name in meta.get("source_dirs", []):
        dir_path = os.path.join(FORGE_DIR, dir_name)
        if os.path.isdir(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.endswith(MARKDOWN_EXTENSION):
                    fpath = os.path.join(dir_path, fname)
                    if os.path.getsize(fpath) > 0:
                        with open(fpath, encoding=FILE_ENCODING) as f:
                            content = f.read()
                        docs.append(SOURCE_MARKER + dir_name + "/" + fname + SOURCE_MARKER_END + "\n" + content)
    for rel_file in meta.get("source_files", []):
        fpath = os.path.join(FORGE_DIR, rel_file)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            with open(fpath, encoding=FILE_ENCODING) as f:
                content = f.read()
            docs.append(SOURCE_MARKER + rel_file + SOURCE_MARKER_END + "\n" + content)
    return "\n\n".join(docs)

def load_api_contract():
    if os.path.exists(API_CONTRACT_FILE) and os.path.getsize(API_CONTRACT_FILE) > 0:
        with open(API_CONTRACT_FILE, encoding=FILE_ENCODING) as f:
            return f.read()
    return ""

def load_agent(agent_name):
    path = os.path.join(FORGE_DIR, DIR_AGENTS, agent_name + MARKDOWN_EXTENSION)
    if os.path.exists(path):
        with open(path, encoding=FILE_ENCODING) as f:
            return f.read()
    return "# Agent: " + agent_name + "\nGenerate code based on the provided specifications."

def invoke_ai(prompt, tool, model_id):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding=FILE_ENCODING) as tmp:
        tmp_path = tmp.name
    try:
        if tool == TOOL_GEMINI:
            cmd = [TOOL_GEMINI, GEMINI_ARG_SKIP_TRUST]
            if model_id:
                cmd += [GEMINI_ARG_MODEL, model_id]
            cmd += [GEMINI_ARG_PROMPT, prompt]
        elif tool == TOOL_CLAUDE:
            cmd = [TOOL_CLAUDE, CLAUDE_ARG_PROMPT, prompt, CLAUDE_ARG_OUTPUT_FORMAT, CLAUDE_OUTPUT_TEXT]
        else:
            cmd = [TOOL_GEMINI, GEMINI_ARG_SKIP_TRUST, GEMINI_ARG_PROMPT, prompt]
        with open(tmp_path, "w", encoding=FILE_ENCODING) as out_f:
            result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, timeout=GENERATE_TIMEOUT_SECS)
        if result.returncode != 0:
            err = result.stderr.decode(FILE_ENCODING, errors="replace") if result.stderr else "AI call failed"
            return None, err
        with open(tmp_path, encoding=FILE_ENCODING) as f:
            return f.read(), None
    except subprocess.TimeoutExpired:
        return None, "AI call timed out after 10 minutes"
    except FileNotFoundError:
        return None, "AI tool '" + tool + "' not found in PATH"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def sanitize_path(candidate):
    p = candidate.strip()
    if " (" in p or p.endswith(")"):
        return None
    parts = p.replace("\\", "/").split("/")
    if parts and parts[0] == DIR_BUILD:
        parts = parts[2:]
    if parts and parts[0] == ".forge":
        parts = parts[1:]
    parts = [p2 for p2 in parts if p2 and p2 != ".."]
    if not parts:
        return None
    return "/".join(parts)

def parse_files(output_text):
    files = {}
    current_path = None
    current_lines = []
    for line in output_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("=== ") and stripped.endswith(" ==="):
            if current_path and not current_path.startswith("SOURCE:"):
                files[current_path] = "\n".join(current_lines).strip()
            candidate = stripped[4:-4].strip()
            if candidate.startswith("SOURCE:"):
                current_path = None
                current_lines = []
            else:
                clean = sanitize_path(candidate)
                current_path = clean
                current_lines = []
        elif current_path:
            current_lines.append(line)
    if current_path and not current_path.startswith("SOURCE:"):
        files[current_path] = "\n".join(current_lines).strip()
    return files

# -----------------------------------------------------------------------
# Spec-enforcing prompt builders — one per step
# -----------------------------------------------------------------------

COMMON_FORMAT_RULE = (
    "OUTPUT FORMAT — MANDATORY:\n"
    "Output ONLY file blocks in this exact format, no prose before or after:\n"
    "=== path/to/file.ext ===\n"
    "<complete file content>\n\n"
    "Every file must be complete and immediately runnable. "
    "No truncation, no '# ... rest of file', no TODO stubs.\n"
)

_SECTION_DIVIDER = "=" * 60

def _section(label):
    return _SECTION_DIVIDER + "\n" + label + "\n" + _SECTION_DIVIDER


def _contract_block(api_contract, header):
    if api_contract:
        return _section(header) + "\n" + api_contract + "\n"
    return ""


def _phase_context_block():
    if not ACTIVE_PHASE_NAME:
        return ""
    return (
        _section("PHASE SCOPE — CRITICAL: BUILD ONLY THIS PHASE") + "\n"
        "You are generating code for ONE specific delivery phase of a multi-phase product.\n\n"
        f"  Phase: {ACTIVE_PHASE_NAME}\n\n"
        "RULES:\n"
        "1. Implement ONLY the features, endpoints, and UI screens that belong to this phase.\n"
        "2. Do NOT implement features described in later phases — leave clear extension points instead.\n"
        "3. The code you produce must be shippable as a standalone increment for this phase.\n"
        "4. If a feature is ambiguous, scope it to the minimum needed for this phase only.\n"
    )


def build_backend_prompt(persona, docs):
    parts = [persona]
    if _phase_context_block():
        parts.append(_phase_context_block())
    parts += [
        _section("SPEC COMPLIANCE RULES — NON-NEGOTIABLE"),
        (
            "1. TECH STACK: Read the architecture documents below. Identify every technology, "
            "framework, database, and service named. Use EXACTLY those — no substitutions.\n"
            "   - If the spec says Supabase: use the supabase-py client, NOT SQLAlchemy ORM.\n"
            "   - If the spec says PostgreSQL via Supabase: use Supabase's database client.\n"
            "   - If the spec says FastAPI: use FastAPI with async handlers.\n"
            "   - If the spec says JWT auth: implement it exactly as described.\n"
            "   Never default to SQLite, in-memory stores, or generic ORMs when the spec names something specific.\n\n"
            "2. COMPLETENESS: Every endpoint listed in the engineering spec must be implemented in full. "
            "No stubs. No placeholder return values. Real business logic, real DB calls, real error handling.\n\n"
            "3. FIRST FILE IS api-contract.md — REQUIRED:\n"
            "   Your very first output block must be:\n"
            "   === api-contract.md ===\n"
            "   This file documents every endpoint so the frontend agent can connect to it. Include:\n"
            "   - Base URL (e.g. http://localhost:8000/api/v1)\n"
            "   - Auth mechanism (Supabase JWT Bearer, session cookie, etc.)\n"
            "   - Every endpoint: METHOD, path, auth required (yes/no), request body schema, response schema\n"
            "   - Supabase table names and Row Level Security policies if applicable\n"
            "   - All environment variables (name, description, example value)\n\n"
            "4. ENVIRONMENT VARIABLES: All credentials and config must come from env vars. "
            "Generate .env.example with every variable the app needs.\n\n"
            "5. SUPABASE SPECIFICS (if spec uses Supabase):\n"
            "   - Use supabase-py for all DB operations\n"
            "   - Implement Row Level Security policies in a migration file\n"
            "   - Use Supabase Auth for authentication (verify JWTs using Supabase's JWKS)\n"
            "   - Generate supabase/migrations/ SQL files for schema\n\n"
            "6. PRODUCTION QUALITY: Include proper error handling, input validation (Pydantic models), "
            "logging, CORS config, health check endpoint, and graceful startup/shutdown."
        ),
        COMMON_FORMAT_RULE,
        _section("SPECIFICATION DOCUMENTS (your source of truth — follow these exactly)"),
        docs,
    ]
    return "\n\n".join(parts)

def build_frontend_prompt(persona, docs, api_contract):
    contract_block = (
        _contract_block(api_contract, "BACKEND API CONTRACT — CONNECT TO THESE EXACT ENDPOINTS")
        if api_contract else
        "WARNING: Backend API contract not yet generated. "
        "Infer endpoints from the engineering spec documents.\n"
    )
    parts = [persona]
    if _phase_context_block():
        parts.append(_phase_context_block())
    parts += [
        _section("SPEC COMPLIANCE RULES — NON-NEGOTIABLE"),
        (
            "1. TECH STACK: Read the design and architecture documents below. Use EXACTLY the "
            "framework, component library, and styling system named — no substitutions.\n"
            "   - If spec says React + TypeScript: use React with strict TypeScript, no JS files.\n"
            "   - If spec says Next.js: use Next.js App Router or Pages as specified.\n"
            "   - If spec says Tailwind CSS: use Tailwind utility classes, not custom CSS.\n"
            "   - If spec says Supabase Auth: use @supabase/supabase-js for auth on the frontend.\n\n"
            "2. REAL API INTEGRATION — MANDATORY:\n"
            "   Every data fetch, mutation, and auth call MUST use the actual backend endpoints "
            "from the API contract above. NO mock data. NO hardcoded arrays. NO placeholder fetch calls.\n"
            "   - Create a typed API client (e.g. src/lib/api.ts) that wraps all endpoint calls.\n"
            "   - Use the exact request/response shapes from the contract.\n"
            "   - Handle loading, error, and empty states for every async operation.\n\n"
            "3. AUTH WIRING: If the backend uses Supabase Auth, implement the full auth flow:\n"
            "   - Sign in / sign up / sign out using @supabase/supabase-js\n"
            "   - Protected routes that redirect unauthenticated users\n"
            "   - Pass the Supabase session JWT as Bearer token to backend API calls\n\n"
            "4. ENVIRONMENT VARIABLES: Use the correct prefix for your framework:\n"
            "   - Vite: VITE_API_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY\n"
            "   - Next.js: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, etc.\n"
            "   Generate .env.example with all required variables.\n\n"
            "5. EVERY SCREEN FROM THE DESIGN SPEC must be implemented — no missing pages.\n\n"
            "6. PRODUCTION QUALITY: TypeScript strict mode, proper error boundaries, "
            "loading skeletons, form validation, accessible markup (ARIA where needed).\n\n"
            "7. tsconfig.json EXACT VALUES — use only these strings, no variations:\n"
            "   - moduleResolution: must be one of: 'node10', 'node16', 'nodenext', 'bundler'\n"
            "     For Next.js 14+: use 'bundler'. NOT 'bundle', NOT 'node', NOT 'NodeNext' (case matters).\n"
            "   - module: 'esnext' for Next.js App Router\n"
            "   - Do NOT include 'noImplicitReturns', 'noUnusedLocals', or other options not supported\n"
            "     by your Next.js version — they cause build failures.\n\n"
            "8. Dockerfile and next.config.js MUST be consistent:\n"
            "   - Always set `output: 'standalone'` in next.config.js for Docker builds.\n"
            "   - The Dockerfile runner stage MUST copy from `.next/standalone` — this only works\n"
            "     when `output: 'standalone'` is set. If you omit it, the runner has nothing to copy.\n"
            "   - Use `npm install --no-audit --no-fund` NOT `npm ci`. Copy only `package.json`.\n\n"
            "9. ROUTING PARADIGM — PICK ONE, NEVER MIX:\n"
            "   - Next.js App Router: use ONLY `src/app/`. NEVER generate `src/pages/`.\n"
            "   - Next.js Pages Router: use ONLY `src/pages/`. NEVER generate `src/app/`.\n"
            "   - NEVER import `react-router-dom` in a Next.js project. Next.js has its own router.\n"
            "   - Check `package.json`: if `next` is a dependency, you are in Next.js — no React Router.\n\n"
            "10. CASE-SENSITIVE IMPORTS — DOCKER LINUX FILESYSTEM IS CASE-SENSITIVE:\n"
            "    All component directory names MUST be lowercase: `components/layout/`, `components/ui/`,\n"
            "    `components/editor/`, `components/canvas/`, `components/shared/`.\n"
            "    Every import path must EXACTLY match the generated filename including case.\n"
            "    Rule: if you generate `components/ui/button.tsx`, import it as `@/components/ui/button`.\n"
            "    Never mix `Button` and `button` in the same path — pick lowercase and be consistent.\n\n"
            "11. IMPORT COMPLETENESS — EVERY IMPORT MUST RESOLVE:\n"
            "    Before finalising output, mentally walk every `import` statement:\n"
            "    - Is the imported file being generated in this output? If not, remove the import.\n"
            "    - Is the imported npm package listed in package.json? If not, add it.\n"
            "    - Are all named exports (`{ Button }`, `{ AppShell }`) actually exported by that file?\n"
            "    A build that compiles is the minimum bar. Missing imports are build failures."
        ),
        COMMON_FORMAT_RULE,
        contract_block,
        _section("SPECIFICATION DOCUMENTS"),
        docs,
    ]
    return "\n\n".join(parts)

def build_integration_prompt(persona, docs, api_contract):
    contract_block = _contract_block(api_contract, "BACKEND API CONTRACT")
    parts = [persona]
    if _phase_context_block():
        parts.append(_phase_context_block())
    parts += [
        _section("SPEC COMPLIANCE RULES — NON-NEGOTIABLE"),
        (
            "1. TECH STACK: Use ONLY the third-party services and SDKs named in the integration spec.\n\n"
            "2. FULL IMPLEMENTATION: Every integration (Stripe, Slack, email, webhooks, etc.) must be "
            "completely implemented using real SDK calls — no stubs, no TODO comments.\n\n"
            "3. ERROR HANDLING: Every external call must have retry logic, timeout handling, "
            "and structured error logging.\n\n"
            "4. CREDENTIALS: All API keys and secrets must come from environment variables. "
            "Generate .env.example entries for every third-party credential.\n\n"
            "5. WEBHOOK SECURITY: Implement signature verification for all inbound webhooks.\n\n"
            "6. PRODUCTION QUALITY: Idempotency keys for payment operations, "
            "dead-letter handling for async jobs, rate limit awareness."
        ),
        COMMON_FORMAT_RULE,
        contract_block,
        _section("SPECIFICATION DOCUMENTS"),
        docs,
    ]
    return "\n\n".join(parts)

def build_tests_prompt(persona, docs, api_contract):
    contract_block = _contract_block(api_contract, "BACKEND API CONTRACT — TEST THESE EXACT ENDPOINTS")
    parts = [persona]
    if _phase_context_block():
        parts.append(_phase_context_block())
    parts += [
        _section("SPEC COMPLIANCE RULES — NON-NEGOTIABLE"),
        (
            "1. TEST FRAMEWORK: Use ONLY the frameworks named in the quality spec "
            "(e.g. pytest for backend, Playwright or Vitest for frontend).\n\n"
            "2. REAL ENDPOINT TESTING: Backend tests must call the actual API endpoints from the "
            "contract above — no mocking the HTTP layer. Use httpx.AsyncClient or similar.\n\n"
            "3. COVERAGE: Every endpoint in the API contract needs:\n"
            "   - Happy path test (valid input, expect 200/201)\n"
            "   - Auth failure test (missing/invalid token, expect 401)\n"
            "   - Validation failure test (bad input, expect 422)\n"
            "   - At least one edge case (empty list, duplicate, not found)\n\n"
            "4. FIXTURES: Generate reusable pytest fixtures or test factories for "
            "creating test users, workspaces, and data.\n\n"
            "5. E2E TESTS: If Playwright is specified, implement full user journey tests "
            "that exercise the real frontend against a real backend.\n\n"
            "6. CI READY: Tests must pass with `pytest` or `npm test` from the repo root. "
            "Include a conftest.py with DB setup/teardown."
        ),
        COMMON_FORMAT_RULE,
        contract_block,
        _section("SPECIFICATION DOCUMENTS"),
        docs,
    ]
    return "\n\n".join(parts)

def _infra_layout_block():
    """Tell the infra agent the exact sibling directory layout so it generates correct paths."""
    # Compute peer step names excluding 'infra' — these become sibling dirs next to infra/
    peers = [s for s in BUILD_ORDER if s != "infra"]
    lines = [
        "CRITICAL — DIRECTORY LAYOUT:",
        "All build steps are generated as SIBLING directories inside the same phase folder:",
        "",
    ]
    for p in peers:
        lines.append(f"  {p}/    ← peer service directory")
    lines += [
        "  infra/  ← YOU are generating files into this directory",
        "",
        "RULES THAT FOLLOW FROM THIS LAYOUT:",
        "",
        "1. docker-compose.yml lives inside infra/ — build contexts must use RELATIVE PARENT paths:",
    ]
    for p in peers:
        lines.append(f"     context: ../{p}   (NOT ./{p} — that would look inside infra/)")
    lines += [
        "",
        "2. Each service's Dockerfile belongs INSIDE THAT SERVICE'S directory, NOT here:",
    ]
    for p in peers:
        lines.append(f"     ../{p}/Dockerfile  ← generate this file as '{p}/Dockerfile' in your output")
    lines += [
        "",
        "3. Output Dockerfiles using the peer directory as the path prefix:",
        "   === backend/Dockerfile ===     (written to ../backend/Dockerfile)",
        "   === frontend/Dockerfile ===    (written to ../frontend/Dockerfile)",
        "",
        "4. The infra/ directory itself contains ONLY orchestration files:",
        "   docker-compose.yml, Makefile, README.md, CI/CD workflows, Terraform, monitoring config.",
        "   No application Dockerfiles belong here.",
        "",
        "5. In every Dockerfile, use `npm install --no-audit --no-fund` NOT `npm ci`.",
        "   Reason: there is no package-lock.json — AI-generated projects do not include lockfiles.",
        "   Also: COPY only `package.json` (not `package*.json`) so Docker never sees a stale lockfile.",
    ]
    return _section("REPOSITORY LAYOUT — READ BEFORE GENERATING ANYTHING") + "\n" + "\n".join(lines)


def build_infra_prompt(persona, docs, api_contract):
    contract_block = _contract_block(api_contract, "API CONTRACT (use to derive all required env vars and service dependencies)")
    parts = [persona]
    if _phase_context_block():
        parts.append(_phase_context_block())
    parts += [
        _infra_layout_block(),
        _section("YOUR MISSION"),
        (
            "Read EVERY specification document below. Identify:\n"
            "  - The deployment platform (Fly.io, Vercel, AWS, Railway, etc.)\n"
            "  - Every third-party service used (Supabase, Stripe, Slack, SendGrid, Redis, etc.)\n"
            "  - Every environment variable required by the backend and frontend\n"
            "  - The test framework and what a test run needs (DB, env vars, etc.)\n\n"
            "Then generate a complete, self-contained infrastructure that automates EVERYTHING "
            "except the initial one-time secret values a human must set in GitHub."
        ),
        _section("MANDATORY OUTPUT FILES"),
        (
            "You MUST generate ALL of the following. Read the docs to fill in the specifics.\n\n"

            "1. `.github/workflows/ci.yml` — Pull Request checks:\n"
            "   - Trigger: on pull_request to main\n"
            "   - Jobs: lint, backend-test, frontend-test, e2e\n"
            "   - backend-test: start Supabase local (supabase start), run migrations, run pytest\n"
            "   - frontend-test: npm ci, npm run type-check, npm test\n"
            "   - e2e: run Playwright against a Supabase branch DB (supabase db branch create)\n"
            "   - All secrets injected from GitHub Secrets — NEVER hardcoded\n\n"

            "2. `.github/workflows/deploy.yml` — Deploy pipeline:\n"
            "   - Trigger: on push to main (deploy staging), on release published (deploy production)\n"
            "   - Steps IN ORDER:\n"
            "     a. Run migrations: `supabase db push --project-ref ${{ secrets.SUPABASE_PROJECT_ID }}`\n"
            "     b. Register/update webhooks for each third-party service found in the docs "
            "(Stripe: `stripe listen --forward-to`, Slack: POST to Slack API to register endpoint, etc.)\n"
            "     c. Build and deploy backend to the deployment platform from the docs\n"
            "     d. Build and deploy frontend to the deployment platform from the docs\n"
            "     e. Run smoke tests against the deployed URL\n\n"

            "3. `secrets-required.md` — The ONLY manual step:\n"
            "   A table of every GitHub Secret that must be set manually by the developer, with:\n"
            "   - Secret name (exact GitHub secret key)\n"
            "   - Where to get the value (e.g. 'Supabase Dashboard → Settings → API')\n"
            "   - Which workflow uses it\n"
            "   - Whether it's required for CI, staging, production, or all\n"
            "   Derive this list from the docs — every service mentioned needs its secrets listed.\n\n"

            "4. `supabase/config.toml` — Supabase CLI project config for local dev and CI.\n\n"

            "5. `docker-compose.yml` — Local development stack:\n"
            "   - Every service the app needs (backend, frontend, redis, etc.)\n"
            "   - Build contexts MUST use ../service paths (e.g. context: ../backend, context: ../frontend)\n"
            "     because this file lives inside infra/ and the service dirs are siblings, not children\n"
            "   - Each service's Dockerfile is at ../service/Dockerfile — reference it as dockerfile: Dockerfile\n"
            "   - Healthchecks on every service\n"
            "   - Volumes for persistence\n"
            "   - .env.local loaded via env_file\n\n"

            "6. `Makefile` — Developer commands:\n"
            "   - `make dev` — start full local stack\n"
            "   - `make migrate` — run Supabase migrations locally\n"
            "   - `make test` — run all tests\n"
            "   - `make e2e` — run Playwright\n"
            "   - `make deploy-staging` — trigger staging deploy\n"
            "   - `make setup` — first-time setup (install deps, copy .env.example, supabase start)\n\n"

            "7. `README.md` — Getting started:\n"
            "   - Prerequisites (Node version, Python version, Supabase CLI, etc.)\n"
            "   - `make setup` to get running locally in < 5 minutes\n"
            "   - Link to secrets-required.md for GitHub configuration"
        ),
        _section("SPEC COMPLIANCE RULES"),
        (
            "1. DEPLOYMENT PLATFORM: Use EXACTLY what the operations/architecture docs specify. "
            "If docs say Fly.io, generate fly.toml. If Vercel, generate vercel.json. "
            "If Railway, generate railway.toml. Never substitute.\n\n"
            "2. THIRD-PARTY SERVICES: Every service mentioned in ANY doc must appear in the CI/CD. "
            "If Stripe is in the integration spec, the deploy workflow must register the Stripe webhook. "
            "If Slack is mentioned, the workflow must configure the Slack app endpoint. "
            "If Supabase Storage is mentioned, the workflow must create the required buckets.\n\n"
            "3. SUPABASE MIGRATIONS: Use Supabase CLI (`supabase db push`) — NOT Alembic — for schema changes. "
            "The migration SQL files already exist in `supabase/migrations/`. Run them in CI.\n\n"
            "4. ENVIRONMENT VARIABLES: Every variable from the API contract and docs must appear "
            "in secrets-required.md AND in the workflow env: blocks. No variable may be missing.\n\n"
            "5. NO PLACEHOLDERS: Every workflow step must be complete and runnable. "
            "No `# TODO`, no `YOUR_VALUE_HERE`, no incomplete steps."
        ),
        COMMON_FORMAT_RULE,
        contract_block,
        _section("SPECIFICATION DOCUMENTS (read all of these to derive the infra)"),
        docs,
    ]
    return "\n\n".join(parts)

def build_prompt_for_step(step, persona, docs, api_contract):
    _prompt_builders = {
        "backend": lambda: build_backend_prompt(persona, docs),
        "frontend": lambda: build_frontend_prompt(persona, docs, api_contract),
        "integration": lambda: build_integration_prompt(persona, docs, api_contract),
        "tests": lambda: build_tests_prompt(persona, docs, api_contract),
        "infra": lambda: build_infra_prompt(persona, docs, api_contract),
    }
    builder = _prompt_builders.get(step)
    if builder:
        return builder()
    return persona + "\n\n---\n\n## Specification Documents\n\n" + docs

# -----------------------------------------------------------------------
# Post-generation fixups
# -----------------------------------------------------------------------

def _normalize_component_dirs(out_dir):
    """Rename PascalCase component subdirectories to lowercase and rewrite imports.

    AI models consistently generate PascalCase component directories (Layout/,
    Editor/, Canvas/) but write lowercase import paths (@/components/layout/).
    Docker Linux builds are case-sensitive unlike macOS — this causes a build
    failure that is invisible locally and only surfaces in the container.

    This fixup is deterministic: it renames every PascalCase dir under any
    `components/` folder to lowercase, then rewrites every .ts/.tsx file in
    the output that references the old casing.
    """
    import re as _re

    # Collect all components/ directories recursively
    for root, dirs, files in os.walk(out_dir):
        if os.path.basename(root) == "components":
            # Lowercase subdirectory names (Layout/ → layout/, etc.)
            for d in list(dirs):
                lower = d.lower()
                if d != lower:
                    old_path = os.path.join(root, d)
                    tmp_path = old_path + "__tmp__"
                    new_path = os.path.join(root, lower)
                    # Two-step rename required on case-insensitive macOS HFS+
                    os.rename(old_path, tmp_path)
                    os.rename(tmp_path, new_path)
            # Don't recurse into node_modules
            dirs[:] = [d for d in dirs if d != "node_modules"]

        # Also lowercase filenames inside ui/ — these are shared primitives with
        # no PascalCase convention (Button.tsx → button.tsx, Input.tsx → input.tsx)
        if os.path.basename(root) in ("ui",) and "components" in root:
            for fname in list(files):
                lower = fname.lower()
                if fname != lower:
                    old_path = os.path.join(root, fname)
                    tmp_path = old_path + "__tmp__"
                    new_path = os.path.join(root, lower)
                    os.rename(old_path, tmp_path)
                    os.rename(tmp_path, new_path)
                    # Fix any internal self-referencing imports in the renamed file
                    try:
                        text = open(new_path, encoding="utf-8").read()
                        fixed = text.replace(fname, lower)
                        if fixed != text:
                            open(new_path, "w", encoding="utf-8").write(fixed)
                    except OSError:
                        pass

    # Now rewrite import paths in all .ts/.tsx source files
    # Match: from '@/components/AnyCase/...' or from "@/components/AnyCase/..."
    _import_re = _re.compile(
        r"(from\s+['\"])(@/components/)([^/'\"]+)(.*?['\"])",
        _re.MULTILINE,
    )

    for root, dirs, files in os.walk(out_dir):
        dirs[:] = [d for d in dirs if d != "node_modules"]
        for fname in files:
            if not fname.endswith((".ts", ".tsx", ".js", ".jsx")):
                continue
            fpath = os.path.join(root, fname)
            try:
                text = open(fpath, encoding="utf-8").read()
                new_text = _import_re.sub(
                    lambda m: m.group(1) + m.group(2) + m.group(3).lower() + m.group(4),
                    text,
                )
                if new_text != text:
                    open(fpath, "w", encoding="utf-8").write(new_text)
            except OSError:
                pass


def _post_generate_fixups(out_dir):
    """Run automatic fixups on generated code after files are written."""
    _normalize_component_dirs(out_dir)


# -----------------------------------------------------------------------
# Step runner
# -----------------------------------------------------------------------

_API_CONTRACT_FILENAME = "api-contract.md"
_STEPS_NEEDING_CONTRACT = ("frontend", "integration", "tests")


def run_step(step):
    meta = STEPS.get(step)
    if not meta:
        print(_LOG_PREFIX + " Unknown step: " + step)
        sys.exit(1)

    print(_LOG_PREFIX + " Running: " + meta["label"])
    save_step_status(step, STATUS_RUNNING)

    docs = collect_docs(meta)
    if not docs.strip():
        msg = "No source documents found. Generate and review the spec docs first."
        save_step_status(step, STATUS_ERROR, error=msg)
        print(_LOG_PREFIX + " " + msg)
        return False

    api_contract = load_api_contract()
    if step in _STEPS_NEEDING_CONTRACT and not api_contract:
        print(_LOG_PREFIX + " WARNING: api-contract.md not found — run backend step first for fully connected output.")

    persona = load_agent(meta["agent"])
    prompt = build_prompt_for_step(step, persona, docs, api_contract)

    tool = os.environ.get("FORGE_TOOL", DEFAULT_TOOL)
    model_id = os.environ.get("FORGE_MODEL", "")
    print(_LOG_PREFIX + " Invoking AI (" + tool + " " + (model_id or "default") + ")...")

    output, error = invoke_ai(prompt, tool, model_id)
    if error or not output:
        msg = error or "AI returned empty output"
        save_step_status(step, STATUS_ERROR, error=msg)
        print(_LOG_PREFIX + " Error: " + msg)
        return False

    parsed = parse_files(output)
    if not parsed:
        parsed = {"output.md": output}

    # Phase-scoped output: 15-build/<phase-id>/<step>/ when a phase is active
    if ACTIVE_PHASE_ID:
        out_dir = os.path.join(FORGE_DIR, DIR_BUILD, ACTIVE_PHASE_ID, step)
    else:
        out_dir = os.path.join(FORGE_DIR, meta["output_dir"])
    os.makedirs(out_dir, exist_ok=True)

    file_list = []
    for rel_path, content in parsed.items():
        # Save api-contract.md to shared location so frontend/tests can read it
        if step == "backend" and rel_path == _API_CONTRACT_FILENAME:
            os.makedirs(os.path.dirname(API_CONTRACT_FILE), exist_ok=True)
            with open(API_CONTRACT_FILE, "w", encoding=FILE_ENCODING) as f:
                f.write(content)
            print(_LOG_PREFIX + " API contract saved: " + API_CONTRACT_FILE)

        parts = rel_path.replace("\\", "/").split("/")
        full_path = os.path.join(out_dir, *parts)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding=FILE_ENCODING) as f:
            f.write(content)
        file_list.append(rel_path)
        print(_LOG_PREFIX + " Written: " + rel_path)

    save_step_status(step, STATUS_COMPLETE, files=file_list)
    print(_LOG_PREFIX + " Done. " + str(len(file_list)) + " files generated.")

    # Run post-generation fixups (lockfile generation, etc.)
    _post_generate_fixups(out_dir)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_runner.py <step>")
        sys.exit(1)
    success = run_step(sys.argv[1])
    sys.exit(0 if success else 1)
