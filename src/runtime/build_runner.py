#!/usr/bin/env python3
'''Build system runner - generates production-grade code from reviewed spec documents.
Two-pass strategy: backend generates API contract first, then frontend/integration consume it.
Usage: python3 scripts/build_runner.py <step>
'''
import os, sys, json, subprocess, tempfile
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FORGE_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", os.path.dirname(FORGE_DIR))
BUILD_STATUS_FILE = os.path.join(FORGE_DIR, "runs", "build-system.json")
API_CONTRACT_FILE = os.path.join(FORGE_DIR, "15-build", "api-contract.md")

# Build order matters: backend must run before frontend/integration/tests
STEPS = {
    "backend": {
        "label": "Backend & API",
        "agent": "code-architect",
        "source_dirs": ["01-requirements", "03-analysis", "04-architecture", "06-engineering"],
        "source_files": [],
        "output_dir": "15-build/backend",
    },
    "frontend": {
        "label": "Frontend UI",
        "agent": "frontend-coder",
        "source_dirs": ["02-design", "01-requirements"],
        "source_files": ["06-engineering/frontend-spec.md", "04-architecture/system-architecture.md"],
        "output_dir": "15-build/frontend",
    },
    "integration": {
        "label": "Integration Layer",
        "agent": "integration-engineer",
        "source_dirs": ["06-engineering"],
        "source_files": ["04-architecture/api-design.md"],
        "output_dir": "15-build/integration",
    },
    "tests": {
        "label": "Test Suite",
        "agent": "qa-coder",
        "source_dirs": ["07-quality"],
        "source_files": ["06-engineering/backend-spec.md", "06-engineering/frontend-spec.md"],
        "output_dir": "15-build/tests",
    },
    "infra": {
        "label": "Infrastructure",
        "agent": "devops-coder",
        "source_dirs": ["04-architecture", "06-engineering", "07-quality", "08-operations"],
        "source_files": ["01-requirements/prd.md"],
        "output_dir": "15-build/infra",
    },
}

BUILD_ORDER = ["backend", "frontend", "integration", "tests", "infra"]

def load_build_status():
    if os.path.exists(BUILD_STATUS_FILE):
        try:
            with open(BUILD_STATUS_FILE) as f:
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
        "generated_at": datetime.now().isoformat() if status_val == "complete" else existing.get("generated_at", ""),
        "error": error,
    }
    with open(BUILD_STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)

def collect_docs(meta):
    docs = []
    for dir_name in meta.get("source_dirs", []):
        dir_path = os.path.join(FORGE_DIR, dir_name)
        if os.path.isdir(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.endswith(".md"):
                    fpath = os.path.join(dir_path, fname)
                    if os.path.getsize(fpath) > 0:
                        with open(fpath, encoding="utf-8") as f:
                            content = f.read()
                        docs.append("=== SOURCE: " + dir_name + "/" + fname + " ===\n" + content)
    for rel_file in meta.get("source_files", []):
        fpath = os.path.join(FORGE_DIR, rel_file)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            docs.append("=== SOURCE: " + rel_file + " ===\n" + content)
    return "\n\n".join(docs)

def load_api_contract():
    if os.path.exists(API_CONTRACT_FILE) and os.path.getsize(API_CONTRACT_FILE) > 0:
        with open(API_CONTRACT_FILE, encoding="utf-8") as f:
            return f.read()
    return ""

def load_agent(agent_name):
    path = os.path.join(FORGE_DIR, "11-agents", agent_name + ".md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return "# Agent: " + agent_name + "\nGenerate code based on the provided specifications."

def invoke_ai(prompt, tool, model_id):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as tmp:
        tmp_path = tmp.name
    try:
        if tool == "gemini":
            cmd = ["gemini", "--skip-trust"]
            if model_id:
                cmd += ["-m", model_id]
            cmd += ["-p", prompt]
        elif tool == "claude":
            cmd = ["claude", "-p", prompt, "--output-format", "text"]
        else:
            cmd = ["gemini", "--skip-trust", "-p", prompt]
        with open(tmp_path, "w") as out_f:
            result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, timeout=600)
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace") if result.stderr else "AI call failed"
            return None, normalize_ai_error(err)
        with open(tmp_path, encoding="utf-8") as f:
            return f.read(), None
    except subprocess.TimeoutExpired:
        return None, "The request timed out after 10 minutes. Try again."
    except FileNotFoundError:
        return None, "AI tool '" + tool + "' not found in PATH"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def normalize_ai_error(raw_error):
    text = (raw_error or "").strip()
    lowered = text.lower()
    quota_markers = [
        "you've hit your limit",
        "hit your limit",
        "usage limit",
        "quota",
        "rate limit",
        "too many requests",
        "status 429",
    ]
    if any(marker in lowered for marker in quota_markers):
        return "The AI request failed. Wait a few minutes, then retry."
    if not text:
        return "The AI model returned an error. Retry the request."
    return text.splitlines()[0][:220]

def sanitize_path(candidate):
    p = candidate.strip()
    if " (" in p or p.endswith(")"):
        return None
    parts = p.replace("\\", "/").split("/")
    if parts and parts[0] == "15-build":
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

def build_backend_prompt(persona, docs):
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
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
        "=" * 60,
        COMMON_FORMAT_RULE,
        "=" * 60,
        "SPECIFICATION DOCUMENTS (your source of truth — follow these exactly)",
        "=" * 60,
        docs,
    ])

