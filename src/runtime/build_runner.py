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


def _validate_build(out_dir, step):
    """Run `npm run build` in the generated directory and surface errors clearly.

    This catches TypeScript errors, missing imports, and JSX syntax failures that
    only manifest at build time — not during file generation.

    The validation:
    1. Runs `npm install --no-audit --no-fund` to install deps
    2. Runs `npm run build` (which runs tsc + Next.js/Vite compilation)
    3. If it fails, logs the first 50 lines of error output to the build status
    4. Marks the step as having a build_validation_error (non-blocking — files are kept)

    Why non-blocking: the files are already written and may be useful even if the build
    fails. The developer can see the error, fix the generation prompt, and regenerate.
    The status surfaces the error prominently in the dashboard.
    """
    # Only validate frontend steps — backend/infra use different build systems
    _VALIDATABLE_STEPS = {"frontend"}
    if step not in _VALIDATABLE_STEPS:
        return

    # Check if this looks like a Node.js project
    pkg_json = os.path.join(out_dir, "package.json")
    if not os.path.isfile(pkg_json):
        return

    print(_LOG_PREFIX + " [validate] Running npm install + npm run build to verify generated code...")

    try:
        # Install deps first
        install_result = subprocess.run(
            ["npm", "install", "--no-audit", "--no-fund"],
            cwd=out_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if install_result.returncode != 0:
            _record_build_validation_error(
                step,
                "npm install failed:\n" + (install_result.stderr or install_result.stdout)[:3000],
            )
            return

        # Run the build
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=out_dir,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "NEXT_TELEMETRY_DISABLED": "1"},
        )

        if build_result.returncode != 0:
            combined = (build_result.stdout or "") + "\n" + (build_result.stderr or "")
            # Extract meaningful lines: errors, not noise
            error_lines = [
                ln for ln in combined.splitlines()
                if any(kw in ln for kw in ("error", "Error", "ERROR", "Cannot find", "Module not found", "SyntaxError", "Type error", "Failed to compile"))
            ]
            summary = "\n".join(error_lines[:60]) if error_lines else combined[:3000]
            _record_build_validation_error(step, summary)
            print(_LOG_PREFIX + " [validate] BUILD FAILED — see build status for details")
            print(_LOG_PREFIX + " [validate] First errors:\n" + summary[:500])
        else:
            print(_LOG_PREFIX + " [validate] Build succeeded — generated code is valid.")
            _clear_build_validation_error(step)

    except subprocess.TimeoutExpired:
        _record_build_validation_error(step, "Build validation timed out after 5 minutes")
    except FileNotFoundError:
        print(_LOG_PREFIX + " [validate] npm not found — skipping build validation")
    except Exception as e:
        print(_LOG_PREFIX + " [validate] Validation error (non-fatal): " + str(e))


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

    # Pass 1: deterministic fixups (correct AI-generated code mistakes)
    _post_generate_fixups(out_dir)

    # Pass 2: build validation (run actual npm build to surface any remaining errors)
    _validate_build(out_dir, step)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_runner.py <step>")
        sys.exit(1)
    success = run_step(sys.argv[1])
    sys.exit(0 if success else 1)
