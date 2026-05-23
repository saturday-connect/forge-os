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
    ANTIGRAVITY_ARG_PRINT,
    ANTIGRAVITY_ARG_SKIP_PERMISSIONS,
    TOOL_ANTIGRAVITY,
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
        if tool == TOOL_ANTIGRAVITY:
            cmd = [TOOL_ANTIGRAVITY, ANTIGRAVITY_ARG_SKIP_PERMISSIONS, ANTIGRAVITY_ARG_PRINT, prompt]
        elif tool == TOOL_GEMINI:
            cmd = [TOOL_GEMINI, GEMINI_ARG_SKIP_TRUST]
            if model_id:
                cmd += [GEMINI_ARG_MODEL, model_id]
            cmd += [GEMINI_ARG_PROMPT, prompt]
        elif tool == TOOL_CLAUDE:
            cmd = [TOOL_CLAUDE, CLAUDE_ARG_PROMPT, prompt, CLAUDE_ARG_OUTPUT_FORMAT, CLAUDE_OUTPUT_TEXT]
        else:
            cmd = [TOOL_ANTIGRAVITY, ANTIGRAVITY_ARG_SKIP_PERMISSIONS, ANTIGRAVITY_ARG_PRINT, prompt]
        with open(tmp_path, "w", encoding=FILE_ENCODING) as out_f:
            result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, timeout=GENERATE_TIMEOUT_SECS,
                                    cwd=FORGE_DIR)  # pin cwd — prevents AI CLI scanning ~ or Desktop for context
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
        _section("PRIMARY DIRECTIVE — READ THIS FIRST"),
        (
            "You are generating a production-grade backend codebase that must pass `docker compose up --build` "
            "on the FIRST attempt with ZERO post-generation fixes.\n\n"
            "The definition of success: every container starts, every endpoint responds correctly, "
            "and the test suite exits 0.\n\n"
            "STEP ZERO — READ THE SPEC, IDENTIFY THE STACK:\n"
            "Before writing a single line of code, read all specification documents below and identify:\n"
            "  1. Language (Python, Node.js/TypeScript, Go, Ruby, Java, Rust, etc.)\n"
            "  2. Framework (FastAPI, Express, Gin, Rails, Spring Boot, Actix, etc.)\n"
            "  3. Database and client (Supabase, PostgreSQL + raw driver, MongoDB, MySQL, etc.)\n"
            "  4. Auth mechanism (Supabase Auth, JWT, OAuth2, session cookies, API keys)\n"
            "  5. Any named third-party services\n\n"
            "Use EXACTLY what the spec names. Never substitute."
        ),

        _section("FIRST OUTPUT BLOCK — MANDATORY"),
        (
            "Your VERY FIRST output block must ALWAYS be:\n\n"
            "=== api-contract.md ===\n\n"
            "This file is read by the frontend and integration agents. It must contain:\n"
            "  - Base URL (e.g. http://localhost:8000/api/v1)\n"
            "  - Auth mechanism and how to pass credentials\n"
            "  - Every endpoint: METHOD, full path, auth required (yes/no), request body schema, response schema\n"
            "  - Every error response: status code, body shape, when it occurs\n"
            "  - Database table/collection names and access policies if applicable\n"
            "  - All environment variables: name, description, example value\n\n"
            "Do NOT skip this file. Do NOT generate it last. It goes FIRST."
        ),

        _section("RULE 1 — TECH STACK: USE EXACTLY WHAT THE SPEC SAYS, NEVER SUBSTITUTE"),
        (
            "Read the architecture documents. Use EXACTLY the language, framework, DB, and auth system named.\n\n"
            "Common substitution mistakes to NEVER make:\n"
            "  Spec says FastAPI (Python)  → use FastAPI, NOT Flask, NOT Django\n"
            "  Spec says Express (Node.js) → use Express, NOT Fastify, NOT Koa\n"
            "  Spec says Go + Gin          → use Gin, NOT Echo, NOT stdlib net/http\n"
            "  Spec says Rails (Ruby)      → use Rails, NOT Sinatra\n"
            "  Spec says Supabase DB       → use the Supabase client for that language, NOT a raw ORM\n"
            "  Spec says PostgreSQL        → use PostgreSQL, NOT SQLite or in-memory store\n"
            "  Spec says Redis             → use Redis client, NOT an in-memory dict/map\n"
            "  Spec says JWT auth          → implement JWT, NOT session cookies\n\n"
            "If the spec is ambiguous, pick the simplest correct interpretation and document it in api-contract.md."
        ),

        _section("RULE 2 — DEPENDENCY MANIFEST: DECLARE EVERY PACKAGE"),
        (
            "Every package imported in any source file MUST appear in the dependency manifest.\n"
            "The Docker build installs from this manifest — a missing package = build failure.\n\n"
            "The manifest filename depends on the language:\n"
            "  Python      → requirements.txt  (pip install -r requirements.txt)\n"
            "  Node.js/TS  → package.json      (npm install)\n"
            "  Go          → go.mod            (go mod download)\n"
            "  Ruby        → Gemfile           (bundle install)\n"
            "  Java        → pom.xml / build.gradle\n"
            "  Rust        → Cargo.toml        (cargo build)\n\n"
            "RULE: walk every import/require/use statement in every source file. "
            "For every external package (not stdlib, not a local file): it MUST be in the manifest.\n\n"
            "Language-specific pitfalls:\n"
            "  Python/FastAPI: `python-multipart` is required for form/file uploads but often missed\n"
            "  Node.js: `@types/express`, `ts-node`, `typescript` belong in devDependencies\n"
            "  Go: run `go mod tidy` conceptually — every import must have a corresponding require\n"
            "  Ruby: separate test gems into group :test, :development in Gemfile"
        ),

        _section("RULE 3 — DOCKERFILE: MULTI-STAGE, NON-ROOT, CORRECT BASE IMAGE"),
        (
            "Use a multi-stage Dockerfile. Copy only what the runtime needs. Never run as root.\n\n"
            "Python/FastAPI:\n"
            "  FROM python:3.12-slim AS builder\n"
            "  COPY requirements.txt ./\n"
            "  RUN pip install --no-cache-dir -r requirements.txt\n"
            "  FROM python:3.12-slim AS runner\n"
            "  COPY --from=builder /usr/local/lib /usr/local/lib\n"
            "  COPY --from=builder /usr/local/bin /usr/local/bin\n"
            "  COPY . .\n"
            "  RUN useradd --create-home appuser && chown -R appuser /app\n"
            "  USER appuser\n"
            "  CMD ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000']\n\n"
            "Node.js/TypeScript:\n"
            "  FROM node:20-alpine AS builder\n"
            "  COPY package.json ./\n"
            "  RUN npm install --no-audit --no-fund  ← NEVER npm ci (no lockfile)\n"
            "  COPY . .\n"
            "  RUN npm run build\n"
            "  FROM node:20-alpine AS runner\n"
            "  COPY --from=builder /app/dist ./dist\n"
            "  COPY --from=builder /app/node_modules ./node_modules\n"
            "  RUN addgroup -S appgroup && adduser -S appuser -G appgroup\n"
            "  USER appuser\n"
            "  CMD ['node', 'dist/index.js']\n\n"
            "Go:\n"
            "  FROM golang:1.22-alpine AS builder\n"
            "  COPY go.mod go.sum ./\n"
            "  RUN go mod download\n"
            "  COPY . .\n"
            "  RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/server\n"
            "  FROM scratch AS runner\n"
            "  COPY --from=builder /app/server /server\n"
            "  USER 65534\n"
            "  CMD ['/server']\n\n"
            "Ruby/Rails:\n"
            "  FROM ruby:3.3-slim AS builder\n"
            "  COPY Gemfile Gemfile.lock ./\n"
            "  RUN bundle install --without development test\n"
            "  FROM ruby:3.3-slim AS runner\n"
            "  COPY --from=builder /usr/local/bundle /usr/local/bundle\n"
            "  COPY . .\n"
            "  RUN useradd --create-home appuser && chown -R appuser /app\n"
            "  USER appuser\n"
            "  CMD ['bundle', 'exec', 'rails', 'server', '-b', '0.0.0.0']\n\n"
            "UNIVERSAL RULES (apply regardless of language):\n"
            "  - Dependency install step BEFORE COPY . . (Docker layer cache)\n"
            "  - Explicit base image version — never :latest\n"
            "  - Non-root user in runner stage\n"
            "  - Server binds to 0.0.0.0 (not 127.0.0.1 — Docker won't expose it)"
        ),

        _section("RULE 4 — LANGUAGE PACKAGE STRUCTURE: NO MISSING INIT FILES"),
        (
            "Every language has package/module structure rules. Violating them = import errors at startup.\n\n"
            "Python:\n"
            "  Every directory that contains importable modules MUST have __init__.py\n"
            "  app/__init__.py, app/routers/__init__.py, app/models/__init__.py — ALL required\n"
            "  Missing __init__.py → ModuleNotFoundError on startup\n\n"
            "Node.js/TypeScript:\n"
            "  Every barrel file (index.ts) that re-exports must actually export what consumers import\n"
            "  tsconfig.json `paths` must align with the actual directory structure\n"
            "  `outDir: dist` — all imports in src/ must resolve after compilation to dist/\n\n"
            "Go:\n"
            "  Package name at top of every .go file must match the directory name\n"
            "  `package main` only in the entrypoint file (cmd/server/main.go)\n"
            "  All other packages use their directory name: `package handlers`, `package models`\n\n"
            "Ruby:\n"
            "  Every require path must match the actual file path relative to lib/\n"
            "  Rails autoloads from app/ — filenames must match class names exactly (snake_case)\n\n"
            "Java:\n"
            "  Package declarations must match directory path exactly\n"
            "  com.example.app → src/main/java/com/example/app/"
        ),

        _section("RULE 5 — FRAMEWORK-SPECIFIC CORRECTNESS"),
        (
            "Common framework-specific mistakes that cause silent failures or crashes:\n\n"
            "PYTHON / FastAPI:\n"
            "  - All I/O route handlers MUST be `async def` (sync handlers block the event loop)\n"
            "  - Use lifespan context manager, NOT @app.on_event('startup') (deprecated)\n"
            "  - Pydantic v2: use @field_validator not @validator; .model_dump() not .dict()\n"
            "  - supabase-py v2: result.data not result['data']; create client ONCE at startup\n"
            "  - CORS middleware MUST be added explicitly (FastAPI does not add it by default)\n\n"
            "NODE.JS / Express or Fastify:\n"
            "  - All async route handlers need try/catch or express-async-errors wrapper\n"
            "  - JSON body parsing: app.use(express.json()) BEFORE route registration\n"
            "  - TypeScript: compile with `tsc` before running; CMD must point to dist/, not src/\n"
            "  - @supabase/supabase-js v2: createClient takes (url, key), returns typed client\n\n"
            "GO / Gin or stdlib:\n"
            "  - c.JSON(200, data) not fmt.Fprintf (use the framework's response helper)\n"
            "  - Middleware registration order matters: auth before routes that need auth\n"
            "  - go.sum must be committed; go mod tidy ensures it is consistent\n\n"
            "RUBY / Rails:\n"
            "  - Rails credentials for secrets, not hardcoded values\n"
            "  - db:migrate must run before the app can start (include in Dockerfile or entrypoint)\n"
            "  - CORS: use rack-cors gem, configure in config/initializers/cors.rb\n\n"
            "JAVA / Spring Boot:\n"
            "  - @RestController + @RequestMapping, not @Controller (returns view names, not JSON)\n"
            "  - application.properties vs application.yml — pick one, be consistent\n"
            "  - @Transactional on service methods that write to DB, NOT on controllers"
        ),

        _section("RULE 6 — HEALTH CHECK ENDPOINT — ALWAYS REQUIRED"),
        (
            "ALWAYS generate a health check endpoint at GET /health.\n"
            "It is required by docker-compose healthcheck and CI smoke tests.\n\n"
            "Python/FastAPI:    @app.get('/health') async def health(): return {'status': 'ok'}\n"
            "Node.js/Express:   app.get('/health', (req, res) => res.json({ status: 'ok' }))\n"
            "Go/Gin:            r.GET('/health', func(c *gin.Context) { c.JSON(200, gin.H{'status': 'ok'}) })\n"
            "Ruby/Rails:        get '/health', to: proc { [200, {}, ['{\"status\":\"ok\"}']] }\n"
            "Java/Spring:       @GetMapping('/health') public Map<String,String> health() { return Map.of('status','ok'); }\n\n"
            "The health endpoint must respond within 5 seconds even if the DB is unavailable. "
            "If you check DB connectivity, return 503 on failure — not crash the process."
        ),

        _section("RULE 7 — EVERY IMPORT MUST RESOLVE"),
        (
            "Before finalising output, walk every import/require/use in every source file:\n\n"
            "Step 1 — Local imports: does the target file exist in your output?\n"
            "          Does it export the named symbol?\n\n"
            "Step 2 — Package imports: is the package in the dependency manifest?\n"
            "          Is the import path correct for that package's actual export shape?\n\n"
            "Step 3 — Circular imports (Python/Node.js): if A imports B and B imports A, "
            "          the runtime throws ImportError or undefined-at-require-time.\n"
            "          Fix: extract shared types into a separate types/models file.\n\n"
            "Step 4 — Case sensitivity (Linux Docker): `import './UserService'` fails if the file "
            "          is named `userService.ts`. Use consistent lowercase filenames.\n\n"
            "An unresolved import crashes the server at startup. "
            "There is no partial startup — one bad import and zero endpoints are served."
        ),

        _section("RULE 8 — COMPLETE IMPLEMENTATION: NO STUBS OR TODOS"),
        (
            "Every endpoint in the engineering spec MUST be fully implemented:\n"
            "  - Real business logic\n"
            "  - Real database queries (not hardcoded return values)\n"
            "  - Real error handling with appropriate HTTP status codes\n"
            "  - Real input validation\n"
            "  - Real auth checks (return 401 when unauthenticated, 403 when unauthorized)\n\n"
            "NEVER generate:\n"
            "  return {}          / return nil   / return null     ← empty response\n"
            "  # TODO: implement  / // TODO       / /* TODO */      ← unimplemented stub\n"
            "  raise NotImplementedError / panic('not implemented') ← crashes immediately\n"
            "  pass               / { }                             ← silent no-op\n\n"
            "If an endpoint depends on a third-party service that may not be available, "
            "implement it with a feature flag and a graceful fallback — not a stub."
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
        _section("PRIMARY DIRECTIVE — READ THIS FIRST"),
        (
            "You are generating a production-grade frontend codebase that must pass `npm run build` "
            "inside a Docker Linux container on the FIRST attempt, with ZERO post-generation fixes.\n\n"
            "The definition of success is: `docker compose up --build` starts all containers with exit code 0.\n\n"
            "Every rule below exists because ignoring it causes a Docker build failure. "
            "Treat every rule as a hard constraint, not a suggestion."
        ),

        _section("MANDATORY REQUIRED FILES — YOU MUST GENERATE ALL OF THESE"),
        (
            "Generate ALL files in this list. A missing file is a build failure.\n\n"
            "  src/lib/api.ts              — typed HTTP client, ALL endpoints from the API contract\n"
            "  src/lib/store.ts            — ONE unified Zustand store (see store rules below)\n"
            "  src/lib/supabase.ts         — lazy Supabase client (see supabase rules below)\n"
            "  src/types/api.ts            — TypeScript interfaces for all API request/response types\n"
            "  src/app/layout.tsx          — root layout with metadata and font setup\n"
            "  src/app/page.tsx            — root page (redirect or landing)\n"
            "  src/components/ui/button.tsx\n"
            "  src/components/ui/card.tsx\n"
            "  src/components/ui/input.tsx\n"
            "  tsconfig.json               — exact values specified below\n"
            "  next.config.js              — must include output:'standalone'\n"
            "  Dockerfile                  — multi-stage, no npm ci, uses standalone output\n"
            "  package.json                — all deps INCLUDING tailwindcss/autoprefixer/postcss if using Tailwind\n"
            "  .env.example                — all required environment variables"
        ),

        _section("RULE 1 — SINGLE UNIFIED STATE STORE (CRITICAL)"),
        (
            "Generate EXACTLY ONE state store file: `src/lib/store.ts`.\n\n"
            "DO NOT generate multiple store files at different paths. Having two or more store files "
            "that export the same hook name (useDiagramStore, useAppStore, etc.) at different import paths "
            "creates 61+ TypeScript errors because each consumer imagines a different state shape.\n\n"
            "The store MUST include every field that ANY consumer component needs. Before writing "
            "the store, list every component and what state it reads/writes. The store interface "
            "must be the UNION of all those fields.\n\n"
            "CORRECT pattern (one store, all state):\n"
            "```typescript\n"
            "// src/lib/store.ts\n"
            "import { create } from 'zustand';\n\n"
            "interface AppState {\n"
            "  // all fields any consumer needs\n"
            "  user: User | null;\n"
            "  items: Item[];\n"
            "  isLoading: boolean;\n"
            "  error: string | null;\n"
            "  setUser: (user: User | null) => void;\n"
            "  setItems: (items: Item[]) => void;\n"
            "  setLoading: (v: boolean) => void;\n"
            "  setError: (e: string | null) => void;\n"
            "  fetchItems: () => Promise<void>;\n"
            "}\n\n"
            "export const useAppStore = create<AppState>((set, get) => ({ ... }));\n"
            "```\n\n"
            "WRONG pattern (DO NOT DO THIS):\n"
            "  src/lib/store.ts        exports useAppStore with fields A, B\n"
            "  src/store/useStore.ts   exports useAppStore with fields C, D  ← NEVER\n"
            "  src/store/appStore.ts   exports useAppStore with fields E, F  ← NEVER\n\n"
            "If a component needs a field, that field must exist in the store. "
            "If it doesn't exist yet, add it to the store before writing the component."
        ),

        _section("RULE 2 — UI COMPONENT CONTRACTS (NEVER GENERATE INCOMPLETE COMPONENTS)"),
        (
            "Every UI component must export EVERY named export that any consumer will import.\n\n"

            "CARD COMPONENT — src/components/ui/card.tsx MUST export ALL of:\n"
            "  export const Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription\n"
            "  Reason: consumers import subcomponents by convention. Missing any = TypeScript error.\n\n"

            "BUTTON COMPONENT — src/components/ui/button.tsx MUST support:\n"
            "  variant: 'primary' | 'secondary' | 'ghost' | 'outline' | 'destructive' | 'link' | 'error'\n"
            "  size: 'sm' | 'md' | 'lg' | 'icon'\n"
            "  isLoading?: boolean   (also accept loading?: boolean as alias)\n"
            "  icon?: React.ReactNode\n"
            "  Reason: consumers use all of these. Missing variant/size = TypeScript build failure.\n\n"

            "INPUT COMPONENT — src/components/ui/input.tsx MUST export:\n"
            "  export const Input  (with label?, error?, helperText? props)\n\n"

            "GENERAL RULE: When you write a component that uses <ComponentName>, you MUST verify "
            "that ComponentName is exported by the file you're importing from. "
            "If CardHeader isn't exported by card.tsx, add it to card.tsx before using it."
        ),

        _section("RULE 3 — CSS VARIABLES CANNOT BE USED AS JSX EXPRESSION VALUES"),
        (
            "ILLEGAL — this causes a SyntaxError crash in SWC (Next.js compiler):\n"
            "  <rect rx={var(--radius-sm)} />        ← 'var' is a JS keyword, not a function\n"
            "  <circle r={var(--size-md)} />          ← same crash\n"
            "  <line strokeWidth={var(--border)} />   ← same crash\n\n"

            "CORRECT — use these patterns instead:\n"
            "  <rect rx={4} />                        ← numeric literal for SVG attributes\n"
            "  <rect rx='4' />                        ← string literal (SVG accepts this too)\n"
            "  <rect style={{ borderRadius: 'var(--radius-sm)' }} />  ← CSS var in style prop\n"
            "  <rect className={styles.rounded} />    ← CSS class where the var is applied\n\n"

            "Rule: `{var(--anything)}` is NEVER valid JSX. It is CSS syntax. "
            "If you want a CSS variable value in a JSX attribute, use a CSS class or inline style object."
        ),

        _section("RULE 4 — NEXT.JS ROUTING (NEVER MIX ROUTING LIBRARIES)"),
        (
            "Next.js has its own router. NEVER use react-router-dom in a Next.js project.\n\n"

            "BANNED — will crash at runtime:\n"
            "  import { useNavigate, NavLink, Link } from 'react-router-dom'  ← NEVER\n"
            "  import { BrowserRouter, Route, Routes } from 'react-router-dom'  ← NEVER\n"
            "  'react-router-dom' in package.json  ← NEVER\n\n"

            "CORRECT Next.js equivalents:\n"
            "  import Link from 'next/link'                          ← replaces <NavLink to=>\n"
            "  import { useRouter } from 'next/navigation'           ← replaces useNavigate()\n"
            "  import { usePathname } from 'next/navigation'         ← replaces useLocation()\n\n"

            "Active link detection — next/link does NOT support className as a function.\n"
            "WRONG:  <Link href='/' className={({ isActive }) => isActive ? 'active' : ''}>\n"
            "CORRECT:\n"
            "  const pathname = usePathname();\n"
            "  <Link href='/' className={pathname === '/' ? styles.active : ''}>\n\n"

            "Router navigation:\n"
            "  const router = useRouter();   ← NOT const navigate = useRouter()\n"
            "  router.push('/path');         ← NOT router('/path') or navigate('/path')"
        ),

        _section("RULE 5 — TYPESCRIPT MUST COMPILE WITH ZERO ERRORS"),
        (
            "The build runs `tsc --noEmit` before producing output. Any TypeScript error = build failure.\n\n"

            "tsconfig.json EXACT VALUES for Next.js 14+:\n"
            "  'moduleResolution': 'bundler'   ← NOT 'bundle' (invalid), NOT 'node' (wrong for Next.js 14)\n"
            "  'module': 'esnext'\n"
            "  'target': 'es5'\n"
            "  'strict': true\n"
            "  'noEmit': true\n"
            "  'jsx': 'preserve'\n"
            "  'incremental': true\n"
            "  'plugins': [{ 'name': 'next' }]\n"
            "  'paths': { '@/*': ['./src/*'] }\n\n"

            "TypeScript rules that prevent build failures:\n\n"

            "a) All named imports must be exported by the source file:\n"
            "   If you write: import { Foo, Bar } from './baz'\n"
            "   Then baz.tsx MUST export Foo AND export Bar.\n\n"

            "b) All props passed to a component must exist in its interface:\n"
            "   If you use <Button loading={true}>, then ButtonProps must have loading?: boolean.\n"
            "   If you use size='icon', then ButtonProps size must include 'icon'.\n\n"

            "c) Types from @/types/api.ts must match what the API actually returns:\n"
            "   If ValidateResponse has is_valid: boolean, you cannot access .valid on it.\n"
            "   Add alias fields to the type if consumers use different names.\n\n"

            "d) Never access properties that don't exist on a type:\n"
            "   If LayoutCoordinates has nodes[] and edges[], don't access .children or .layout_coordinates.\n\n"

            "e) useRouter() returns a Router object, not a function:\n"
            "   WRONG: const navigate = useRouter(); navigate('/path');\n"
            "   CORRECT: const router = useRouter(); router.push('/path');\n\n"

            "f) Array/object index access may be undefined — guard accordingly:\n"
            "   const icon = node.type ? IconMap[node.type] : IconMap.default;  ← safe\n"
            "   NOT: IconMap[node.type]  ← crashes if node.type is undefined"
        ),

        _section("RULE 6 — SUPABASE CLIENT INITIALIZATION"),
        (
            "The Supabase client MUST be lazy-initialized to avoid build failures when env vars "
            "are not set at Next.js static generation time.\n\n"

            "WRONG — crashes SSG build with 'supabaseUrl is required':\n"
            "  export const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, ...);\n\n"

            "CORRECT — use exactly this pattern:\n"
            "```typescript\n"
            "// src/lib/supabase.ts\n"
            "import { createClient, SupabaseClient } from '@supabase/supabase-js';\n\n"
            "let _client: SupabaseClient | null = null;\n\n"
            "function getClient(): SupabaseClient {\n"
            "  if (!_client) {\n"
            "    const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? 'https://placeholder.supabase.co';\n"
            "    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? 'placeholder';\n"
            "    _client = createClient(url, key);\n"
            "  }\n"
            "  return _client;\n"
            "}\n\n"
            "export const supabase = new Proxy({} as SupabaseClient, {\n"
            "  get(_t, prop) { return getClient()[prop as keyof SupabaseClient]; },\n"
            "});\n"
            "```\n\n"
            "Also: add `export const dynamic = 'force-dynamic';` at the top of any page that "
            "calls Supabase auth (login, signup, protected pages). "
            "This prevents Next.js from statically rendering the page at build time without env vars."
        ),

        _section("RULE 7 — CASE-SENSITIVE FILENAMES AND IMPORTS (LINUX DOCKER)"),
        (
            "macOS filesystem is case-insensitive. Docker Linux is case-sensitive. "
            "A file that imports correctly on Mac will crash in Docker if the case doesn't match.\n\n"

            "MANDATORY conventions — enforce these EXACTLY:\n"
            "  All directories under src/components/ MUST be lowercase:\n"
            "    src/components/ui/       ← CORRECT\n"
            "    src/components/layout/   ← CORRECT\n"
            "    src/components/editor/   ← CORRECT\n"
            "    src/components/shared/   ← CORRECT\n"
            "    src/components/UI/       ← WRONG — will crash in Docker\n"
            "    src/components/Layout/   ← WRONG — will crash in Docker\n\n"

            "  All filenames inside src/components/ MUST be lowercase:\n"
            "    src/components/ui/button.tsx    ← CORRECT\n"
            "    src/components/ui/card.tsx      ← CORRECT\n"
            "    src/components/ui/Button.tsx    ← WRONG\n"
            "    src/components/ui/Card.tsx      ← WRONG\n\n"

            "  Imports MUST exactly match the filename case:\n"
            "    import { Button } from '@/components/ui/button'   ← CORRECT\n"
            "    import { Button } from '@/components/ui/Button'   ← WRONG\n\n"

            "  NEVER generate two files that differ only in case:\n"
            "    src/components/ui/button.tsx AND src/components/ui/Button.tsx  ← CRASHES DOCKER\n\n"

            "  Page components (src/app/**/page.tsx) and layout files use lowercase directory names:\n"
            "    src/app/dashboard/page.tsx   ← CORRECT\n"
            "    src/app/Dashboard/page.tsx   ← WRONG"
        ),

        _section("RULE 8 — PACKAGE.JSON — ALL DEPENDENCIES MUST BE DECLARED"),
        (
            "Every package that is imported in any source file MUST appear in package.json.\n"
            "The Docker build runs `npm install` from package.json. "
            "An import for a package not in package.json = build failure at compile time.\n\n"

            "MANDATORY entries — add these if your code uses them:\n"
            "  'zustand'              — if using Zustand store\n"
            "  'axios'                — if using axios HTTP client\n"
            "  '@supabase/supabase-js' — if using Supabase auth or DB\n"
            "  'tailwindcss'          — in devDependencies if using Tailwind CSS\n"
            "  'autoprefixer'         — in devDependencies if using Tailwind\n"
            "  'postcss'              — in devDependencies if using Tailwind\n"
            "  'clsx'                 — if using clsx() for class merging\n"
            "  'tailwind-merge'       — if using twMerge()\n"
            "  'lucide-react'         — if using Lucide icons\n"
            "  '@monaco-editor/react' — if using Monaco editor\n"
            "  'elkjs'                — if rendering ELK graph layouts\n"
            "  'web-worker'           — if using ELK (it requires web-worker)\n"
            "  'framer-motion'        — if using animation\n"
            "  'zod'                  — if using schema validation\n"
            "  'react-hook-form'      — if using form handling\n"
            "  'date-fns'             — if formatting dates\n\n"

            "RULE: scan every `import` statement in your output. For every package that is not "
            "a relative import (./), a path alias (@/), or a Node.js built-in — it MUST be in package.json."
        ),

        _section("RULE 9 — DOCKERFILE REQUIREMENTS"),
        (
            "Use ONLY this Dockerfile pattern for Next.js. Deviating from it causes runtime failures.\n\n"
            "```dockerfile\n"
            "FROM node:18-alpine AS base\n\n"
            "FROM base AS builder\n"
            "WORKDIR /app\n"
            "COPY package.json ./\n"
            "RUN npm install --no-audit --no-fund\n"
            "COPY . .\n"
            "RUN npm run build\n\n"
            "FROM base AS runner\n"
            "WORKDIR /app\n"
            "ENV NODE_ENV production\n"
            "ENV NEXT_TELEMETRY_DISABLED 1\n"
            "RUN addgroup --system --gid 1001 nodejs\n"
            "RUN adduser --system --uid 1001 nextjs\n"
            "COPY --from=builder /app/public ./public\n"
            "COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./\n"
            "COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static\n"
            "USER nextjs\n"
            "EXPOSE 3000\n"
            "ENV PORT 3000\n"
            "ENV HOSTNAME '0.0.0.0'\n"
            "CMD ['node', 'server.js']\n"
            "```\n\n"
            "CRITICAL — DO NOT:\n"
            "  - Use `npm ci` — there is no package-lock.json\n"
            "  - COPY `package*.json` — only COPY `package.json`\n"
            "  - Omit `output: 'standalone'` in next.config.js — the runner stage needs it\n"
            "  - Use `CMD ['npm', 'start']` — use `CMD ['node', 'server.js']`"
        ),

        _section("RULE 10 — COMPLETE API CLIENT WITH CORRECT SIGNATURES"),
        (
            "src/lib/api.ts must be a complete, typed HTTP client. Rules:\n\n"

            "a) Every method accepts ONLY the arguments it actually uses.\n"
            "   WRONG: validateMermaid(raw: string, type: string, token: string) "
            "if the HTTP call only uses `raw`.\n"
            "   CORRECT: validateMermaid(raw: string) — add optional _extra?: string for forward-compat.\n\n"

            "b) Response types must match what the API actually returns.\n"
            "   If the endpoint returns { is_valid: boolean }, the response type MUST have is_valid.\n"
            "   You cannot access .valid on a type that only has .is_valid.\n\n"

            "c) Export ALL types that any consumer file will import:\n"
            "   export type { Diagram, Node, Edge, Group, TransformResponse, ValidateResponse };\n"
            "   Consumers often do: import { Node, Edge } from '@/lib/api' — these must be exported.\n\n"

            "d) The api object must only contain methods that actually exist:\n"
            "   NEVER generate usage like api.clearToken(), api.logout(), api.calculateLayout() "
            "unless those methods are defined in the api object in api.ts.\n"
            "   To clear auth: use localStorage.removeItem('auth_token') directly."
        ),

        _section("RULE 11 — EVERY IMPORT MUST RESOLVE TO A REAL EXPORT"),
        (
            "Before finalising your output, execute this mental checklist for EVERY file you generate:\n\n"

            "Step 1 — For every `import { A, B, C } from './path'`:\n"
            "   Verify that the target file exports A, exports B, and exports C.\n"
            "   If any of them are not exported — either add the export, or remove the import.\n\n"

            "Step 2 — For every `import { A } from '@/components/ui/x'`:\n"
            "   Verify the file src/components/ui/x.tsx exists in your output.\n"
            "   Verify it exports A.\n\n"

            "Step 3 — For every `import { Icon } from 'lucide-react'`:\n"
            "   Only import icons that actually exist in lucide-react.\n"
            "   Valid: ArrowRight, Check, X, ChevronDown, Search, Plus, Settings, User, etc.\n"
            "   If unsure about a specific icon name — use a definitely-valid one instead.\n\n"

            "Step 4 — For every npm package import:\n"
            "   Verify it is in package.json dependencies or devDependencies.\n\n"

            "Step 5 — For every React component used in JSX:\n"
            "   Verify the component is imported in the file.\n"
            "   Verify it is exported by the file it's imported from.\n\n"

            "This checklist is not optional. A build that compiles clean on first `npm run build` "
            "is the only acceptable output."
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
        _section("PRIMARY DIRECTIVE — READ THIS FIRST"),
        (
            "You are generating production-grade integration code that must work correctly "
            "on the FIRST attempt inside a Docker Linux container with ZERO post-generation fixes.\n\n"
            "The definition of success: every third-party integration connects, webhooks are secured, "
            "and `docker compose up --build` exits 0.\n\n"
            "Every rule below exists because ignoring it causes a runtime failure or a security breach."
        ),

        _section("MANDATORY REQUIRED FILES — GENERATE ALL OF THESE"),
        (
            "A missing file is a build failure. Generate ALL that apply to the spec:\n\n"
            "  app/integrations/__init__.py      — package init\n"
            "  app/integrations/<service>.py     — one file per third-party service\n"
            "  app/routers/webhooks.py           — inbound webhook router (signature-verified)\n"
            "  requirements.txt additions        — every new SDK package, pinned\n"
            "  .env.example additions            — every new credential needed\n"
            "  tests/test_integrations.py        — at minimum a smoke test per integration"
        ),

        _section("RULE 1 — USE ONLY NAMED SDKS FROM THE SPEC"),
        (
            "Read every integration spec document. For each third-party service, use its OFFICIAL SDK:\n\n"
            "  Stripe  → stripe>=8.0 (NOT requests to api.stripe.com directly)\n"
            "  Slack   → slack_sdk>=3.27 (NOT webhooks-only unless spec says so)\n"
            "  SendGrid → sendgrid>=6.11 (NOT smtplib unless spec says SMTP)\n"
            "  Twilio  → twilio>=9.0\n"
            "  AWS     → boto3>=1.34\n"
            "  GCS     → google-cloud-storage>=2.15\n\n"
            "NEVER use requests/httpx directly to call a service that has an official SDK.\n"
            "Add every SDK to requirements.txt with a pinned minimum version."
        ),

        _section("RULE 2 — WEBHOOK SIGNATURE VERIFICATION IS MANDATORY"),
        (
            "Every inbound webhook endpoint MUST verify the request signature before processing.\n"
            "An unverified webhook = critical security vulnerability.\n\n"
            "STRIPE webhooks:\n"
            "  import stripe\n"
            "  event = stripe.Webhook.construct_event(\n"
            "      payload=await request.body(),\n"
            "      sig_header=request.headers.get('stripe-signature'),\n"
            "      secret=os.getenv('STRIPE_WEBHOOK_SECRET'),\n"
            "  )\n"
            "  # raises stripe.error.SignatureVerificationError on failure\n\n"
            "SLACK webhooks:\n"
            "  from slack_sdk.signature import SignatureVerifier\n"
            "  verifier = SignatureVerifier(signing_secret=os.getenv('SLACK_SIGNING_SECRET'))\n"
            "  if not verifier.is_valid_request(body=body_bytes, headers=dict(request.headers)):\n"
            "      raise HTTPException(status_code=401, detail='Invalid signature')\n\n"
            "GENERIC HMAC pattern (for services without an SDK):\n"
            "  import hmac, hashlib\n"
            "  expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()\n"
            "  if not hmac.compare_digest(expected, received_sig):\n"
            "      raise HTTPException(status_code=401)\n\n"
            "NEVER skip signature verification with a TODO comment."
        ),

        _section("RULE 3 — ALL CREDENTIALS FROM ENVIRONMENT VARIABLES"),
        (
            "NEVER hardcode API keys, secrets, or credentials in source code.\n\n"
            "CORRECT:\n"
            "  stripe.api_key = os.getenv('STRIPE_SECRET_KEY')\n"
            "  SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')\n\n"
            "WRONG:\n"
            "  stripe.api_key = 'sk_live_abc123'  ← NEVER\n"
            "  SLACK_BOT_TOKEN = 'xoxb-abc'        ← NEVER\n\n"
            "Startup validation — fail fast if required env vars are missing:\n"
            "  def validate_env():\n"
            "      required = ['STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET', 'SLACK_BOT_TOKEN']\n"
            "      missing = [k for k in required if not os.getenv(k)]\n"
            "      if missing:\n"
            "          raise RuntimeError(f'Missing required env vars: {missing}')\n\n"
            "Add EVERY credential to .env.example with a comment explaining where to get it."
        ),

        _section("RULE 4 — RETRY, TIMEOUT, AND ERROR HANDLING FOR EVERY EXTERNAL CALL"),
        (
            "External service calls WILL fail intermittently. Handle this at the call site:\n\n"
            "MINIMUM per external call:\n"
            "  - timeout: set an explicit timeout (never let a call hang indefinitely)\n"
            "  - retry: 3 attempts with exponential backoff for transient errors (429, 503, network)\n"
            "  - circuit break: do not retry on permanent errors (401, 403, 404)\n"
            "  - log: structured log on every failure with the service name and error\n\n"
            "CORRECT pattern:\n"
            "  import tenacity\n"
            "  @tenacity.retry(\n"
            "      stop=tenacity.stop_after_attempt(3),\n"
            "      wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),\n"
            "      retry=tenacity.retry_if_exception_type((stripe.error.RateLimitError, ConnectionError)),\n"
            "  )\n"
            "  async def charge_customer(amount: int, customer_id: str) -> stripe.PaymentIntent:\n"
            "      return stripe.PaymentIntent.create(amount=amount, customer=customer_id)\n\n"
            "Add tenacity>=8.2.0 to requirements.txt."
        ),

        _section("RULE 5 — IDEMPOTENCY KEYS FOR PAYMENT OPERATIONS"),
        (
            "Payment operations (Stripe charges, refunds, payouts) MUST use idempotency keys.\n"
            "Without them, a network retry creates a duplicate charge — irreversible data loss.\n\n"
            "CORRECT:\n"
            "  import uuid\n"
            "  stripe.PaymentIntent.create(\n"
            "      amount=amount,\n"
            "      currency='usd',\n"
            "      customer=customer_id,\n"
            "      idempotency_key=f'pi-{order_id}-{uuid.uuid4()}',\n"
            "  )\n\n"
            "WRONG:\n"
            "  stripe.PaymentIntent.create(amount=amount, currency='usd')  ← no idempotency key\n\n"
            "Store the idempotency key in your DB before calling Stripe, "
            "so a retry uses the same key rather than generating a new one."
        ),

        _section("RULE 6 — REQUIREMENTS.TXT: EVERY SDK MUST BE DECLARED"),
        (
            "Every SDK imported in any integration file MUST be in requirements.txt.\n"
            "Common packages to add when they appear in imports:\n"
            "  stripe>=8.0.0\n"
            "  slack_sdk>=3.27.0\n"
            "  sendgrid>=6.11.0\n"
            "  twilio>=9.0.0\n"
            "  boto3>=1.34.0\n"
            "  google-cloud-storage>=2.15.0\n"
            "  tenacity>=8.2.0        — for retry logic\n"
            "  httpx>=0.27.0          — for any direct HTTP calls\n\n"
            "RULE: walk every `import X` and `from X import Y` in every integration file. "
            "If X is not stdlib, it MUST be in requirements.txt."
        ),

        _section("RULE 7 — EVERY IMPORT MUST RESOLVE"),
        (
            "Before finalising output, for every file you generate:\n\n"
            "1. Every `from app.X import Y` — does app/X.py exist? Does it export Y?\n"
            "2. Every `from .X import Y` (relative) — is X in the same package? Does it export Y?\n"
            "3. Every third-party import — is the package in requirements.txt?\n"
            "4. All integration functions used in routers — are they imported at the top of the router file?\n\n"
            "An unresolved import crashes the FastAPI app on startup with ImportError. "
            "There is no graceful degradation — the entire server fails to start."
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
        _section("PRIMARY DIRECTIVE — READ THIS FIRST"),
        (
            "You are generating a production-grade test suite that must run `pytest` to exit 0 "
            "and `npm test` to pass on the FIRST attempt inside a Docker Linux container, "
            "with ZERO post-generation fixes.\n\n"
            "The definition of success: `make test` in CI exits 0 with coverage reported.\n\n"
            "Every rule below exists because ignoring it causes test collection failure or "
            "silent test skips that hide real bugs."
        ),

        _section("MANDATORY REQUIRED FILES — GENERATE ALL OF THESE"),
        (
            "A missing file causes test collection failure. Generate ALL of:\n\n"
            "  tests/__init__.py              — makes tests a package (required for imports)\n"
            "  tests/conftest.py              — ALL shared fixtures (app client, auth token, DB seed)\n"
            "  tests/test_<domain>.py         — one file per API domain from the contract\n"
            "  pytest.ini (or pyproject.toml) — test config including asyncio_mode\n"
            "  requirements-dev.txt           — test-only packages (pytest, httpx, faker, etc.)\n"
            "  playwright.config.ts           — if E2E tests are specified in the quality spec"
        ),

        _section("RULE 1 — USE ONLY THE TEST FRAMEWORKS NAMED IN THE QUALITY SPEC"),
        (
            "Read the quality spec documents. Use EXACTLY the frameworks named:\n\n"
            "  Spec says pytest     → use pytest with pytest-asyncio, NEVER unittest\n"
            "  Spec says Playwright → use Playwright for E2E, NOT Cypress or Selenium\n"
            "  Spec says Vitest     → use Vitest for frontend unit tests, NOT Jest\n"
            "  Spec says Jest       → use Jest, NOT Vitest\n\n"
            "NEVER mix test frameworks (e.g. pytest + unittest in the same suite). "
            "Pick the one the spec names and use it exclusively for that layer."
        ),

        _section("RULE 2 — PYTEST ASYNC: ASYNCIO_MODE MUST BE SET"),
        (
            "FastAPI test clients and async fixtures require explicit asyncio configuration.\n"
            "Missing this setting causes: `PytestUnraisableExceptionWarning` or all async tests skip.\n\n"
            "CORRECT — include in pytest.ini:\n"
            "  [pytest]\n"
            "  asyncio_mode = auto\n"
            "  testpaths = tests\n\n"
            "OR in pyproject.toml:\n"
            "  [tool.pytest.ini_options]\n"
            "  asyncio_mode = 'auto'\n"
            "  testpaths = ['tests']\n\n"
            "Add to requirements-dev.txt:\n"
            "  pytest>=8.0.0\n"
            "  pytest-asyncio>=0.23.0\n"
            "  httpx>=0.27.0         ← for AsyncClient\n"
            "  anyio>=4.3.0          ← dependency of pytest-asyncio\n\n"
            "NEVER use `@pytest.mark.asyncio` on individual test functions when asyncio_mode=auto is set — "
            "it's redundant and causes a deprecation warning."
        ),

        _section("RULE 3 — CONFTEST.PY: ALL SHARED FIXTURES GO HERE"),
        (
            "conftest.py is NOT optional. Missing fixtures cause every test to fail with FixtureError.\n\n"
            "REQUIRED fixtures:\n\n"
            "  @pytest.fixture(scope='session')\n"
            "  async def async_client():\n"
            "      from app.main import app\n"
            "      async with AsyncClient(app=app, base_url='http://test') as client:\n"
            "          yield client\n\n"
            "  @pytest.fixture(scope='session')\n"
            "  async def auth_token(async_client):\n"
            "      response = await async_client.post('/api/v1/auth/login',\n"
            "          json={'email': 'test@example.com', 'password': 'testpass123'})\n"
            "      return response.json()['access_token']\n\n"
            "  @pytest.fixture\n"
            "  def auth_headers(auth_token):\n"
            "      return {'Authorization': f'Bearer {auth_token}'}\n\n"
            "For DB-dependent tests, add a fixture that seeds and tears down test data. "
            "Use a separate test DB (set via TEST_DATABASE_URL env var)."
        ),

        _section("RULE 4 — COVERAGE: EVERY ENDPOINT NEEDS 4 TEST CASES"),
        (
            "For EVERY endpoint in the API contract, generate these 4 test cases minimum:\n\n"
            "  async def test_<action>_success(async_client, auth_headers):\n"
            "      r = await async_client.post('/api/v1/items', json={...}, headers=auth_headers)\n"
            "      assert r.status_code == 201\n"
            "      assert r.json()['id'] is not None\n\n"
            "  async def test_<action>_unauthenticated(async_client):\n"
            "      r = await async_client.post('/api/v1/items', json={...})  # no auth\n"
            "      assert r.status_code == 401\n\n"
            "  async def test_<action>_invalid_input(async_client, auth_headers):\n"
            "      r = await async_client.post('/api/v1/items', json={'bad': 'data'}, headers=auth_headers)\n"
            "      assert r.status_code == 422\n\n"
            "  async def test_<action>_not_found(async_client, auth_headers):\n"
            "      r = await async_client.get('/api/v1/items/nonexistent-id', headers=auth_headers)\n"
            "      assert r.status_code == 404\n\n"
            "NEVER write a test that only checks `status_code == 200` without asserting the response body. "
            "An endpoint that returns `{}` would pass — that test is worthless."
        ),

        _section("RULE 5 — TEST IMPORTS MUST MATCH THE ACTUAL CODE STRUCTURE"),
        (
            "Every `from app.X import Y` in a test file MUST match the actual backend code structure.\n\n"
            "Before writing a test import:\n"
            "  1. Does app/X.py exist in the backend output? Does it export Y?\n"
            "  2. Does the app.main module create the FastAPI `app` object?\n"
            "  3. Is the test file inside the `tests/` directory?\n\n"
            "WRONG:\n"
            "  from backend.app.main import app  ← wrong if running pytest from repo root\n"
            "  from src.app.main import app       ← wrong if there's no src/ prefix\n\n"
            "CORRECT:\n"
            "  from app.main import app  ← when pytest runs from the backend/ directory\n\n"
            "In pytest.ini or Makefile, set the working directory to the backend service dir:\n"
            "  cd backend && pytest  ← ensures `from app.X` resolves correctly"
        ),

        _section("RULE 6 — REQUIREMENTS-DEV.TXT: ALL TEST DEPS MUST BE DECLARED"),
        (
            "Generate a separate requirements-dev.txt for test-only packages.\n"
            "The CI pipeline runs `pip install -r requirements-dev.txt` before running tests.\n\n"
            "MANDATORY entries:\n"
            "  pytest>=8.0.0\n"
            "  pytest-asyncio>=0.23.0\n"
            "  httpx>=0.27.0           — for AsyncClient (NOT requests)\n"
            "  anyio>=4.3.0\n"
            "  faker>=24.0.0           — if generating test data\n"
            "  pytest-cov>=5.0.0       — for coverage reporting\n"
            "  factory-boy>=3.3.0      — if using model factories\n\n"
            "requirements-dev.txt should also include `-r requirements.txt` at the top "
            "so the test environment has all production packages too."
        ),

        _section("RULE 7 — PLAYWRIGHT E2E: COMPLETE SETUP IF SPECIFIED"),
        (
            "If the quality spec mentions Playwright or E2E tests, generate the full setup.\n"
            "Partial Playwright setup is worse than none — it causes CI to hang.\n\n"
            "REQUIRED files:\n"
            "  playwright.config.ts      — base URL, browser targets, test dir\n"
            "  tests/e2e/               — all E2E test files\n"
            "  tests/e2e/<flow>.spec.ts — one file per user journey\n\n"
            "playwright.config.ts MINIMUM:\n"
            "  export default defineConfig({\n"
            "    testDir: './tests/e2e',\n"
            "    use: { baseURL: process.env.BASE_URL || 'http://localhost:3000' },\n"
            "    webServer: {\n"
            "      command: 'docker compose up -d',\n"
            "      url: 'http://localhost:3000',\n"
            "      reuseExistingServer: !process.env.CI,\n"
            "    },\n"
            "  });\n\n"
            "Add to package.json devDependencies:\n"
            "  '@playwright/test': '^1.44.0'"
        ),

        _section("RULE 8 — EVERY IMPORT MUST RESOLVE IN TEST FILES"),
        (
            "Test files have the same import correctness requirement as production code.\n\n"
            "Before finalising each test file:\n"
            "  1. Every `from app.X import Y` — does the backend generate app/X.py with Y exported?\n"
            "  2. Every pytest fixture used — is it defined in conftest.py or imported?\n"
            "  3. Every factory class — is it defined in the same or an imported file?\n"
            "  4. Every package imported — is it in requirements-dev.txt?\n\n"
            "A missing import causes `ERROR collecting tests/test_X.py` — "
            "no tests run at all, CI fails silently."
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
        _section("PRIMARY DIRECTIVE — READ THIS FIRST"),
        (
            "You are generating production-grade infrastructure that must pass `docker compose up --build` "
            "and `docker compose config --quiet` on the FIRST attempt with ZERO post-generation fixes.\n\n"
            "The definition of success: every container starts, healthchecks pass, CI/CD YAML is valid.\n\n"
            "Every rule below exists because ignoring it causes a build failure, a CI pipeline failure, "
            "or a security vulnerability."
        ),

        _section("RULE 1 — DEPLOYMENT PLATFORM: USE EXACTLY WHAT THE SPEC SAYS"),
        (
            "Read the operations and architecture docs. Use EXACTLY the platform named:\n\n"
            "  Spec says Fly.io    → generate fly.toml for each service, flyctl commands in CI\n"
            "  Spec says Vercel    → generate vercel.json for frontend, Vercel CLI in CI\n"
            "  Spec says Railway   → generate railway.toml, Railway CLI in CI\n"
            "  Spec says AWS ECS   → generate task definitions, ECR push, ECS deploy steps\n"
            "  Spec says GCP Cloud Run → generate service.yaml, gcloud run deploy steps\n\n"
            "NEVER substitute a different platform. NEVER use Docker Swarm when the spec says Kubernetes."
        ),

        _section("RULE 2 — DOCKER COMPOSE: EXACT BUILD CONTEXT AND DOCKERFILE PATHS"),
        (
            "docker-compose.yml lives in infra/. Service dirs are siblings at the same level.\n\n"
            "CORRECT — context uses parent-relative paths:\n"
            "  services:\n"
            "    backend:\n"
            "      build:\n"
            "        context: ../backend\n"
            "        dockerfile: Dockerfile\n"
            "    frontend:\n"
            "      build:\n"
            "        context: ../frontend\n"
            "        dockerfile: Dockerfile\n\n"
            "WRONG — these paths are relative to the wrong directory:\n"
            "  context: ./backend   ← looks for infra/backend/ — does not exist\n"
            "  context: backend     ← same error\n"
            "  context: .           ← builds from infra/ — wrong\n\n"
            "EVERY service needs a healthcheck:\n"
            "  healthcheck:\n"
            "    test: ['CMD', 'curl', '-f', 'http://localhost:8000/health']\n"
            "    interval: 30s\n"
            "    timeout: 10s\n"
            "    retries: 3\n"
            "    start_period: 40s\n\n"
            "depends_on must use condition: service_healthy (not just service_started):\n"
            "  depends_on:\n"
            "    backend:\n"
            "      condition: service_healthy"
        ),

        _section("RULE 3 — DOCKERFILE npm COMMANDS: NEVER USE npm ci"),
        (
            "AI-generated projects do NOT include package-lock.json.\n"
            "`npm ci` REQUIRES package-lock.json — it will crash with:\n"
            "  npm error `npm ci` can only install packages when your package.json\n"
            "  and package-lock.json are in sync\n\n"
            "CORRECT — every Node.js Dockerfile MUST use:\n"
            "  COPY package.json ./\n"
            "  RUN npm install --no-audit --no-fund\n\n"
            "WRONG:\n"
            "  COPY package*.json ./  ← may copy a stale lockfile\n"
            "  RUN npm ci             ← CRASHES without lockfile\n\n"
            "This applies to EVERY Dockerfile you generate — backend/Dockerfile, frontend/Dockerfile, "
            "any service Dockerfile. Check every npm command before finalising."
        ),

        _section("RULE 4 — GITHUB ACTIONS YAML: EXACT SYNTAX RULES"),
        (
            "GitHub Actions YAML is strict. Any syntax error = entire workflow fails silently.\n\n"
            "MANDATORY structure for every workflow:\n"
            "  name: <descriptive name>\n"
            "  on:\n"
            "    push:\n"
            "      branches: [main]\n"
            "  permissions:\n"
            "    contents: read\n"
            "  jobs:\n"
            "    <job-id>:\n"
            "      runs-on: ubuntu-latest\n"
            "      steps:\n"
            "        - uses: actions/checkout@v4\n\n"
            "CRITICAL RULES:\n"
            "  1. `uses:` and `run:` are mutually exclusive in a step — never combine them\n"
            "  2. Secrets: `${{ secrets.MY_SECRET }}` — never `${{secrets.MY_SECRET}}` (spaces required)\n"
            "  3. Environment files: use `>> $GITHUB_ENV` — NOT `export VAR=value` (lost after the step)\n"
            "  4. Python setup: use `actions/setup-python@v5` — NOT v3\n"
            "  5. Node setup: use `actions/setup-node@v4` — NOT v2\n"
            "  6. Cache: use `actions/cache@v4` — NOT v2\n"
            "  7. Multi-line run blocks: use `|` YAML block scalar — never string concatenation\n"
            "  8. Docker login: use `docker/login-action@v3` before any docker push\n\n"
            "NEVER generate a step like:\n"
            "  - run: echo 'do step X'  # TODO\n"
            "Every step must be complete and runnable."
        ),

        _section("RULE 5 — ENVIRONMENT VARIABLES: ZERO OMISSIONS"),
        (
            "Every environment variable read by ANY service must appear in BOTH:\n"
            "  a. The docker-compose.yml `environment:` or `env_file:` block for that service\n"
            "  b. secrets-required.md as a GitHub Secret entry\n\n"
            "Method: walk every .env.example file from backend, frontend, and integration steps. "
            "Every variable listed there must be wired into the CI/CD.\n\n"
            "CORRECT in docker-compose.yml:\n"
            "  backend:\n"
            "    environment:\n"
            "      DATABASE_URL: ${DATABASE_URL}\n"
            "      SUPABASE_URL: ${SUPABASE_URL}\n"
            "      SUPABASE_KEY: ${SUPABASE_KEY}\n"
            "      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}\n\n"
            "CORRECT in CI:\n"
            "  env:\n"
            "    DATABASE_URL: ${{ secrets.DATABASE_URL }}\n"
            "    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}\n\n"
            "NEVER use placeholder values like YOUR_KEY_HERE or REPLACE_ME in workflow files."
        ),

        _section("RULE 6 — SUPABASE MIGRATIONS: USE SUPABASE CLI, NOT ALEMBIC"),
        (
            "The spec uses Supabase — do NOT generate Alembic migration files or alembic.ini.\n"
            "Schema migrations are SQL files in supabase/migrations/, applied via Supabase CLI.\n\n"
            "CORRECT in CI deploy workflow:\n"
            "  - name: Run database migrations\n"
            "    run: |\n"
            "      npx supabase db push --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}\n"
            "    env:\n"
            "      SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}\n\n"
            "WRONG:\n"
            "  - run: alembic upgrade head  ← not the tool being used\n"
            "  - run: python manage.py migrate  ← Django pattern, not FastAPI/Supabase\n\n"
            "supabase/config.toml MUST be generated for local dev and CI to work. "
            "Use `supabase init` output format with the project_id from the SUPABASE_PROJECT_REF secret."
        ),

        _section("RULE 7 — SECRETS-REQUIRED.MD: COMPLETE AND ACTIONABLE"),
        (
            "secrets-required.md is the ONLY manual step for the developer. It must be complete.\n\n"
            "REQUIRED table format:\n"
            "  | Secret Name | Where to get it | Used in | Required for |\n"
            "  |---|---|---|---|\n"
            "  | SUPABASE_URL | Supabase Dashboard → Settings → API → Project URL | CI + deploy | All |\n"
            "  | SUPABASE_ANON_KEY | Supabase Dashboard → Settings → API → anon key | CI + deploy | All |\n"
            "  | STRIPE_SECRET_KEY | Stripe Dashboard → Developers → API keys | deploy | Staging, Prod |\n\n"
            "RULES:\n"
            "  - List EVERY secret referenced in ANY workflow file\n"
            "  - Explain exactly WHERE to find the value (URL, dashboard section, CLI command)\n"
            "  - Never leave a row with 'See docs' or 'Contact admin' — be specific\n"
            "  - Include instructions for SUPABASE_PROJECT_REF (it is the project ref ID, not the URL)"
        ),

        _section("RULE 8 — MAKEFILE: ALL TARGETS MUST BE RUNNABLE"),
        (
            "The Makefile is used by developers every day. Every target must work.\n\n"
            "REQUIRED targets (copy this structure):\n"
            "  .PHONY: dev migrate test e2e setup deploy-staging\n\n"
            "  setup:\n"
            "  \tcp .env.example .env.local\n"
            "  \tnpx supabase start\n"
            "  \t$(MAKE) migrate\n\n"
            "  dev:\n"
            "  \tdocker compose -f infra/docker-compose.yml up --build\n\n"
            "  migrate:\n"
            "  \tnpx supabase db push\n\n"
            "  test:\n"
            "  \tcd backend && pip install -r requirements-dev.txt -q && pytest\n"
            "  \tcd frontend && npm install --no-audit --no-fund -s && npm test\n\n"
            "  e2e:\n"
            "  \tcd frontend && npx playwright test\n\n"
            "NEVER use `npm ci` in the Makefile — use `npm install --no-audit --no-fund`.\n"
            "NEVER have a target that does nothing (`@echo 'TODO'`)."
        ),

        _section("RULE 9 — NO PLACEHOLDERS, NO TODOS, NO INCOMPLETE STEPS"),
        (
            "Every file you generate must be complete and immediately runnable.\n\n"
            "NEVER generate:\n"
            "  # TODO: add deploy step here\n"
            "  YOUR_DEPLOY_TOKEN_HERE\n"
            "  - run: # implement this\n"
            "  <your-project-name>    ← placeholder in fly.toml or vercel.json\n\n"
            "INSTEAD: use environment variable references everywhere:\n"
            "  ${{ secrets.FLY_APP_NAME }}      ← in GitHub Actions\n"
            "  ${FLY_APP_NAME}                   ← in docker-compose env blocks\n"
            "  $(FLY_APP_NAME)                   ← in Makefile\n\n"
            "Then add FLY_APP_NAME to secrets-required.md so the developer knows to set it. "
            "This is the correct pattern — not a placeholder, not a TODO."
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


def _delete_vite_artifacts(out_dir):
    """Remove Vite/CRA entry files from Next.js App Router projects.

    AI models trained on both Vite and Next.js frequently generate Vite-pattern
    entry files (src/App.tsx, src/main.tsx) and Vite-style page files
    (src/pages/*.tsx using react-router-dom) even when the project is Next.js.
    These cause TypeScript errors at build time and pollute the Next.js build.

    Detection: if package.json contains 'next' as a dependency AND src/app/
    exists (App Router), this is a Next.js project — delete Vite artifacts.
    """
    import json as _json
    import shutil as _shutil

    for root, dirs, files in os.walk(out_dir):
        dirs[:] = [d for d in dirs if d != "node_modules"]

        pkg = os.path.join(root, "package.json")
        if not os.path.isfile(pkg):
            continue

        try:
            meta = _json.loads(open(pkg, encoding="utf-8").read())
        except Exception:
            continue

        deps = {**meta.get("dependencies", {}), **meta.get("devDependencies", {})}
        is_nextjs = "next" in deps
        src_app = os.path.join(root, "src", "app")
        has_app_router = os.path.isdir(src_app)

        if not (is_nextjs and has_app_router):
            continue

        # Delete Vite/CRA entry files
        vite_files = [
            os.path.join(root, "src", "App.tsx"),
            os.path.join(root, "src", "App.jsx"),
            os.path.join(root, "src", "main.tsx"),
            os.path.join(root, "src", "main.jsx"),
            os.path.join(root, "src", "index.tsx"),
            os.path.join(root, "src", "index.jsx"),
            os.path.join(root, "index.html"),
            os.path.join(root, "vite.config.ts"),
            os.path.join(root, "vite.config.js"),
        ]
        for f in vite_files:
            if os.path.isfile(f):
                os.remove(f)

        # Delete src/pages/ if it contains react-router-dom imports
        src_pages = os.path.join(root, "src", "pages")
        if os.path.isdir(src_pages):
            has_router = False
            for pf in os.listdir(src_pages):
                pf_path = os.path.join(src_pages, pf)
                if os.path.isfile(pf_path):
                    try:
                        content = open(pf_path, encoding="utf-8").read()
                        if "react-router-dom" in content:
                            has_router = True
                            break
                    except OSError:
                        pass
            if has_router:
                _shutil.rmtree(src_pages)


def _fix_react_router_in_nextjs(out_dir):
    """Replace react-router-dom navigation APIs with next/navigation equivalents.

    AI models frequently generate react-router-dom inside Next.js components:
      import { NavLink }    from 'react-router-dom'  → next/link  + usePathname
      import { useNavigate } from 'react-router-dom'  → useRouter from next/navigation
      import { useLocation } from 'react-router-dom'  → usePathname from next/navigation
      import { Link }       from 'react-router-dom'   → next/link

    Transforms applied per-file:
      1. Rewrite the import statement
      2. Replace JSX / call-site usage with the Next.js equivalent

    Only runs on Next.js projects (package.json has 'next' dependency).
    """
    import json as _json, re as _re

    for root, dirs, files in os.walk(out_dir):
        dirs[:] = [d for d in dirs if d != "node_modules"]
        pkg = os.path.join(root, "package.json")
        if not os.path.isfile(pkg):
            continue
        try:
            meta = _json.loads(open(pkg, encoding="utf-8").read())
        except Exception:
            continue
        deps = {**meta.get("dependencies", {}), **meta.get("devDependencies", {})}
        if "next" not in deps:
            continue

        # Walk all .ts/.tsx files under this package root
        for froot, fdirs, ffiles in os.walk(root):
            fdirs[:] = [d for d in fdirs if d != "node_modules"]
            for fname in ffiles:
                if not fname.endswith((".ts", ".tsx")):
                    continue
                fpath = os.path.join(froot, fname)
                try:
                    text = open(fpath, encoding="utf-8").read()
                except OSError:
                    continue

                if "react-router-dom" not in text:
                    continue

                # Determine which symbols are imported
                rrd_import = _re.search(
                    r"import\s+\{([^}]+)\}\s+from\s+['\"]react-router-dom['\"]", text
                )
                if not rrd_import:
                    continue

                symbols = [s.strip() for s in rrd_import.group(1).split(",")]
                needs_link     = any(s in ("NavLink", "Link") for s in symbols)
                needs_router   = any(s in ("useNavigate",) for s in symbols)
                needs_pathname = any(s in ("NavLink", "useLocation") for s in symbols)

                new_imports = []
                if needs_link:
                    new_imports.append("import Link from 'next/link';")
                nav_hooks = []
                if needs_router:
                    nav_hooks.append("useRouter")
                if needs_pathname:
                    nav_hooks.append("usePathname")
                if nav_hooks:
                    new_imports.append(
                        f"import {{ {', '.join(nav_hooks)} }} from 'next/navigation';"
                    )

                # Replace the original import
                text = _re.sub(
                    r"import\s+\{[^}]+\}\s+from\s+['\"]react-router-dom['\"];?\n?",
                    "\n".join(new_imports) + "\n",
                    text,
                    count=1,
                )

                # Replace call-site usage
                text = text.replace("useNavigate()", "useRouter()")
                text = text.replace("const navigate = useRouter()", "const router = useRouter()")
                text = text.replace("navigate(", "router.push(")
                text = text.replace("useLocation()", "usePathname()")
                text = text.replace("const location = usePathname()", "const pathname = usePathname()")
                # NavLink to= → Link href=
                text = _re.sub(r"<NavLink\s+to=", "<Link href=", text)
                text = text.replace("</NavLink>", "</Link>")

                try:
                    open(fpath, "w", encoding="utf-8").write(text)
                except OSError:
                    pass


# Curated version map for packages frequently generated but omitted from package.json.
# Versions are conservative lower bounds — npm resolves the latest compatible.
_KNOWN_MISSING_DEPS: dict = {
    "@supabase/supabase-js": "^2.39.0",
    "elkjs": "^0.9.3",
    "web-worker": "^1.2.0",
    "d3": "^7.9.0",
    "framer-motion": "^11.0.0",
    "date-fns": "^3.6.0",
    "zod": "^3.23.0",
    "react-hook-form": "^7.51.0",
    "swr": "^2.2.5",
    "@tanstack/react-query": "^5.40.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.3.0",
    "class-variance-authority": "^0.7.0",
}


def _ensure_package_dependencies(out_dir):
    """Add commonly-omitted npm packages to package.json.

    Scans every .ts/.tsx file for bare package imports, compares against
    declared dependencies, and adds any recognised missing package to
    package.json using the version floor from _KNOWN_MISSING_DEPS.

    react-router-dom is explicitly excluded — it should never be a dependency
    of a Next.js project. Any file still using it after _fix_react_router_in_nextjs
    has already been rewritten.
    """
    import json as _json, re as _re

    _import_re = _re.compile(r"""from\s+['"](@?[a-zA-Z0-9][\w\-./]*)['"]""")
    _never_add = {"react-router-dom", "react", "react-dom", "next"}

    for root, dirs, files in os.walk(out_dir):
        dirs[:] = [d for d in dirs if d != "node_modules"]
        pkg_path = os.path.join(root, "package.json")
        if not os.path.isfile(pkg_path):
            continue

        try:
            meta = _json.loads(open(pkg_path, encoding="utf-8").read())
        except Exception:
            continue

        declared = set(
            {**meta.get("dependencies", {}), **meta.get("devDependencies", {})}.keys()
        )
        to_add: dict = {}

        for froot, fdirs, ffiles in os.walk(root):
            fdirs[:] = [d for d in fdirs if d != "node_modules"]
            for fname in ffiles:
                if not fname.endswith((".ts", ".tsx", ".js", ".jsx")):
                    continue
                try:
                    text = open(os.path.join(froot, fname), encoding="utf-8").read()
                except OSError:
                    continue
                for m in _import_re.finditer(text):
                    raw = m.group(1)
                    if raw.startswith(("./", "../", "@/")):
                        continue
                    parts = raw.split("/")
                    name = "/".join(parts[:2]) if raw.startswith("@") else parts[0]
                    if name in declared or name in _never_add or name in to_add:
                        continue
                    if name in _KNOWN_MISSING_DEPS:
                        to_add[name] = _KNOWN_MISSING_DEPS[name]

        if to_add:
            meta.setdefault("dependencies", {}).update(to_add)
            try:
                open(pkg_path, "w", encoding="utf-8").write(
                    _json.dumps(meta, indent=2) + "\n"
                )
            except OSError:
                pass


def _fix_css_var_in_jsx(out_dir):
    """Replace CSS var() used as JSX expression values — invalid JS that crashes SWC.

    AI models sometimes emit patterns like:
        rx={var(--radius-sm)}
        strokeWidth={var(--border-width)}
    These are CSS syntax, not JavaScript. `var` is a JS keyword, not a function,
    so the SWC parser fails immediately with "Unexpected token".

    Fix strategy:
    - SVG numeric attributes (rx, ry, r, cx, cy, strokeWidth, strokeDashoffset,
      strokeDasharray, x, y, x1, y1, x2, y2, offset): replace with sensible defaults.
    - Any other attribute: convert to string form `="var(--...)"` which at least
      compiles (even if the CSS var won't resolve for SVG presentation attrs).
    """
    import re as _re

    # Pattern: ={var(--<name>)}  (with optional whitespace inside braces)
    _css_var_re = _re.compile(r'=\{\s*var\((--[\w-]+)\)\s*\}')

    # SVG numeric attribute defaults — these can't take CSS string values
    _SVG_NUMERIC_DEFAULTS: dict = {
        "rx": "4", "ry": "4", "r": "4",
        "cx": "0", "cy": "0",
        "x": "0", "y": "0",
        "x1": "0", "y1": "0", "x2": "100", "y2": "0",
        "strokeWidth": "1", "stroke-width": "1",
        "strokeDashoffset": "0", "stroke-dashoffset": "0",
        "strokeDasharray": "4", "stroke-dasharray": "4",
        "offset": "0",
        "fontSize": "14", "font-size": "14",
    }

    def _replace_attr(m: "_re.Match") -> str:
        css_var_name = m.group(1)
        full_match = m.group(0)
        # Determine which attribute this belongs to by looking backwards in context
        # We can't easily do lookbehind for the attribute name in a general regex;
        # instead return string form — caller will do a second pass for numeric attrs
        return f'="{css_var_name}"'

    extensions = (".tsx", ".jsx", ".ts", ".js")
    for root, dirs, files in os.walk(out_dir):
        dirs[:] = [d for d in dirs if d != "node_modules"]
        for fname in files:
            if not fname.endswith(extensions):
                continue
            fpath = os.path.join(root, fname)
            try:
                text = open(fpath, encoding="utf-8").read()
            except OSError:
                continue
            if "var(--" not in text:
                continue

            # Two-pass replacement:
            # Pass 1: replace ={var(--...)} for SVG numeric attrs with a number
            new_text = text
            for attr_name, default_val in _SVG_NUMERIC_DEFAULTS.items():
                # Match: attr={var(--anything)}  (with optional whitespace)
                attr_re = _re.compile(
                    r'(?<=' + _re.escape(attr_name) + r')\s*=\s*\{\s*var\(--[\w-]+\)\s*\}'
                )
                new_text = attr_re.sub(f"={{{default_val}}}", new_text)

            # Pass 2: any remaining ={var(--...)} → convert to string form
            new_text = _css_var_re.sub(_replace_attr, new_text)

            if new_text != text:
                try:
                    open(fpath, "w", encoding="utf-8").write(new_text)
                except OSError:
                    pass


def _fix_ui_component_exports(out_dir):
    """Synthesize missing shadcn-style sub-component exports in UI component files.

    AI frequently generates consumer code that imports sub-components:
        import { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription }
            from '@/components/ui/card'
    but the generated card.tsx only exports the base Card component.

    This fixup scans all imports from @/components/ui/<name>, collects the union of
    named exports required, then appends any missing ones to the component file.

    Currently covers: Card sub-components, Button variants, Input variants.
    Extend _UI_SUBCOMPONENT_TEMPLATES as new patterns emerge.
    """
    import re as _re, json as _json

    # Map: (ui-file-basename, export-name) → code fragment to append
    _UI_SUBCOMPONENT_TEMPLATES: dict[tuple[str, str], str] = {
        ("card", "CardHeader"): (
            "\nexport const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = "
            "({ children, className }) => (\n"
            "  <div className={['card-header', className].filter(Boolean).join(' ')}>{children}</div>\n"
            ");\n"
        ),
        ("card", "CardContent"): (
            "\nexport const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = "
            "({ children, className }) => (\n"
            "  <div className={['card-content', className].filter(Boolean).join(' ')}>{children}</div>\n"
            ");\n"
        ),
        ("card", "CardFooter"): (
            "\nexport const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = "
            "({ children, className }) => (\n"
            "  <div className={['card-footer', className].filter(Boolean).join(' ')}>{children}</div>\n"
            ");\n"
        ),
        ("card", "CardTitle"): (
            "\nexport const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = "
            "({ children, className }) => (\n"
            "  <h3 className={['card-title', className].filter(Boolean).join(' ')}>{children}</h3>\n"
            ");\n"
        ),
        ("card", "CardDescription"): (
            "\nexport const CardDescription: React.FC<{ children: React.ReactNode; className?: string }> = "
            "({ children, className }) => (\n"
            "  <p className={['card-description', className].filter(Boolean).join(' ')}>{children}</p>\n"
            ");\n"
        ),
    }

    # regex: from '@/components/ui/<name>' with named imports
    _ui_import_re = _re.compile(
        r"import\s*\{([^}]+)\}\s*from\s*['\"]@/components/ui/(\w+)['\"]"
    )
    _export_name_re = _re.compile(r"\bexport\s+(?:const|function|class|type|interface)\s+(\w+)")

    for root, dirs, files in os.walk(out_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".next")]
        ui_dir = os.path.join(root, "src", "components", "ui")
        if not os.path.isdir(ui_dir):
            continue

        # Collect required exports per ui-file from all consumer files
        required: dict[str, set] = {}  # basename → set of export names needed
        src_dir = os.path.join(root, "src")
        for froot, fdirs, ffiles in os.walk(src_dir):
            fdirs[:] = [d for d in fdirs if d != "node_modules"]
            for fname in ffiles:
                if not fname.endswith((".tsx", ".ts", ".jsx", ".js")):
                    continue
                try:
                    text = open(os.path.join(froot, fname), encoding="utf-8").read()
                except OSError:
                    continue
                for m in _ui_import_re.finditer(text):
                    names_str, ui_basename = m.group(1), m.group(2)
                    names = [n.strip() for n in names_str.split(",") if n.strip()]
                    required.setdefault(ui_basename, set()).update(names)

        # For each ui file, append any missing sub-components
        for ui_basename, needed_names in required.items():
            # Look for the file (could be .tsx or .ts)
            ui_file = None
            for ext in (".tsx", ".ts", ".jsx", ".js"):
                candidate = os.path.join(ui_dir, ui_basename + ext)
                if os.path.isfile(candidate):
                    ui_file = candidate
                    break
            if not ui_file:
                continue

            try:
                text = open(ui_file, encoding="utf-8").read()
            except OSError:
                continue

            # Find what the file already exports
            already_exported = set(_export_name_re.findall(text))

            # Append missing sub-components
            appended = False
            for name in sorted(needed_names):
                if name in already_exported:
                    continue
                fragment = _UI_SUBCOMPONENT_TEMPLATES.get((ui_basename, name))
                if fragment and name not in text:
                    text += fragment
                    already_exported.add(name)
                    appended = True

            if appended:
                try:
                    open(ui_file, "w", encoding="utf-8").write(text)
                except OSError:
                    pass
        break  # only process first src/components/ui found


def _detect_language(service_dir):
    """Detect the backend language from the generated files in service_dir.

    Returns one of: 'python', 'node', 'go', 'ruby', 'java', 'rust', or None.
    Detection is by presence of the language's dependency manifest file.
    """
    markers = [
        ("python", "requirements.txt"),
        ("python", "setup.py"),
        ("python", "pyproject.toml"),
        ("node",   "package.json"),
        ("go",     "go.mod"),
        ("ruby",   "Gemfile"),
        ("java",   "pom.xml"),
        ("java",   "build.gradle"),
        ("rust",   "Cargo.toml"),
    ]
    for lang, filename in markers:
        if os.path.isfile(os.path.join(service_dir, filename)):
            return lang
    return None


def _find_service_dir(out_dir):
    """Find the actual service root (may be out_dir itself or one level down)."""
    # Check if out_dir is the service root
    if _detect_language(out_dir):
        return out_dir
    # Check one level down (e.g. generated as backend/backend/ or backend/app/)
    try:
        for entry in sorted(os.listdir(out_dir)):
            candidate = os.path.join(out_dir, entry)
            if os.path.isdir(candidate) and _detect_language(candidate):
                return candidate
    except OSError:
        pass
    return None


def _validate_build(out_dir, step):
    """Dispatch to the correct static validator for each build step.

    Detection is automatic:
      frontend    → always npm (Next.js/Vite)
      backend     → detect language from generated files, then validate accordingly
      integration → same as backend (may be any language)
      tests       → detect language, run test collection dry-run
      infra       → YAML lint + docker compose config

    All validators are non-blocking: files are kept even on failure.
    Errors are written to build-system.json and surfaced in the dashboard.
    """
    if step == "frontend":
        _validate_frontend(out_dir, step)
    elif step == "infra":
        _validate_infra(out_dir, step)
    elif step in ("backend", "integration", "tests"):
        service_dir = _find_service_dir(out_dir)
        if not service_dir:
            print(_LOG_PREFIX + f" [validate:{step}] No recognised language manifest found — skipping")
            return
        lang = _detect_language(service_dir)
        print(_LOG_PREFIX + f" [validate:{step}] Detected language: {lang or 'unknown'}")
        if lang == "python":
            _validate_python(service_dir, step)
        elif lang == "node":
            _validate_node_backend(service_dir, step)
        elif lang == "go":
            _validate_go(service_dir, step)
        elif lang == "ruby":
            _validate_ruby(service_dir, step)
        elif lang == "java":
            _validate_java(service_dir, step)
        else:
            print(_LOG_PREFIX + f" [validate:{step}] No validator for language '{lang}' — skipping")


def _run_subprocess(cmd, cwd, timeout=300, extra_env=None):
    """Run a subprocess, returning (returncode, combined_output)."""
    env = {**os.environ, **(extra_env or {})}
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env,
        )
        combined = (result.stdout or "") + "\n" + (result.stderr or "")
        return result.returncode, combined
    except subprocess.TimeoutExpired:
        return -1, f"Command timed out after {timeout}s: {' '.join(cmd)}"
    except FileNotFoundError:
        return -2, f"Command not found: {cmd[0]}"
    except Exception as e:
        return -3, str(e)


def _extract_error_lines(text, limit=60):
    """Extract error-relevant lines from build output."""
    _ERROR_KW = (
        "error", "Error", "ERROR", "Cannot find", "Module not found",
        "SyntaxError", "Type error", "Failed to compile", "ImportError",
        "ModuleNotFoundError", "NameError", "AttributeError", "TypeError",
        "FAILED", "ERRORS", "invalid", "Invalid", "not found", "not installed",
    )
    error_lines = [ln for ln in text.splitlines() if any(kw in ln for kw in _ERROR_KW)]
    return "\n".join(error_lines[:limit]) if error_lines else text[:3000]


def _validate_frontend(out_dir, step):
    """Validate frontend: npm install + npm run build."""
    pkg_json = os.path.join(out_dir, "package.json")
    if not os.path.isfile(pkg_json):
        return

    print(_LOG_PREFIX + " [validate:frontend] Running npm install + npm run build...")

    rc, out = _run_subprocess(["npm", "install", "--no-audit", "--no-fund"], out_dir, timeout=300)
    if rc != 0 and rc != -2:
        _record_build_validation_error(step, "npm install failed:\n" + out[:3000])
        return
    if rc == -2:
        print(_LOG_PREFIX + " [validate:frontend] npm not found — skipping")
        return

    rc, out = _run_subprocess(
        ["npm", "run", "build"], out_dir, timeout=360,
        extra_env={"NEXT_TELEMETRY_DISABLED": "1"},
    )
    if rc != 0:
        summary = _extract_error_lines(out)
        _record_build_validation_error(step, summary)
        print(_LOG_PREFIX + " [validate:frontend] BUILD FAILED — see build status for details")
        print(_LOG_PREFIX + " [validate:frontend] First errors:\n" + summary[:500])
    else:
        print(_LOG_PREFIX + " [validate:frontend] Build succeeded.")
        _clear_build_validation_error(step)


def _validate_python(service_dir, step):
    """Validate Python: pip install (no-deps) + py_compile every .py file."""
    print(_LOG_PREFIX + f" [validate:{step}] Checking Python syntax (pip + py_compile)...")

    rc, out = _run_subprocess(
        ["pip", "install", "--quiet", "--no-deps", "-r", "requirements.txt"],
        service_dir, timeout=180,
    )
    if rc == -2:
        print(_LOG_PREFIX + f" [validate:{step}] pip not found — skipping")
        return
    if rc != 0:
        _record_build_validation_error(step, "pip install failed:\n" + out[:3000])
        print(_LOG_PREFIX + f" [validate:{step}] pip install FAILED")
        return

    errors = []
    _skip_dirs = {"__pycache__", ".venv", "venv", "node_modules", ".git"}
    for root, dirs, files in os.walk(service_dir):
        dirs[:] = [d for d in dirs if d not in _skip_dirs]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            rc2, out2 = _run_subprocess(["python", "-m", "py_compile", fpath], service_dir, timeout=15)
            if rc2 not in (0, -2) and out2.strip():
                errors.append(f"{os.path.relpath(fpath, service_dir)}: {out2.strip()[:300]}")

    if errors:
        summary = f"Syntax errors in {len(errors)} file(s):\n" + "\n".join(errors[:20])
        _record_build_validation_error(step, summary)
        print(_LOG_PREFIX + f" [validate:{step}] SYNTAX ERRORS — see build status")
    else:
        print(_LOG_PREFIX + f" [validate:{step}] All Python files compile clean.")
        _clear_build_validation_error(step)


def _validate_node_backend(service_dir, step):
    """Validate Node.js/TypeScript backend: npm install + tsc --noEmit (if tsconfig exists)."""
    print(_LOG_PREFIX + f" [validate:{step}] Checking Node.js/TypeScript (npm install + tsc)...")

    rc, out = _run_subprocess(
        ["npm", "install", "--no-audit", "--no-fund"], service_dir, timeout=300,
    )
    if rc == -2:
        print(_LOG_PREFIX + f" [validate:{step}] npm not found — skipping")
        return
    if rc != 0:
        _record_build_validation_error(step, "npm install failed:\n" + out[:3000])
        return

    # TypeScript type-check if tsconfig present
    tsconfig = os.path.join(service_dir, "tsconfig.json")
    if os.path.isfile(tsconfig):
        rc, out = _run_subprocess(
            ["npx", "--yes", "tsc", "--noEmit"], service_dir, timeout=180,
        )
        if rc != 0:
            summary = _extract_error_lines(out)
            _record_build_validation_error(step, "TypeScript errors:\n" + summary)
            print(_LOG_PREFIX + f" [validate:{step}] TYPESCRIPT ERRORS — see build status")
            return

    # If there's an npm build script, run it
    try:
        import json as _json
        meta = _json.loads(open(os.path.join(service_dir, "package.json"), encoding="utf-8").read())
        if "build" in meta.get("scripts", {}):
            rc, out = _run_subprocess(["npm", "run", "build"], service_dir, timeout=300)
            if rc != 0:
                summary = _extract_error_lines(out)
                _record_build_validation_error(step, "npm run build failed:\n" + summary)
                print(_LOG_PREFIX + f" [validate:{step}] BUILD FAILED — see build status")
                return
    except Exception:
        pass

    print(_LOG_PREFIX + f" [validate:{step}] Node.js validation passed.")
    _clear_build_validation_error(step)


def _validate_go(service_dir, step):
    """Validate Go: go build ./... to catch compilation errors."""
    print(_LOG_PREFIX + f" [validate:{step}] Checking Go (go build)...")

    rc, out = _run_subprocess(["go", "build", "./..."], service_dir, timeout=120)
    if rc == -2:
        print(_LOG_PREFIX + f" [validate:{step}] go not found — skipping")
        return
    if rc != 0:
        summary = _extract_error_lines(out)
        _record_build_validation_error(step, "go build failed:\n" + summary)
        print(_LOG_PREFIX + f" [validate:{step}] GO BUILD FAILED — see build status")
    else:
        print(_LOG_PREFIX + f" [validate:{step}] go build passed.")
        _clear_build_validation_error(step)


def _validate_ruby(service_dir, step):
    """Validate Ruby: bundle install + ruby -e 'require' syntax check on .rb files."""
    print(_LOG_PREFIX + f" [validate:{step}] Checking Ruby (bundle install + syntax check)...")

    rc, out = _run_subprocess(["bundle", "install", "--quiet"], service_dir, timeout=180)
    if rc == -2:
        print(_LOG_PREFIX + f" [validate:{step}] bundle not found — skipping")
        return
    if rc != 0:
        _record_build_validation_error(step, "bundle install failed:\n" + out[:3000])
        return

    errors = []
    _skip_dirs = {".git", "tmp", "log", "node_modules", ".bundle"}
    for root, dirs, files in os.walk(service_dir):
        dirs[:] = [d for d in dirs if d not in _skip_dirs]
        for fname in files:
            if not fname.endswith(".rb"):
                continue
            fpath = os.path.join(root, fname)
            rc2, out2 = _run_subprocess(["ruby", "-c", fpath], service_dir, timeout=10)
            if rc2 not in (0, -2) and out2.strip() and "Syntax OK" not in out2:
                errors.append(f"{os.path.relpath(fpath, service_dir)}: {out2.strip()[:300]}")

    if errors:
        summary = f"Ruby syntax errors in {len(errors)} file(s):\n" + "\n".join(errors[:20])
        _record_build_validation_error(step, summary)
        print(_LOG_PREFIX + f" [validate:{step}] RUBY SYNTAX ERRORS — see build status")
    else:
        print(_LOG_PREFIX + f" [validate:{step}] Ruby syntax check passed.")
        _clear_build_validation_error(step)


def _validate_java(service_dir, step):
    """Validate Java: mvn compile or gradle compileJava."""
    print(_LOG_PREFIX + f" [validate:{step}] Checking Java (compile)...")

    if os.path.isfile(os.path.join(service_dir, "pom.xml")):
        rc, out = _run_subprocess(
            ["mvn", "compile", "-q", "--batch-mode"], service_dir, timeout=300,
        )
        tool = "mvn compile"
    else:
        rc, out = _run_subprocess(
            ["./gradlew", "compileJava", "--quiet"], service_dir, timeout=300,
        )
        tool = "gradle compileJava"

    if rc == -2:
        print(_LOG_PREFIX + f" [validate:{step}] Build tool not found — skipping")
        return
    if rc != 0:
        summary = _extract_error_lines(out)
        _record_build_validation_error(step, f"{tool} failed:\n" + summary)
        print(_LOG_PREFIX + f" [validate:{step}] JAVA COMPILE FAILED — see build status")
    else:
        print(_LOG_PREFIX + f" [validate:{step}] Java compile passed.")
        _clear_build_validation_error(step)


def _validate_tests(out_dir, step):
    """Validate tests: detect language and run test collection dry-run."""
    service_dir = _find_service_dir(out_dir)
    if not service_dir:
        print(_LOG_PREFIX + " [validate:tests] No service dir found — skipping")
        return

    lang = _detect_language(service_dir)
    print(_LOG_PREFIX + f" [validate:tests] Detected language: {lang or 'unknown'}")

    if lang == "python":
        _validate_python_tests(service_dir)
    elif lang == "node":
        _validate_node_tests(service_dir)
    elif lang == "go":
        _validate_go_tests(service_dir)
    else:
        # Fall back to generic syntax check for the detected language
        if lang:
            _validate_go(service_dir, step) if lang == "go" else _validate_python(service_dir, step)


def _validate_python_tests(service_dir):
    """Python tests: pip install + pytest --collect-only."""
    step = "tests"
    req_dev = os.path.join(service_dir, "requirements-dev.txt")
    req_file = req_dev if os.path.isfile(req_dev) else os.path.join(service_dir, "requirements.txt")

    rc, out = _run_subprocess(
        ["pip", "install", "--quiet", "--no-deps", "-r", os.path.basename(req_file)],
        service_dir, timeout=180,
    )
    if rc == -2:
        print(_LOG_PREFIX + " [validate:tests] pip not found — skipping")
        return
    if rc != 0:
        _record_build_validation_error(step, "pip install failed:\n" + out[:3000])
        return

    rc, out = _run_subprocess(
        ["python", "-m", "pytest", "--collect-only", "-q", "--no-header"],
        service_dir, timeout=60,
    )
    if rc == -2:
        print(_LOG_PREFIX + " [validate:tests] pytest not found — skipping")
        return
    if rc != 0:
        summary = _extract_error_lines(out)
        _record_build_validation_error(step, "Test collection failed:\n" + summary)
        print(_LOG_PREFIX + " [validate:tests] TEST COLLECTION FAILED — see build status")
        print(_LOG_PREFIX + " [validate:tests] First errors:\n" + summary[:400])
    else:
        print(_LOG_PREFIX + " [validate:tests] Test collection succeeded.")
        _clear_build_validation_error(step)


def _validate_node_tests(service_dir):
    """Node.js tests: npm install + npx tsc --noEmit."""
    step = "tests"
    rc, out = _run_subprocess(
        ["npm", "install", "--no-audit", "--no-fund"], service_dir, timeout=300,
    )
    if rc == -2:
        print(_LOG_PREFIX + " [validate:tests] npm not found — skipping")
        return
    if rc != 0:
        _record_build_validation_error(step, "npm install failed:\n" + out[:3000])
        return

    if os.path.isfile(os.path.join(service_dir, "tsconfig.json")):
        rc, out = _run_subprocess(["npx", "--yes", "tsc", "--noEmit"], service_dir, timeout=120)
        if rc != 0:
            summary = _extract_error_lines(out)
            _record_build_validation_error(step, "TypeScript errors in tests:\n" + summary)
            print(_LOG_PREFIX + " [validate:tests] TYPESCRIPT ERRORS — see build status")
            return

    print(_LOG_PREFIX + " [validate:tests] Node.js test validation passed.")
    _clear_build_validation_error(step)


def _validate_go_tests(service_dir):
    """Go tests: go test -run '^$' ./... (compile all test files, run none)."""
    step = "tests"
    rc, out = _run_subprocess(
        ["go", "test", "-run", "^$", "./..."], service_dir, timeout=120,
    )
    if rc == -2:
        print(_LOG_PREFIX + " [validate:tests] go not found — skipping")
        return
    if rc != 0:
        summary = _extract_error_lines(out)
        _record_build_validation_error(step, "go test compile failed:\n" + summary)
        print(_LOG_PREFIX + " [validate:tests] GO TEST COMPILE FAILED — see build status")
    else:
        print(_LOG_PREFIX + " [validate:tests] Go test compilation passed.")
        _clear_build_validation_error(step)


def _validate_infra(out_dir, step):
    """Validate infra: docker compose config + YAML syntax check."""
    # Look for docker-compose.yml in out_dir or one level down
    compose_file = None
    for candidate_name in ("docker-compose.yml", "docker-compose.yaml"):
        for search_dir in [out_dir] + [os.path.join(out_dir, d) for d in os.listdir(out_dir)
                                        if os.path.isdir(os.path.join(out_dir, d))]:
            candidate = os.path.join(search_dir, candidate_name)
            if os.path.isfile(candidate):
                compose_file = candidate
                break
        if compose_file:
            break

    # YAML syntax check on all .yml/.yaml files
    yaml_errors = []
    try:
        import yaml as _yaml
        for root, dirs, files in os.walk(out_dir):
            dirs[:] = [d for d in dirs if d != "node_modules"]
            for fname in files:
                if not fname.endswith((".yml", ".yaml")):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        _yaml.safe_load_all(f.read())
                except _yaml.YAMLError as e:
                    rel = os.path.relpath(fpath, out_dir)
                    yaml_errors.append(f"{rel}: {str(e)[:200]}")
                except OSError:
                    pass
    except ImportError:
        pass  # PyYAML not available — skip YAML lint

    if yaml_errors:
        summary = f"YAML syntax errors in {len(yaml_errors)} file(s):\n" + "\n".join(yaml_errors[:20])
        _record_build_validation_error(step, summary)
        print(_LOG_PREFIX + " [validate:infra] YAML ERRORS — see build status for details")
        return

    # docker compose config (structural validation) if compose file found
    if compose_file:
        compose_dir = os.path.dirname(compose_file)
        compose_fname = os.path.basename(compose_file)
        print(_LOG_PREFIX + " [validate:infra] Running docker compose config...")
        rc, out = _run_subprocess(
            ["docker", "compose", "-f", compose_fname, "config", "--quiet"],
            compose_dir, timeout=60,
        )
        if rc == -2:
            print(_LOG_PREFIX + " [validate:infra] docker not found — skipping compose validation")
        elif rc != 0:
            summary = _extract_error_lines(out)
            _record_build_validation_error(step, "docker compose config failed:\n" + summary)
            print(_LOG_PREFIX + " [validate:infra] COMPOSE CONFIG FAILED — see build status")
            return
        else:
            print(_LOG_PREFIX + " [validate:infra] docker compose config passed.")

    if not yaml_errors:
        print(_LOG_PREFIX + " [validate:infra] Infra validation passed.")
        _clear_build_validation_error(step)


def _record_build_validation_error(step, error_text):
    status = load_build_status()
    entry = status.get(step, {})
    entry["build_validation_error"] = error_text[:4000]
    status[step] = entry
    with open(BUILD_STATUS_FILE, "w", encoding=FILE_ENCODING) as f:
        import json as _json
        _json.dump(status, f, indent=2)


def _clear_build_validation_error(step):
    status = load_build_status()
    entry = status.get(step, {})
    entry.pop("build_validation_error", None)
    status[step] = entry
    with open(BUILD_STATUS_FILE, "w", encoding=FILE_ENCODING) as f:
        import json as _json
        _json.dump(status, f, indent=2)


def _post_generate_fixups(out_dir):
    """Run automatic fixups on generated code after files are written."""
    _delete_vite_artifacts(out_dir)
    _fix_react_router_in_nextjs(out_dir)
    _fix_css_var_in_jsx(out_dir)
    _fix_ui_component_exports(out_dir)
    _ensure_package_dependencies(out_dir)
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

    # Deterministic fixups (correct AI-generated code mistakes)
    _post_generate_fixups(out_dir)
    # Note: _validate_build() exists for opt-in use but is NOT called automatically.
    # Running npm install / pip install post-generation triggers macOS TCC permission
    # prompts (Desktop/Documents/Downloads access) and takes 3-5 min. The prompt
    # rules are the primary protection against bad generated code.

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_runner.py <step>")
        sys.exit(1)
    success = run_step(sys.argv[1])
    sys.exit(0 if success else 1)