def build_frontend_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "BACKEND API CONTRACT — CONNECT TO THESE EXACT ENDPOINTS\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else
        "WARNING: Backend API contract not yet generated. "
        "Infer endpoints from the engineering spec documents.\n"
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
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
            "loading skeletons, form validation, accessible markup (ARIA where needed)."
        ),
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS",
        "=" * 60,
        docs,
    ])

def build_integration_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "BACKEND API CONTRACT\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else ""
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
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
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS",
        "=" * 60,
        docs,
    ])

def build_tests_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "BACKEND API CONTRACT — TEST THESE EXACT ENDPOINTS\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else ""
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
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
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS",
        "=" * 60,
        docs,
    ])

def build_infra_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "API CONTRACT (use to derive all required env vars and service dependencies)\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else ""
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "YOUR MISSION",
        "=" * 60,
        (
            "Read EVERY specification document below. Identify:\n"
            "  - The deployment platform (Fly.io, Vercel, AWS, Railway, etc.)\n"
            "  - Every third-party service used (Supabase, Stripe, Slack, SendGrid, Redis, etc.)\n"
            "  - Every environment variable required by the backend and frontend\n"
            "  - The test framework and what a test run needs (DB, env vars, etc.)\n\n"
            "Then generate a complete, self-contained infrastructure that automates EVERYTHING "
            "except the initial one-time secret values a human must set in GitHub."
        ),
        "=" * 60,
        "MANDATORY OUTPUT FILES",
        "=" * 60,
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
        "=" * 60,
        "SPEC COMPLIANCE RULES",
        "=" * 60,
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
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS (read all of these to derive the infra)",
        "=" * 60,
        docs,
    ])

def build_prompt_for_step(step, persona, docs, api_contract):
    if step == "backend":
        return build_backend_prompt(persona, docs)
    elif step == "frontend":
        return build_frontend_prompt(persona, docs, api_contract)
    elif step == "integration":
        return build_integration_prompt(persona, docs, api_contract)
    elif step == "tests":
        return build_tests_prompt(persona, docs, api_contract)
    elif step == "infra":
        return build_infra_prompt(persona, docs, api_contract)
    return persona + "\n\n---\n\n## Specification Documents\n\n" + docs

# -----------------------------------------------------------------------
# Step runner
# -----------------------------------------------------------------------

def run_step(step):
    meta = STEPS.get(step)
    if not meta:
        print("[BUILD] Unknown step: " + step)
        sys.exit(1)

    print("[BUILD] Running: " + meta["label"])
    save_step_status(step, "running")

    docs = collect_docs(meta)
    if not docs.strip():
        msg = "No source documents found. Generate and review the spec docs first."
        save_step_status(step, "error", error=msg)
        print("[BUILD] " + msg)
        return False

    api_contract = load_api_contract()
    if step in ("frontend", "integration", "tests") and not api_contract:
        print("[BUILD] WARNING: api-contract.md not found — run backend step first for fully connected output.")

    persona = load_agent(meta["agent"])
    prompt = build_prompt_for_step(step, persona, docs, api_contract)

    tool = os.environ.get("FORGE_TOOL", "gemini")
    model_id = os.environ.get("FORGE_MODEL", "")
    print("[BUILD] Invoking AI (" + tool + " " + (model_id or "default") + ")...")

    output, error = invoke_ai(prompt, tool, model_id)
    if error or not output:
        msg = error or "AI returned empty output"
        save_step_status(step, "error", error=msg)
        print("[BUILD] Error: " + msg)
        return False

    parsed = parse_files(output)
    if not parsed:
        parsed = {"output.md": output}

    out_dir = os.path.join(FORGE_DIR, meta["output_dir"])
    os.makedirs(out_dir, exist_ok=True)

    file_list = []
    for rel_path, content in parsed.items():
        # Save api-contract.md to shared location so frontend/tests can read it
        if step == "backend" and rel_path == "api-contract.md":
            os.makedirs(os.path.dirname(API_CONTRACT_FILE), exist_ok=True)
            with open(API_CONTRACT_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print("[BUILD] API contract saved: " + API_CONTRACT_FILE)

        parts = rel_path.replace("\\", "/").split("/")
        full_path = os.path.join(out_dir, *parts)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        file_list.append(rel_path)
        print("[BUILD] Written: " + rel_path)

    save_step_status(step, "complete", files=file_list)
    print("[BUILD] Done. " + str(len(file_list)) + " files generated.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_runner.py <step>")
        sys.exit(1)
    success = run_step(sys.argv[1])
    sys.exit(0 if success else 1)
