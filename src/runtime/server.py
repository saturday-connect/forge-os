import os
import sys
import json
import logging
import subprocess
import shutil
import tempfile
import time
import threading
import re
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from constants import (
    AI_POLL_TIMEOUT_SECS,
    ALL_GATE_NAMES,
    ALL_STAGE_DIRS,
    BUILD_STATUS_COMMITTED,
    BUILD_STATUS_PUSHED,
    BUILD_STATUS_PR_CREATED,
    BUILD_STATUS_MERGED,
    BUILD_STEP_DIRS,
    BUILD_STEP_KEYS,
    CACHE_CONTROL_NO_CACHE,
    CONTENT_TYPE_HTML,
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_PLAIN,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_ORIGIN,
    DEFAULT_BRANCH,
    DEFAULT_BRANCH_PREFIX,
    DEFAULT_PORT,
    DEFAULT_TOOL,
    DELIVERY_SCAN_DIRS,
    DELIVERY_SCAN_FILES,
    DEPARTMENTS,
    DESCRIPTION_MAX_LEN,
    DIFF_CHAR_LIMIT,
    DIFF_HEADER_LINES,
    DIR_AGENTS,
    DIR_BUILD,
    DIR_GATES,
    DIR_RAW_INPUT,
    ERROR_PREVIEW_LEN,
    FILE_BUILD_IN_PROGRESS,
    FILE_BUILD_REVIEW,
    FILE_BUILD_SYSTEM,
    FILE_DISTILL_RESULT,
    FILE_ENCODING,
    FILE_PROJECT_STATE,
    FILE_REVIEWS,
    FILE_STATUS,
    GATE_STAGE_MAP,
    GATE_STATUS_APPROVED,
    GATE_STATUS_PASSED,
    GATE_STATUS_PENDING,
    GEMINI_ARG_MODEL,
    GEMINI_ARG_PROMPT,
    GEMINI_ARG_SKIP_TRUST,
    GENERATE_TIMEOUT_SECS,
    GIT_COMMIT_EMAIL,
    GIT_COMMIT_NAME,
    GIT_TIMEOUT_SECS,
    GITHUB_ACCEPT_HEADER,
    GITHUB_ACCEPT_V3_HEADER,
    GITHUB_API_VERSION,
    GITHUB_CONTENT_TYPE,
    GITHUB_USER_AGENT,
    HTTP_CHECK_TIMEOUT_SECS,
    ISSUE_DEFAULT_PRIORITY,
    ISSUE_DEFAULT_TYPE,
    ISSUE_ID_PREFIX,
    ISSUE_STATUS_OPEN,
    LARGE_CHANGESET_THRESHOLD,
    MARKDOWN_EXTENSION,
    MAX_BODY_BYTES,
    NETWORK_TIMEOUT_SECS,
    ORG_SUBDIRS,
    PAT_SIGNAL_PATH,
    PHASE_BUILD,
    PHASE_DEPLOY,
    PHASE_GENERATE,
    PHASE_INPUT,
    PHASE_REVIEW,
    PHASE_STATUS_ACTIVE,
    PHASE_STATUS_BUILT,
    PHASE_STATUS_DEPLOYED,
    PHASE_STATUS_PENDING,
    PIPELINE_STAGE_NAMES,
    PROJECT_STATUS_ACTIVE,
    PROJECT_STATUS_ARCHIVED,
    QUOTA_ERROR_MARKERS,
    REVIEW_EMPTY,
    REVIEW_NEEDS_REVIEW,
    REVIEW_REVIEWED,
    SECRETS_SEARCH_PATHS,
    SOURCE_MARKER,
    SOURCE_MARKER_END,
    SPEC_FILES_FOR_REVIEW,
    SPEC_SNIPPET_MAX_CHARS,
    STAGE_DIR_MAP,
    STATUS_DISTILLING,
    STATUS_ERROR,
    STATUS_FIXING,
    STATUS_IDLE,
    STATUS_PENDING,
    STATUS_RUNNING,
    TOOL_CLAUDE,
    TOOL_GEMINI,
    USER_FILE_PATH,
    VALID_STAGE_PREFIX_COUNT,
    VERDICT_APPROVE,
    VERDICT_APPROVE_WITH_NOTES,
    VERDICT_ERROR,
    VERDICT_REQUEST_CHANGES,
    VERDICT_UNKNOWN,
    CLAUDE_ARG_PROMPT,
    CLAUDE_ARG_OUTPUT_FORMAT,
    CLAUDE_OUTPUT_TEXT,
    VERSION_TIMESTAMP_FORMAT,
    INDEX_SCHEMA_VERSION,
    STATE_SCHEMA_VERSION,
    DIR_RUNS,
    KB_BRANCH_DISTILL_PREFIX,
    KB_BRANCH_EXPORT_PREFIX,
    KB_GLOBAL_DECISIONS,
    KB_GLOBAL_LEARNINGS,
    KB_GLOBAL_PATTERNS,
    KB_PROJECTS_DIR,
    KB_STATUS_DISTILLING,
    KB_STATUS_DONE,
    KB_STATUS_ERROR,
    KB_STATUS_EXPORTING,
    FILE_KB_STATE,
    FILE_CONSISTENCY_CHECK,
    CONSISTENCY_CHECK_MAX_DOWNSTREAM,
    CONSISTENCY_CHECK_DOC_CHARS,
    CONSISTENCY_CHECK_FIXED_CHARS,
    FORGE_PHASE_ID_ENV,
    FORGE_PHASE_NAME_ENV,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [server] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("forge.server")

# ---------------------------------------------------------------------------
# PATH augmentation — Electron launches with a minimal macOS PATH that omits
# Homebrew, NVM, and user-local bin dirs. Prepend known locations so that
# shutil.which() and all subprocess calls can find gemini, claude, codex, etc.
# ---------------------------------------------------------------------------
import glob as _glob
_nvm_node_bins = sorted(_glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin")), reverse=True)
_extra_paths = [
    *_nvm_node_bins,
    os.path.expanduser("~/.npm-global/bin"),
    os.path.expanduser("~/.npm/bin"),
    os.path.expanduser("~/.local/bin"),
    "/opt/homebrew/bin",
    "/opt/homebrew/sbin",
    "/usr/local/bin",
]
os.environ["PATH"] = os.pathsep.join(
    [p for p in _extra_paths if os.path.isdir(p)] + [os.environ.get("PATH", "")]
)
logger.info("PATH augmented: %s", os.environ["PATH"])

# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------
_state_lock    = threading.Lock()
_reviews_lock  = threading.Lock()
_index_lock    = threading.Lock()
_generate_lock = threading.Lock()   # guards _active_generate_proc
_active_generate_proc = None        # current Popen for the running forge-generate subprocess

# Module-level security constants — read from env at startup
FORGE_TOKEN = os.environ.get("FORGE_TOKEN", "")
GIT_PAT = os.environ.get("FORGE_GIT_PAT", "")

REPO_ROOT = os.path.abspath(os.environ.get("FORGE_REPO_ROOT", os.environ.get("AEOS_REPO_ROOT", ".")))
ORCHESTRATOR_ROOT = os.path.abspath(os.environ.get("FORGE_ORCHESTRATOR_ROOT", REPO_ROOT))
_data_dir = os.environ.get("FORGE_DATA_DIR", "")
FORGE_DIR = os.path.abspath(_data_dir) if _data_dir else os.path.join(REPO_ROOT, ".forge")
# FORGE_PROJECTS_ROOT overrides computed path — Electron passes ~/.forge/projects explicitly
_projects_root_override = os.environ.get("FORGE_PROJECTS_ROOT", "")
PROJECTS_ROOT = os.path.abspath(os.path.expanduser(_projects_root_override)) if _projects_root_override else os.path.join(ORCHESTRATOR_ROOT, ".projects")
PROJECTS_INDEX_FILE = os.path.join(PROJECTS_ROOT, "index.json")

KNOWN_TOOLS = {}  # __FORGE_KNOWN_TOOLS__

DISTILL_KNOWLEDGE_PROMPT = """# Knowledge Base Distillation

You are distilling product and engineering documents into reusable organizational knowledge.

**Project:** {project_name}

**Task:**
Analyze the following reviewed documents and extract knowledge reusable for future projects. Focus on GENERAL, REUSABLE knowledge — not project-specific details.

Do NOT include:
- Specific company or product names
- Infrastructure hostnames, IP addresses, API keys
- Business logic specific to this project
- Team member names or contact details

**Documents:**
{doc_content}

---

Respond with EXACTLY these three sections. If a section has nothing relevant, write "Nothing to extract." under the heading.

## Patterns

Reusable architecture and design patterns. Include: pattern name, when to use it, trade-offs.

## Decisions

Key architectural or product decisions. Use this format:
**Decision:** [what was decided]
**Context:** [why this was needed]
**Rationale:** [why this approach over alternatives]

## Learnings

Cross-project lessons — failure modes, gotchas, invariants, principles.
Format: **[Topic]**: [what to do or avoid and why]
"""

CONSISTENCY_CHECK_PROMPT = """The following document was updated based on a critique:

=== UPDATED: {fixed_rel} ===
{fixed_content}

Review each downstream document listed below. Identify ONLY those that now contain specific inconsistencies, gaps, or outdated information caused by the update above.

Be specific — name the exact claim, section, or assumption that conflicts.
If a document is fully consistent with the update, do NOT mention it.

Format each finding as:
FILE: <relative_path>
REASON: <1-2 sentences on what specifically needs updating>

Downstream documents:
{downstream_block}
"""

REVIEWS_FILE = os.path.join(FORGE_DIR, FILE_REVIEWS)
STATE_FILE = os.path.join(FORGE_DIR, FILE_PROJECT_STATE)
RAW_INPUT_DIR = os.path.join(FORGE_DIR, DIR_RAW_INPUT)
FORGE_VERSION = os.environ.get("FORGE_VERSION", "unknown")
FORGE_SCRIPT = os.environ.get("FORGE_SCRIPT", "")

# Phase 4+5: user profile
USER_FILE = os.path.expanduser(USER_FILE_PATH)


# ---------------------------------------------------------------------------
# Project root management
# ---------------------------------------------------------------------------

def set_project_root(project_root, data_dir=None):
    global REPO_ROOT, FORGE_DIR, REVIEWS_FILE, STATE_FILE, RAW_INPUT_DIR
    REPO_ROOT = os.path.abspath(project_root)
    _dd = None
    # 1. Dotfile always takes priority — it is the authoritative pointer written by forge init.
    dotfile = os.path.join(REPO_ROOT, ".forge")
    if os.path.isfile(dotfile):
        try:
            _meta = json.loads(open(dotfile, "r", encoding="utf-8").read())
            _dd = os.path.expanduser(_meta.get("data_dir", ""))
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    # 2. Caller-supplied data_dir (from index entry) — fallback when dotfile is missing.
    if not _dd and data_dir:
        _dd = os.path.expanduser(data_dir) if data_dir.startswith("~") else data_dir
        logger.info("set_project_root: dotfile missing, using index data_dir: %s", _dd)
    # 3. Inherited env var — last resort; stale after the first project switch.
    if not _dd:
        _dd = os.environ.get("FORGE_DATA_DIR", "")
    FORGE_DIR = os.path.abspath(_dd) if _dd else os.path.join(REPO_ROOT, ".forge")

    # Recover gracefully when data_dir was deleted (e.g. manual cleanup, broken
    # uninstaller).  Re-create the directory skeleton and copy scripts from the
    # running server's own directory so the dashboard stays accessible.
    if not os.path.isdir(FORGE_DIR):
        logger.warning("set_project_root: data_dir missing, recreating: %s", FORGE_DIR)
        try:
            import shutil as _shutil
            for _sub in ("scripts", DIR_RAW_INPUT, DIR_RUNS, DIR_AGENTS, DIR_GATES):
                os.makedirs(os.path.join(FORGE_DIR, _sub), exist_ok=True)
            # Copy current runtime scripts from the server's own location
            _src_scripts = os.path.dirname(os.path.abspath(__file__))
            _dst_scripts = os.path.join(FORGE_DIR, "scripts")
            for _fname in ("server.py", "stage_runner.py", "run.py", "build_runner.py",
                           "constants.py", "validate_gates.py", "dashboard.html"):
                _src = os.path.join(_src_scripts, _fname)
                if os.path.exists(_src):
                    _shutil.copy2(_src, os.path.join(_dst_scripts, _fname))
        except OSError as exc:
            logger.warning("set_project_root: recovery failed: %s", exc)

    REVIEWS_FILE = os.path.join(FORGE_DIR, FILE_REVIEWS)
    STATE_FILE = os.path.join(FORGE_DIR, FILE_PROJECT_STATE)
    RAW_INPUT_DIR = os.path.join(FORGE_DIR, DIR_RAW_INPUT)
    os.environ["AEOS_REPO_ROOT"] = REPO_ROOT
    os.environ["FORGE_REPO_ROOT"] = REPO_ROOT
    os.environ["FORGE_DATA_DIR"] = FORGE_DIR


def ensure_projects_root():
    os.makedirs(PROJECTS_ROOT, exist_ok=True)


def slugify_project_name(name):
    raw = (name or "").strip().lower()
    out = []
    prev_dash = False
    for ch in raw:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append("-")
                prev_dash = True
    slug = "".join(out).strip("-")
    return slug or "project"


def default_projects_index():
    return {"active_project_id": "", "projects": [], "_schema_version": INDEX_SCHEMA_VERSION}


def _migrate_index_schema(data, from_version):
    """Migrate index.json from from_version to INDEX_SCHEMA_VERSION.
    Each branch should be additive and idempotent. v0→v1 is a no-op."""
    return data


def _migrate_project_state_schema(data, from_version):
    """Migrate project-state.json from from_version to STATE_SCHEMA_VERSION.
    Each branch should be additive and idempotent. v0→v1 is a no-op."""
    return data


def load_projects_index():
    with _index_lock:
        ensure_projects_root()
        if os.path.exists(PROJECTS_INDEX_FILE):
            try:
                with open(PROJECTS_INDEX_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and isinstance(data.get("projects"), list):
                    data.setdefault("active_project_id", "")
                    file_version = data.get("_schema_version", 0)
                    if file_version < INDEX_SCHEMA_VERSION:
                        data = _migrate_index_schema(data, file_version)
                        data["_schema_version"] = INDEX_SCHEMA_VERSION
                        try:
                            with open(PROJECTS_INDEX_FILE, "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2)
                        except OSError as exc:
                            logger.warning("load_projects_index migrate write: %s", exc)
                    return data
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("load_projects_index: %s", exc)
        return default_projects_index()


def save_projects_index(index_data):
    with _index_lock:
        ensure_projects_root()
        index_data["_schema_version"] = INDEX_SCHEMA_VERSION
        with open(PROJECTS_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        try:
            os.chmod(PROJECTS_INDEX_FILE, 0o600)
        except OSError as exc:
            logger.warning("save_projects_index chmod: %s", exc)


def ensure_unique_slug(index_data, base_slug):
    existing = {p.get("slug", "") for p in index_data.get("projects", [])}
    if base_slug not in existing:
        return base_slug
    i = 2
    while True:
        candidate = f"{base_slug}-{i}"
        if candidate not in existing:
            return candidate
        i += 1


def get_active_project(index_data):
    active_id = index_data.get("active_project_id", "")
    for p in index_data.get("projects", []):
        if p.get("id") == active_id and p.get("status", PROJECT_STATUS_ACTIVE) == PROJECT_STATUS_ACTIVE:
            return p
    return None


def get_project_by_id(index_data, project_id):
    for p in index_data.get("projects", []):
        if p.get("id") == project_id:
            return p
    return None


def choose_next_active_project(index_data):
    for p in index_data.get("projects", []):
        if p.get("status", PROJECT_STATUS_ACTIVE) == PROJECT_STATUS_ACTIVE:
            index_data["active_project_id"] = p.get("id", "")
            return p
    index_data["active_project_id"] = ""
    return None


def safe_project_path(project_path):
    root = os.path.abspath(PROJECTS_ROOT)
    target = os.path.abspath(project_path or "")
    return target.startswith(root + os.sep) and target != root


def sync_registry_from_disk(index_data):
    changed = False
    projects = []
    for p in index_data.get("projects", []):
        path = p.get("path", "")
        if path and os.path.isdir(path):
            p.setdefault("status", PROJECT_STATUS_ACTIVE)
            p.setdefault("archived_at", "")
            projects.append(p)
        else:
            changed = True
    index_data["projects"] = projects
    if index_data.get("active_project_id") and not get_active_project(index_data):
        choose_next_active_project(index_data)
        changed = True
    if changed:
        save_projects_index(index_data)
    return index_data


# ---------------------------------------------------------------------------
# AI invocation
# ---------------------------------------------------------------------------

# CLI diagnostic lines that must never appear in generated document content.
# Matched against each line; a line is dropped if it starts with or contains
# any of these substrings.
_CLI_WARNING_PATTERNS = (
    "Warning: ",
    "Ripgrep is not available",
    "Falling back to GrepTool",
    "256-color support not detected",
)


def _strip_cli_warnings(text):
    lines = text.splitlines(keepends=True)
    cleaned = [l for l in lines if not any(p in l for p in _CLI_WARNING_PATTERNS)]
    return "".join(cleaned).lstrip("\n")


def invoke_ai(prompt, tool, model_id):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding=FILE_ENCODING) as t:
        tmp_path = t.name
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
        with open(tmp_path, "w") as out_f:
            result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, timeout=GENERATE_TIMEOUT_SECS)
        if result.returncode != 0:
            err = result.stderr.decode(FILE_ENCODING, errors="replace") if result.stderr else "AI call failed"
            return None, normalize_ai_error(err)
        with open(tmp_path, encoding=FILE_ENCODING) as f:
            raw = f.read()
        return _strip_cli_warnings(raw), None
    except subprocess.TimeoutExpired:
        return None, "The request timed out after 10 minutes. Try again."
    except FileNotFoundError:
        return None, f"AI tool '{tool}' not found in PATH"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def normalize_ai_error(raw_error):
    text = (raw_error or "").strip()
    lowered = text.lower()
    if any(marker in lowered for marker in QUOTA_ERROR_MARKERS):
        return "The AI request failed. Wait a few minutes, then retry."
    if not text:
        return "The AI model returned an error. Retry the request."
    return text.splitlines()[0][:ERROR_PREVIEW_LEN]


# ---------------------------------------------------------------------------
# Reviews + state
# ---------------------------------------------------------------------------

def load_reviews():
    with _reviews_lock:
        if os.path.exists(REVIEWS_FILE):
            try:
                with open(REVIEWS_FILE, "r") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("load_reviews: %s", exc)
        return {}


def save_reviews(reviews):
    with _reviews_lock:
        with open(REVIEWS_FILE, "w") as f:
            json.dump(reviews, f, indent=2)


def _default_state():
    return {
        "_schema_version": STATE_SCHEMA_VERSION,
        "project_name": "",
        "builds": [],
        "issues": [],
        "phases": [],
        "active_phase_id": None,
        "git": {
            "repo_url": "",
            "username": "",
            "email": "",
            "default_branch": DEFAULT_BRANCH,
            "branch_prefix": DEFAULT_BRANCH_PREFIX
        },
        "environments": {
            "staging": {"url": "", "branch": "staging", "status": "not_deployed", "deployed_at": ""},
            "production": {"url": "", "branch": DEFAULT_BRANCH, "status": "not_deployed", "deployed_at": ""}
        },
        "tool": DEFAULT_TOOL,
        "model": DEFAULT_TOOL
    }


def load_project_state():
    with _state_lock:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                defaults = _default_state()
                for k, v in defaults.items():
                    if k not in data:
                        data[k] = v
                    elif isinstance(v, dict) and isinstance(data[k], dict):
                        for sk, sv in v.items():
                            if sk not in data[k]:
                                data[k][sk] = sv
                file_version = data.get("_schema_version", 0)
                if file_version < STATE_SCHEMA_VERSION:
                    data = _migrate_project_state_schema(data, file_version)
                    data["_schema_version"] = STATE_SCHEMA_VERSION
                    try:
                        _to_save = json.loads(json.dumps(data))
                        _to_save.get("git", {}).pop("token", None)
                        with open(STATE_FILE, "w") as f:
                            json.dump(_to_save, f, indent=2)
                        os.chmod(STATE_FILE, 0o600)
                    except OSError as exc:
                        logger.warning("load_project_state migrate write: %s", exc)
                return data
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("load_project_state: %s", exc)
        return _default_state()


def save_project_state(state):
    # Strip git PAT before persisting — use env var GIT_PAT instead
    with _state_lock:
        to_save = json.loads(json.dumps(state))
        to_save.get("git", {}).pop("token", None)
        to_save["_schema_version"] = STATE_SCHEMA_VERSION
        with open(STATE_FILE, "w") as f:
            json.dump(to_save, f, indent=2)
        try:
            os.chmod(STATE_FILE, 0o600)
        except OSError as exc:
            logger.warning("save_project_state chmod: %s", exc)


# ---------------------------------------------------------------------------
# Phase management helpers
# ---------------------------------------------------------------------------

import re as _re

def _parse_phases_from_docs():
    # Scan delivery docs for phase/MVP headings and return an ordered list.
    scan_dirs = DELIVERY_SCAN_DIRS
    scan_files = DELIVERY_SCAN_FILES

    # Patterns that signal a phase heading (case-insensitive)
    phase_re = _re.compile(
        r'^#{1,3}\s*'
        r'(?P<name>'
        r'MVP(?:\s*[-–:]?\s*[^\n]*)?'
        r'|Phase\s+\d+(?:\s*[-–:]\s*[^\n]*)?'
        r'|(?:Phase|Release|Sprint|Milestone)\s+\w+(?:\s*[-–:]\s*[^\n]*)?'
        r')',
        _re.IGNORECASE | _re.MULTILINE
    )

    found = []      # list of (order_key, name, description, source)
    seen_names = set()

    for d in scan_dirs:
        dir_path = os.path.join(FORGE_DIR, d)
        if not os.path.isdir(dir_path):
            continue
        # Prefer the curated list, then fall back to any .md in the dir
        candidates = scan_files + [
            f for f in os.listdir(dir_path)
            if f.endswith(MARKDOWN_EXTENSION) and f not in scan_files
        ]
        for fname in candidates:
            fpath = os.path.join(dir_path, fname)
            if not os.path.isfile(fpath):
                continue
            try:
                text = open(fpath, encoding="utf-8").read()
            except OSError:
                continue
            lines = text.splitlines()
            for i, line in enumerate(lines):
                m = phase_re.match(line)
                if not m:
                    continue
                raw_name = m.group("name").strip().rstrip(":")
                # Normalise: "Phase 1 - Core Auth" → keep full label
                clean = _re.sub(r'\s+', ' ', raw_name)
                # Deduplicate by normalised lower name
                key = clean.lower()
                if key in seen_names:
                    continue
                seen_names.add(key)
                # Grab first non-empty line after heading as description
                desc_lines = []
                for j in range(i + 1, min(i + 6, len(lines))):
                    l = lines[j].strip()
                    if not l or l.startswith('#'):
                        break
                    if not l.startswith('|') and not l.startswith('-'):
                        desc_lines.append(l)
                        if len(desc_lines) >= 2:
                            break
                desc = ' '.join(desc_lines)[:DESCRIPTION_MAX_LEN]
                # Order: MVP=0, Phase N = N, else alphabetical
                if _re.match(r'mvp', key):
                    order_key = 0
                else:
                    nm = _re.search(r'\d+', key)
                    order_key = int(nm.group()) if nm else 99
                found.append({
                    "order": order_key,
                    "name": clean,
                    "description": desc,
                    "source": f"{d}/{fname}",
                })

    # Deduplicate by order_key — "Phase 1" and "Sprint 1" both extract
    # order=1 from the number, producing two entries at the same slot.
    # Keep only the highest-priority type per order slot.
    # Priority: Phase(0) > Release(1) > Milestone(2) > MVP(3) > Sprint(4) > other(9)
    _type_rank = {"phase": 0, "release": 1, "milestone": 2, "mvp": 3, "sprint": 4}

    def _heading_rank(name):
        low = name.lower()
        for t, r in _type_rank.items():
            if low.startswith(t):
                return r
        return 9

    order_best = {}
    for entry in found:
        ok = entry["order"]
        if ok not in order_best:
            order_best[ok] = entry
        elif _heading_rank(entry["name"]) < _heading_rank(order_best[ok]["name"]):
            order_best[ok] = entry

    found = sorted(order_best.values(), key=lambda x: x["order"])
    return found


def sync_phases(proj):
    # Merge phases parsed from delivery docs into project state.
    # Existing phases keep their status and issue_ids; new phases
    # are inserted as 'pending'. Removed phases are NOT deleted.
    doc_phases = _parse_phases_from_docs()
    existing = {p["id"]: p for p in proj.get("phases", [])}

    merged = []
    for dp in doc_phases:
        slug = _re.sub(r'[^a-z0-9]+', '-', dp["name"].lower()).strip('-')
        if slug in existing:
            p = existing[slug]
            p["name"]        = dp["name"]
            p["description"] = dp["description"] or p.get("description", "")
            p["order"]       = dp["order"]
            p["doc_source"]  = dp["source"]
        else:
            p = {
                "id":          slug,
                "name":        dp["name"],
                "description": dp["description"],
                "order":       dp["order"],
                "status":      PHASE_STATUS_PENDING,
                "doc_source":  dp["source"],
                "issue_ids":   [],
                "created_at":  datetime.now().isoformat(),
            }
            existing[slug] = p
        merged.append(p)

    # Preserve any manually-created phases not in docs
    doc_ids = {_re.sub(r'[^a-z0-9]+', '-', d["name"].lower()).strip('-') for d in doc_phases}
    for pid, p in existing.items():
        if pid not in doc_ids:
            p.pop("doc_source", None)
            merged.append(p)

    merged.sort(key=lambda x: (x.get("order", 99), x["name"]))
    proj["phases"] = merged
    return merged


# ---------------------------------------------------------------------------
# Phase 4+5 helpers
# ---------------------------------------------------------------------------

def _build_org_context_meta():
    _org = os.environ.get("FORGE_ORG", "")
    if not _org:
        return {"active": False, "org": "", "fileCount": 0}
    _cache = os.path.expanduser(f"~/.forge/org-cache/{_org}")
    _count = 0
    for _sub in ORG_SUBDIRS:
        _d = os.path.join(_cache, _sub)
        if os.path.isdir(_d):
            _count += sum(1 for _f in os.listdir(_d) if _f.endswith(MARKDOWN_EXTENSION))
    return {"active": _count > 0, "org": _org, "fileCount": _count}


def load_user():
    try:
        with open(USER_FILE, "r") as _f:
            return json.load(_f)
    except (OSError, json.JSONDecodeError):
        return {"role": "admin", "department": "all"}


def save_user(data):
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, "w") as _f:
        json.dump(data, _f, indent=2)


def _list_knowledge_entries():
    _org = os.environ.get("FORGE_ORG", "")
    if not _org:
        return []
    _cache = os.path.expanduser(f"~/.forge/org-cache/{_org}")
    _entries = []
    for _sub in ORG_SUBDIRS:
        _d = os.path.join(_cache, _sub)
        if os.path.isdir(_d):
            for _fname in sorted(os.listdir(_d)):
                if _fname.endswith(MARKDOWN_EXTENSION):
                    _fpath = os.path.join(_d, _fname)
                    _st = os.stat(_fpath)
                    _entries.append({
                        "name": _fname,
                        "type": _sub,
                        "absPath": _fpath,
                        "size": _st.st_size,
                        "modifiedAt": int(_st.st_mtime * 1000),
                    })
    return _entries


def _push_distill_to_kb(kb_repo_url, token, file_path, stage, ts):
    # Clone KB repo, commit distilled file on a new branch, push, open a PR.
    _parsed = urllib.parse.urlparse(kb_repo_url)
    _path_parts = _parsed.path.rstrip('/').lstrip('/').split('/')
    if len(_path_parts) < 2:
        return None, "Invalid KB repo URL"
    _owner = _path_parts[-2]
    _repo_name = _path_parts[-1]
    if _repo_name.endswith('.git'):
        _repo_name = _repo_name[:-4]
    _auth_url = f"https://x-access-token:{token}@github.com/{_owner}/{_repo_name}.git"
    _branch = f"forge/distill-{stage}-{ts}"
    _work_dir = tempfile.mkdtemp(prefix="forge-kb-")
    try:
        _r = subprocess.run(
            ["git", "clone", "--depth=1", _auth_url, _work_dir],
            capture_output=True, text=True
        )
        if _r.returncode != 0:
            return None, f"Clone failed: {_r.stderr.strip()[:200]}"
        _def_branch_r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=_work_dir, capture_output=True, text=True
        )
        _default_branch = _def_branch_r.stdout.strip() or "main"
        subprocess.run(["git", "checkout", "-b", _branch], cwd=_work_dir, capture_output=True)
        _dest_dir = os.path.join(_work_dir, "patterns")
        os.makedirs(_dest_dir, exist_ok=True)
        _fname = os.path.basename(file_path)
        shutil.copy2(file_path, os.path.join(_dest_dir, _fname))
        subprocess.run(["git", "config", "user.email", GIT_COMMIT_EMAIL], cwd=_work_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", GIT_COMMIT_NAME], cwd=_work_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=_work_dir, capture_output=True)
        _commit_r = subprocess.run(
            ["git", "commit", "-m", f"distill({stage}): add distilled patterns from {ts}"],
            cwd=_work_dir, capture_output=True, text=True
        )
        if _commit_r.returncode != 0:
            return None, f"Commit failed: {_commit_r.stderr.strip()[:200]}"
        _push_r = subprocess.run(
            ["git", "push", "origin", _branch],
            cwd=_work_dir, capture_output=True, text=True
        )
        if _push_r.returncode != 0:
            return None, f"Push failed: {_push_r.stderr.strip()[:200]}"
        _pr_body = json.dumps({
            "title": f"Distilled patterns: {stage} ({ts[:8]})",
            "head": _branch,
            "base": _default_branch,
            "body": (
                f"Auto-generated by Forge OS distillation.\n\n"
                f"**Stage:** `{stage}`  \n**File:** `patterns/{_fname}`  \n**Timestamp:** `{ts}`\n\n"
                f"Review the distilled patterns below and merge to publish them to the org knowledge base."
            ),
        }).encode("utf-8")
        _req = urllib.request.Request(
            f"https://api.github.com/repos/{_owner}/{_repo_name}/pulls",
            data=_pr_body,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": GITHUB_ACCEPT_HEADER,
                "Content-Type": GITHUB_CONTENT_TYPE,
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
                "User-Agent": GITHUB_USER_AGENT,
            }
        )
        with urllib.request.urlopen(_req, timeout=GIT_TIMEOUT_SECS) as _resp:
            _pr = json.loads(_resp.read().decode("utf-8"))
            return _pr.get("html_url", ""), None
    except urllib.error.HTTPError as _e:
        _body = _e.read().decode("utf-8", errors="ignore")[:300]
        return None, f"GitHub API error {_e.code}: {_body}"
    except Exception as _e:
        return None, str(_e)[:300]
    finally:
        shutil.rmtree(_work_dir, ignore_errors=True)


def _load_kb_state():
    path = os.path.join(FORGE_DIR, FILE_KB_STATE)
    if not os.path.exists(path):
        return {"exports": [], "distillations": []}
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"exports": [], "distillations": []}


def _save_kb_state(kb_state):
    path = os.path.join(FORGE_DIR, FILE_KB_STATE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(kb_state, f, indent=2)


def _kb_config_from_state(proj):
    """Return knowledge_base config dict, falling back to git.kb_repo_url for backcompat."""
    kb = proj.get("knowledge_base") or {}
    if kb.get("repo_owner") or kb.get("repo_name"):
        return kb
    kb_url = proj.get("git", {}).get("kb_repo_url", "")
    if kb_url:
        parsed = urllib.parse.urlparse(kb_url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            return {
                "repo_owner": parts[-2],
                "repo_name": parts[-1].replace(".git", ""),
                "branch": "main",
                "ref": "",
                "last_synced": "",
            }
    return kb


def _collect_reviewed_docs():
    """Return list of (rel_path, abs_path) for all reviewed markdown files across all stage dirs."""
    reviews = load_reviews()
    docs = []
    for stage_dir in ALL_STAGE_DIRS:
        stage_path = os.path.join(FORGE_DIR, stage_dir)
        if not os.path.isdir(stage_path):
            continue
        for fname in sorted(os.listdir(stage_path)):
            if not fname.endswith(MARKDOWN_EXTENSION):
                continue
            rel = f"{stage_dir}/{fname}"
            if reviews.get(rel) == REVIEW_REVIEWED:
                docs.append((rel, os.path.join(stage_path, fname)))
    return docs


def _run_export_to_kb(kb_config, proj, token, docs):
    """Clone KB repo, write project docs to projects/<slug>/, push branch, open PR. Returns (pr_url, error)."""
    owner = kb_config.get("repo_owner", "")
    repo = kb_config.get("repo_name", "")
    if not owner or not repo:
        return None, "KB repo not configured"
    slug = slugify_project_name(proj.get("project_name", "project"))
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch = f"{KB_BRANCH_EXPORT_PREFIX}/{slug}/{ts}"
    auth_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"
    work_dir = tempfile.mkdtemp(prefix="forge-kb-export-")
    try:
        r = subprocess.run(
            ["git", "clone", "--depth=1", auth_url, work_dir],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS * 4,
        )
        if r.returncode != 0:
            return None, f"Clone failed: {r.stderr.strip()[:200]}"
        def_br = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=work_dir, capture_output=True, text=True,
        )
        default_branch = def_br.stdout.strip() or "main"
        subprocess.run(["git", "checkout", "-b", branch], cwd=work_dir, capture_output=True)
        for rel, abs_path in docs:
            dest = os.path.join(work_dir, KB_PROJECTS_DIR, slug, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(abs_path, dest)
        meta = {
            "project": proj.get("project_name", slug),
            "slug": slug,
            "exported_at": datetime.now().isoformat(),
            "doc_count": len(docs),
        }
        meta_path = os.path.join(work_dir, KB_PROJECTS_DIR, slug, "_meta.json")
        with open(meta_path, "w", encoding=FILE_ENCODING) as mf:
            json.dump(meta, mf, indent=2)
        subprocess.run(["git", "config", "user.email", GIT_COMMIT_EMAIL], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", GIT_COMMIT_NAME], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=work_dir, capture_output=True)
        commit_r = subprocess.run(
            ["git", "commit", "-m", f"kb(export): {proj.get('project_name', slug)} docs ({len(docs)} files)"],
            cwd=work_dir, capture_output=True, text=True,
        )
        if commit_r.returncode != 0:
            return None, f"Commit failed: {commit_r.stderr.strip()[:200]}"
        push_r = subprocess.run(
            ["git", "push", "origin", branch],
            cwd=work_dir, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS * 2,
        )
        if push_r.returncode != 0:
            return None, f"Push failed: {push_r.stderr.strip()[:200]}"
        pr_payload = json.dumps({
            "title": f"kb(export): {proj.get('project_name', slug)} — {len(docs)} reviewed docs",
            "head": branch,
            "base": default_branch,
            "body": (
                f"Exported reviewed documents from **{proj.get('project_name', slug)}**.\n\n"
                f"- **Files:** {len(docs)}\n"
                f"- **Exported:** `{meta['exported_at']}`\n\n"
                f"Review project docs and merge to add them to the knowledge base.\n\n"
                f"**CODEOWNERS:** `@project-owner-team` approval required."
            ),
            "draft": False,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            data=pr_payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": GITHUB_ACCEPT_HEADER,
                "Content-Type": GITHUB_CONTENT_TYPE,
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
                "User-Agent": GITHUB_USER_AGENT,
            },
        )
        with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT_SECS) as resp:
            pr = json.loads(resp.read().decode("utf-8"))
            return pr.get("html_url", ""), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:300]
        return None, f"GitHub API error {e.code}: {body}"
    except Exception as e:
        return None, str(e)[:300]
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _parse_distill_sections(text):
    """Parse ## Patterns / ## Decisions / ## Learnings sections from AI distillation output."""
    buckets = {"patterns": [], "decisions": [], "learnings": []}
    current = None
    for line in text.splitlines():
        low = line.strip().lower()
        if low.startswith("## patterns"):
            current = "patterns"
        elif low.startswith("## decisions"):
            current = "decisions"
        elif low.startswith("## learnings"):
            current = "learnings"
        elif current:
            buckets[current].append(line)
    return (
        "\n".join(buckets["patterns"]).strip(),
        "\n".join(buckets["decisions"]).strip(),
        "\n".join(buckets["learnings"]).strip(),
    )


def _run_distill_to_kb(kb_config, proj, token, docs):
    """AI distillation: extract global learnings from reviewed docs and open a draft PR in the KB repo."""
    owner = kb_config.get("repo_owner", "")
    repo = kb_config.get("repo_name", "")
    if not owner or not repo:
        return None, "KB repo not configured"
    # Build doc content, cap each doc at 3 000 chars and total at 14 000
    doc_chunks = []
    total = 0
    for rel, abs_path in docs:
        try:
            with open(abs_path, "r", encoding=FILE_ENCODING) as f:
                content = f.read()
        except OSError:
            continue
        snippet = content[:3000]
        chunk = f"\n\n=== {rel} ===\n{snippet}"
        if total + len(chunk) > 14000:
            break
        doc_chunks.append(chunk)
        total += len(chunk)
    if not doc_chunks:
        return None, "No document content to distill"
    prompt = DISTILL_KNOWLEDGE_PROMPT.format(
        project_name=proj.get("project_name", "Project"),
        doc_content="".join(doc_chunks),
    )
    tool = proj.get("tool", DEFAULT_TOOL)
    model_id = proj.get("model", "")
    ai_result, ai_error = invoke_ai(prompt, tool, model_id)
    if ai_error:
        return None, f"AI distillation failed: {ai_error}"
    if not ai_result or not ai_result.strip():
        return None, "AI returned empty distillation"
    patterns, decisions, learnings = _parse_distill_sections(ai_result)
    if not any([patterns, decisions, learnings]):
        return None, "No patterns, decisions or learnings could be extracted"
    slug = slugify_project_name(proj.get("project_name", "project"))
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch = f"{KB_BRANCH_DISTILL_PREFIX}/{slug}/{ts}"
    auth_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"
    work_dir = tempfile.mkdtemp(prefix="forge-kb-distill-")
    try:
        r = subprocess.run(
            ["git", "clone", "--depth=1", auth_url, work_dir],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS * 4,
        )
        if r.returncode != 0:
            return None, f"Clone failed: {r.stderr.strip()[:200]}"
        def_br = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=work_dir, capture_output=True, text=True,
        )
        default_branch = def_br.stdout.strip() or "main"
        subprocess.run(["git", "checkout", "-b", branch], cwd=work_dir, capture_output=True)
        written = []
        date_tag = ts[:8]
        if patterns and "nothing to extract" not in patterns.lower():
            dest = os.path.join(work_dir, KB_GLOBAL_PATTERNS, f"{slug}-{date_tag}.md")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding=FILE_ENCODING) as f:
                f.write(f"# Patterns: {proj.get('project_name', slug)}\n\n> Distilled: {ts}\n\n{patterns}\n")
            written.append(("patterns", os.path.relpath(dest, work_dir)))
        if decisions and "nothing to extract" not in decisions.lower():
            dest = os.path.join(work_dir, KB_GLOBAL_DECISIONS, f"{slug}-{date_tag}.md")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding=FILE_ENCODING) as f:
                f.write(f"# Decisions: {proj.get('project_name', slug)}\n\n> Distilled: {ts}\n\n{decisions}\n")
            written.append(("decisions", os.path.relpath(dest, work_dir)))
        if learnings and "nothing to extract" not in learnings.lower():
            dest = os.path.join(work_dir, KB_GLOBAL_LEARNINGS, f"{slug}-{date_tag}.md")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding=FILE_ENCODING) as f:
                f.write(f"# Learnings: {proj.get('project_name', slug)}\n\n> Distilled: {ts}\n\n{learnings}\n")
            written.append(("learnings", os.path.relpath(dest, work_dir)))
        if not written:
            return None, "Nothing substantive extracted — all sections were empty"
        subprocess.run(["git", "config", "user.email", GIT_COMMIT_EMAIL], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", GIT_COMMIT_NAME], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=work_dir, capture_output=True)
        commit_r = subprocess.run(
            ["git", "commit", "-m", f"kb(distill): global learnings from {slug} ({date_tag})"],
            cwd=work_dir, capture_output=True, text=True,
        )
        if commit_r.returncode != 0:
            return None, f"Commit failed: {commit_r.stderr.strip()[:200]}"
        push_r = subprocess.run(
            ["git", "push", "origin", branch],
            cwd=work_dir, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS * 2,
        )
        if push_r.returncode != 0:
            return None, f"Push failed: {push_r.stderr.strip()[:200]}"
        pr_body_text = (
            f"AI-distilled global learnings from **{proj.get('project_name', slug)}**.\n\n"
            "**Files proposed:**\n"
            + "\n".join(f"- `{path}` ({kind})" for kind, path in written)
            + f"\n\n**Source docs distilled:** {len(doc_chunks)}\n\n"
            + "> This is a **draft PR**. Review the distilled content carefully before merging.\n"
            + "> **CODEOWNERS:** `@knowledge-curators` approval required for `global/` paths."
        )
        pr_payload = json.dumps({
            "title": f"kb(distill): global learnings from {proj.get('project_name', slug)}",
            "head": branch,
            "base": default_branch,
            "body": pr_body_text,
            "draft": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            data=pr_payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": GITHUB_ACCEPT_HEADER,
                "Content-Type": GITHUB_CONTENT_TYPE,
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
                "User-Agent": GITHUB_USER_AGENT,
            },
        )
        with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT_SECS) as resp:
            pr = json.loads(resp.read().decode("utf-8"))
            return {"pr_url": pr.get("html_url", ""), "files": written}, None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:300]
        return None, f"GitHub API error {e.code}: {body}"
    except Exception as e:
        return None, str(e)[:300]
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _load_distill_result():
    _path = os.path.join(FORGE_DIR, FILE_DISTILL_RESULT)
    if not os.path.exists(_path):
        return None
    try:
        with open(_path) as _f:
            return json.load(_f)
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# File tree + state helpers
# ---------------------------------------------------------------------------

def list_raw_inputs():
    # Walk 00-raw-input/ recursively and return all .md files with relative paths.
    if not os.path.exists(RAW_INPUT_DIR):
        return []
    files = []
    for dirpath, dirnames, filenames in os.walk(RAW_INPUT_DIR):
        dirnames.sort()
        for fname in sorted(filenames):
            if fname.endswith(".md"):
                fpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fpath, RAW_INPUT_DIR)
                st = os.stat(fpath)
                files.append({
                    "name": rel,
                    "size": st.st_size,
                    "modifiedAt": int(st.st_mtime)
                })
    return files


def get_combined_raw_input_path():
    # Combine all raw input files into a single temp file and return its path (or None).
    files = list_raw_inputs()
    if not files:
        return None
    parts = []
    for f in files:
        fpath = os.path.join(RAW_INPUT_DIR, f["name"])
        try:
            with open(fpath, "r", encoding="utf-8") as fp:
                content = fp.read().strip()
            if content:
                label = f["name"].replace("/", " / ").replace(".md", "")
                parts.append(f"# [{label}]\n\n{content}")
        except Exception:
            pass
    if not parts:
        return None
    combined = "\n\n---\n\n".join(parts)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8", prefix="forge_raw_")
    tmp.write(combined)
    tmp.close()
    return tmp.name


def build_file_entry(stage_dir, filename, reviews):
    file_path = os.path.join(stage_dir, filename)
    file_stats = os.stat(file_path)
    file_size = file_stats.st_size
    modified_at = int(file_stats.st_mtime)
    stage_name = os.path.basename(stage_dir)
    rel_path = f"{stage_name}/{filename}"
    if reviews is None:
        reviews = {}
    if file_size == 0:
        status = REVIEW_EMPTY
    elif reviews.get(rel_path) == REVIEW_REVIEWED:
        status = REVIEW_REVIEWED
    else:
        status = REVIEW_NEEDS_REVIEW
    return {
        "name": filename,
        "status": status,
        "size": file_size,
        "modifiedAt": modified_at,
    }


def parse_gate_status(content):
    in_status = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Status"):
            in_status = True
            continue
        if in_status and stripped:
            return GATE_STATUS_PASSED if stripped.upper() in (GATE_STATUS_PASSED, GATE_STATUS_APPROVED) else GATE_STATUS_PENDING
    return GATE_STATUS_PENDING


def evaluate_gate(gate_name):
    stage_dir_name = GATE_STAGE_MAP.get(gate_name)
    if not stage_dir_name:
        return GATE_STATUS_PENDING
    reviews = load_reviews()
    stage_path = os.path.join(FORGE_DIR, stage_dir_name)
    if not os.path.exists(stage_path):
        return GATE_STATUS_PENDING
    md_files = [f for f in os.listdir(stage_path) if f.endswith(MARKDOWN_EXTENSION) and os.path.getsize(os.path.join(stage_path, f)) > 0]
    if not md_files:
        return GATE_STATUS_PENDING
    for fname in md_files:
        if reviews.get(f"{stage_dir_name}/{fname}") != REVIEW_REVIEWED:
            return GATE_STATUS_PENDING
    return GATE_STATUS_PASSED


def save_build_progress(entry):
    progress_file = os.path.join(FORGE_DIR, FILE_BUILD_IN_PROGRESS)
    try:
        with open(progress_file, "w") as f:
            json.dump(entry, f)
    except OSError as exc:
        logger.debug("save_build_progress: %s", exc)


def clear_build_progress():
    progress_file = os.path.join(FORGE_DIR, FILE_BUILD_IN_PROGRESS)
    try:
        if os.path.exists(progress_file):
            os.remove(progress_file)
    except OSError as exc:
        logger.debug("clear_build_progress: %s", exc)


def set_processing(status, stage=""):
    status_file = os.path.join(FORGE_DIR, FILE_STATUS)
    runs_dir = os.path.join(FORGE_DIR, "runs")
    if os.path.exists(runs_dir):
        try:
            data = {"status": status, "stage": stage}
            # Always preserve last_error — prevents the next iteration's STATUS_RUNNING
            # write from clobbering an error written by the previous stage before break.
            if os.path.exists(status_file):
                try:
                    with open(status_file, "r") as sf:
                        existing = json.load(sf)
                    if "last_error" in existing:
                        data["last_error"] = existing["last_error"]
                except (OSError, json.JSONDecodeError) as exc:
                    logger.debug("set_processing read existing: %s", exc)
            with open(status_file, "w") as sf:
                json.dump(data, sf)
        except OSError as exc:
            logger.warning("set_processing write: %s", exc)


def compute_full_state():
    if not os.path.isdir(FORGE_DIR):
        return {
            "version": FORGE_VERSION,
            "phase": PHASE_INPUT,
            "gates": {},
            "tree": {},
            "processing": {"status": STATUS_IDLE},
            "stageReviewSummary": {},
            "allReviewed": False,
            "rawInputs": [],
            "builds": [],
            "issues": [],
            "environments": {},
            "git": {},
            "tool": DEFAULT_TOOL,
            "model": DEFAULT_TOOL,
            "project_name": "",
            "skip_org_context": False,
            "orgContext": _build_org_context_meta(),
            "user": load_user(),
            "project_type": "standard",
            "lastDistill": None,
        }
    proj = load_project_state()
    reviews = load_reviews()

    # Resolve project_name: state file → active project index entry → directory basename
    if not proj.get("project_name"):
        _idx = load_projects_index()
        _active = get_active_project(_idx)
        if _active and _active.get("name"):
            proj["project_name"] = _active["name"]
        else:
            proj["project_name"] = os.path.basename(REPO_ROOT)

    # Gates
    gates = {}
    gates_dir = os.path.join(FORGE_DIR, DIR_GATES)
    if os.path.exists(gates_dir):
        for g in os.listdir(gates_dir):
            if g.endswith(MARKDOWN_EXTENSION):
                gate_name = g.replace(MARKDOWN_EXTENSION, "")
                if gate_name in GATE_STAGE_MAP:
                    gates[gate_name] = evaluate_gate(gate_name)
                else:
                    with open(os.path.join(gates_dir, g), "r") as f:
                        content = f.read()
                    gates[gate_name] = parse_gate_status(content)

    # File tree
    VALID_STAGE_PREFIXES = {f"{i:02d}" for i in range(VALID_STAGE_PREFIX_COUNT)}
    files_tree = {}
    stage_review_summary = {}
    for d in sorted(os.listdir(FORGE_DIR)):
        d_path = os.path.join(FORGE_DIR, d)
        if os.path.isdir(d_path) and d[:2] in VALID_STAGE_PREFIXES and d != DIR_RAW_INPUT:
            files_tree[d] = []
            reviewed_count = 0
            generated_count = 0
            total_count = 0
            for fname in sorted(os.listdir(d_path)):
                if fname.endswith(MARKDOWN_EXTENSION):
                    entry = build_file_entry(d_path, fname, reviews)
                    files_tree[d].append(entry)
                    total_count += 1
                    if entry["status"] != REVIEW_EMPTY:
                        generated_count += 1
                    if entry["status"] == REVIEW_REVIEWED:
                        reviewed_count += 1
            stage_review_summary[d] = {
                "reviewed": reviewed_count,
                "generated": generated_count,
                "total": total_count,
            }

    # Processing status
    processing_status = {"status": STATUS_IDLE}
    status_file = os.path.join(FORGE_DIR, FILE_STATUS)
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as sf:
                processing_status = json.load(sf)
        except (OSError, json.JSONDecodeError) as exc:
            logger.debug("compute_full_state status.json: %s", exc)

    all_reviewed = all(
        s["reviewed"] == s["generated"] and s["generated"] > 0
        for s in stage_review_summary.values()
    ) if stage_review_summary else False

    all_gates_passed = all(v == GATE_STATUS_PASSED for v in gates.values()) if gates else False

    raw_inputs = list_raw_inputs()

    total_generated = sum(s["generated"] for s in stage_review_summary.values())
    total_docs = sum(s["total"] for s in stage_review_summary.values())

    builds = proj.get("builds", [])

    # Merge any in-progress build so the dashboard sees it immediately
    progress_file = os.path.join(FORGE_DIR, FILE_BUILD_IN_PROGRESS)
    if os.path.exists(progress_file):
        try:
            with open(progress_file) as _pf:
                in_progress = json.load(_pf)
            if not any(b.get("id") == in_progress.get("id") for b in builds):
                builds = builds + [in_progress]
        except (OSError, json.JSONDecodeError) as exc:
            logger.debug("in-progress build load: %s", exc)

    last_build = builds[-1] if builds else None

    if not raw_inputs:
        phase = PHASE_INPUT
    elif total_generated == 0:
        phase = PHASE_GENERATE
    elif total_generated < total_docs:
        phase = PHASE_GENERATE
    elif not all_reviewed:
        phase = PHASE_REVIEW
    elif not builds or (last_build and last_build.get("status") not in (BUILD_STATUS_PUSHED, BUILD_STATUS_COMMITTED)):
        phase = PHASE_BUILD
    elif last_build and last_build.get("status") in (BUILD_STATUS_PUSHED, BUILD_STATUS_COMMITTED):
        phase = PHASE_DEPLOY
    else:
        phase = PHASE_REVIEW

    return {
        "version": FORGE_VERSION,
        "phase": phase,
        "gates": gates,
        "tree": files_tree,
        "processing": processing_status,
        "stageReviewSummary": stage_review_summary,
        "allReviewed": all_reviewed,
        "rawInputs": raw_inputs,
        "builds": builds,
        "issues": proj.get("issues", []),
        "phases": proj.get("phases", []),
        "active_phase_id": proj.get("active_phase_id"),
        "environments": proj.get("environments", {}),
        "git": proj.get("git", {}),
        "tool": proj.get("tool", DEFAULT_TOOL),
        "model": proj.get("model", DEFAULT_TOOL),
        "project_name": proj.get("project_name", ""),
        "skip_org_context": proj.get("skip_org_context", False),
        "orgContext": _build_org_context_meta(),
        "user": load_user(),
        "project_type": proj.get("project_type", "standard"),
        "lastDistill": _load_distill_result(),
        "schema_version": proj.get("schema_version", 1),
    }


def initialize_active_project():
    index_data = sync_registry_from_disk(load_projects_index())
    active = get_active_project(index_data)
    if active and os.path.isdir(active.get("path", "")):
        set_project_root(active["path"], data_dir=active.get("data_dir", ""))
        return
    if os.path.isdir(FORGE_DIR):
        return
    projects = [
        p for p in index_data.get("projects", [])
        if p.get("status", PROJECT_STATUS_ACTIVE) == PROJECT_STATUS_ACTIVE
    ]
    if projects:
        index_data["active_project_id"] = projects[0].get("id", "")
        save_projects_index(index_data)
        set_project_root(projects[0].get("path", REPO_ROOT), data_dir=projects[0].get("data_dir", ""))


initialize_active_project()


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class ForgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence access logs

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", CORS_ALLOW_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", CORS_ALLOW_METHODS)
        self.send_header("Access-Control-Allow-Headers", CORS_ALLOW_HEADERS)

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._send_cors_headers()
        self.send_header("Content-Type", CONTENT_TYPE_JSON)
        self.end_headers()
        self.wfile.write(body)

    def _check_token(self):
        # Returns True if the request is authorised.
        # In dev mode (no FORGE_TOKEN configured) every request is allowed.
        if not FORGE_TOKEN:
            return True
        return self.headers.get("X-Forge-Token", "") == FORGE_TOKEN

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            dashboard_path = os.path.join(FORGE_DIR, "scripts/dashboard.html")
            if os.path.exists(dashboard_path):
                content = open(dashboard_path, "r", encoding="utf-8").read()
                # Inject runtime config (token) so dashboard JS can authenticate writes
                inject = (
                    f'<script>window.__FORGE_TOKEN__={json.dumps(FORGE_TOKEN)};</script>\n'
                )
                content = content.replace("</head>", inject + "</head>", 1)
                encoded = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", CONTENT_TYPE_HTML)
                self.send_header("Cache-Control", CACHE_CONTROL_NO_CACHE)
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                self.wfile.write(encoded)
            else:
                self.send_response(404)
                self.end_headers()
            return

        if path == "/api/projects":
            index_data = sync_registry_from_disk(load_projects_index())
            active = get_active_project(index_data)
            payload_projects = []
            for p in index_data.get("projects", []):
                payload_projects.append({
                    "id": p.get("id", ""),
                    "name": p.get("name", ""),
                    "slug": p.get("slug", ""),
                    "path": p.get("path", ""),
                    "created_at": p.get("created_at", ""),
                    "updated_at": p.get("updated_at", ""),
                    "last_opened_at": p.get("last_opened_at", ""),
                    "archived_at": p.get("archived_at", ""),
                    "status": p.get("status", PROJECT_STATUS_ACTIVE),
                })
            self._json_response(200, {
                "workspace_root": PROJECTS_ROOT,
                "active_project_id": index_data.get("active_project_id", ""),
                "active_project": active or None,
                "projects": payload_projects,
            })
            return

        if path == "/api/state":
            try:
                state = compute_full_state()
                self._json_response(200, state)
            except Exception as e:
                self._json_response(500, {"error": str(e)})
            return

        if path == "/api/file":
            file_path = params.get("path", [None])[0]
            if not file_path:
                self._json_response(400, {"error": "missing path"})
                return
            # H1: path traversal guard
            abs_path = os.path.normpath(os.path.join(FORGE_DIR, file_path))
            if not abs_path.startswith(FORGE_DIR + os.sep) and abs_path != FORGE_DIR:
                self._json_response(403, {"error": "forbidden"})
                return
            if os.path.exists(abs_path):
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", CONTENT_TYPE_PLAIN)
                self.end_headers()
                with open(abs_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._json_response(404, {"error": "not found"})
            return

        if path == "/api/raw-input":
            name = params.get("name", [None])[0]
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            fpath = os.path.normpath(os.path.join(RAW_INPUT_DIR, name))
            if not fpath.startswith(RAW_INPUT_DIR):
                self._json_response(400, {"error": "invalid path"})
                return
            if os.path.exists(fpath):
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", CONTENT_TYPE_PLAIN)
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._json_response(404, {"error": "not found"})
            return

        if path == "/api/user":
            self._json_response(200, load_user())
            return

        if path == "/api/knowledge":
            kparams = dict(urllib.parse.parse_qsl(parsed.query))
            abs_path = kparams.get("path")
            if abs_path:
                _org = os.environ.get("FORGE_ORG", "")
                _allowed = os.path.expanduser(f"~/.forge/org-cache/{_org}") if _org else ""
                if not _allowed or not abs_path.startswith(_allowed):
                    self._json_response(403, {"error": "forbidden"})
                    return
                if not os.path.isfile(abs_path):
                    self._json_response(404, {"error": "not found"})
                    return
                with open(abs_path, "r", encoding="utf-8") as _f:
                    content = _f.read()
                self._json_response(200, {"content": content})
            else:
                _proj = load_project_state()
                _kb_cfg = _kb_config_from_state(_proj)
                _kb_st = _load_kb_state()
                _reviewed_docs = _collect_reviewed_docs()
                self._json_response(200, {
                    "config": _kb_cfg,
                    "status": _kb_st,
                    "reviewed_doc_count": len(_reviewed_docs),
                    "reviewed_docs": [{"rel": r, "size": os.path.getsize(a)} for r, a in _reviewed_docs],
                    "entries": _list_knowledge_entries(),
                    "gh_cli": subprocess.run(["which", "gh"], capture_output=True).returncode == 0,
                })
            return

        if path == "/api/tools":
            result = {}
            for tool_id, info in KNOWN_TOOLS.items():
                found = shutil.which(tool_id)
                result[tool_id] = {
                    "installed": bool(found),
                    "path": found,
                    "label": info["label"],
                    "models": info["models"],
                }
            self._json_response(200, result)
            return

        if path == "/api/versions":
            file_path = params.get("path", [""])[0]
            if not file_path:
                self._json_response(400, {"error": "missing path"})
                return
            stem = file_path[:-3] if file_path.endswith(MARKDOWN_EXTENSION) else file_path
            ver_dir = os.path.normpath(os.path.join(FORGE_DIR, "versions", stem))
            _versions_base = os.path.join(FORGE_DIR, "versions") + os.sep
            if not ver_dir.startswith(_versions_base) and ver_dir != os.path.join(FORGE_DIR, "versions"):
                self._json_response(403, {"error": "forbidden"})
                return
            versions = []
            if os.path.isdir(ver_dir):
                for fname in sorted(os.listdir(ver_dir), reverse=True):
                    if fname.endswith(".md"):
                        fpath = os.path.join(ver_dir, fname)
                        ts_raw = fname[:-3]
                        try:
                            dt = datetime.strptime(ts_raw, VERSION_TIMESTAMP_FORMAT)
                            ts_iso = dt.isoformat()
                        except ValueError:
                            ts_iso = ts_raw
                        versions.append({"id": ts_raw, "timestamp": ts_iso, "size": os.path.getsize(fpath)})
            self._json_response(200, {"path": file_path, "versions": versions})
            return

        if path == "/api/version":
            file_path = params.get("path", [""])[0]
            ver_id    = params.get("id", [""])[0]
            if not file_path or not ver_id:
                self._json_response(400, {"error": "missing path or id"})
                return
            # C1: validate ver_id format
            if not re.fullmatch(r'\d{8}-\d{6}', ver_id):
                self._json_response(400, {"error": "invalid version id"})
                return
            stem = file_path[:-3] if file_path.endswith(".md") else file_path
            ver_path = os.path.normpath(os.path.join(FORGE_DIR, "versions", stem, f"{ver_id}.md"))
            _versions_base = os.path.join(FORGE_DIR, "versions") + os.sep
            if not ver_path.startswith(_versions_base):
                self._json_response(403, {"error": "forbidden"})
                return
            if not os.path.exists(ver_path):
                self._json_response(404, {"error": "version not found"})
                return
            with open(ver_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", CONTENT_TYPE_PLAIN)
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        if path == "/api/build-system":
            build_status_file = os.path.join(FORGE_DIR, FILE_BUILD_SYSTEM)
            build_status = {}
            if os.path.exists(build_status_file):
                try:
                    with open(build_status_file) as f:
                        build_status = json.load(f)
                except (OSError, json.JSONDecodeError) as exc:
                    logger.debug("build_status_file load: %s", exc)
            # Resolve active phase for filtering
            _bsproj = load_project_state()
            _active_pid = _bsproj.get("active_phase_id", "") or ""
            step_keys = ["backend", "frontend", "integration", "tests", "infra"]
            steps_out = {}
            for key in step_keys:
                st = build_status.get(key, {})
                # Show step as relevant only if it was built for the active phase
                # (or there is no active phase — legacy / phase-unscoped build)
                step_phase = st.get("phase_id") or ""
                if _active_pid and step_phase and step_phase != _active_pid:
                    # Built for a different phase — show idle for current phase
                    st = {}
                steps_out[key] = {
                    "status": st.get("status", STATUS_IDLE),
                    "files": st.get("files", []),
                    "generated_at": st.get("generated_at", ""),
                    "error": st.get("error"),
                    "phase_id": st.get("phase_id"),
                }
            self._json_response(200, {"steps": steps_out, "active_phase_id": _active_pid})
            return

        if path == "/api/build-file":
            step = params.get("step", [""])[0]
            rel  = params.get("path", [""])[0]
            # Optional explicit phase_id; if omitted use active phase
            bf_phase = params.get("phase_id", [""])[0].strip()
            if not step or not rel:
                self._json_response(400, {"error": "Missing step or path"})
                return
            if not bf_phase:
                _bfproj = load_project_state()
                bf_phase = _bfproj.get("active_phase_id", "") or ""
            # Resolve base dir: phase-scoped if phase known, else global
            if bf_phase:
                base = f"{DIR_BUILD}/{bf_phase}/{step}"
            else:
                base = BUILD_STEP_DIRS.get(step, DIR_BUILD + "/" + step)
            parts = [p for p in rel.replace("\\", "/").split("/") if p and p != ".."]
            full_path = os.path.join(FORGE_DIR, base, *parts)
            # Fallback to global path if phase-scoped file not found
            if not os.path.exists(full_path) and bf_phase:
                base_global = BUILD_STEP_DIRS.get(step, DIR_BUILD + "/" + step)
                full_path = os.path.join(FORGE_DIR, base_global, *parts)
            if not os.path.exists(full_path):
                self._json_response(404, {"error": "File not found"})
                return
            with open(full_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
            self._json_response(200, {"content": content, "path": rel})
            return

        if path == "/api/pr-status":
            import re as _re3
            pr_url = params.get("pr_url", [""])[0]
            m = _re3.search(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
            if not m:
                self._json_response(400, {"error": "Not a GitHub PR URL"})
                return
            gh_owner, gh_repo, pr_num = m.group(1), m.group(2), m.group(3)
            proj = load_project_state()
            token = proj.get("git", {}).get("token", "") or GIT_PAT
            auth_header = ["-H", f"Authorization: token {token}"] if token else []
            try:
                curl_r = subprocess.run([
                    "curl", "-s", *auth_header,
                    "-H", f"Accept: {GITHUB_ACCEPT_V3_HEADER}",
                    f"https://api.github.com/repos/{gh_owner}/{gh_repo}/pulls/{pr_num}"
                ], capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS)
                pr_data = json.loads(curl_r.stdout)
                state_val  = pr_data.get("state", "unknown")
                merged     = pr_data.get("merged", False)
                merged_at  = pr_data.get("merged_at") or ""
                merged_by  = (pr_data.get("merged_by") or {}).get("login", "")
                if merged:
                    updated = False
                    for b in proj.get("builds", []):
                        if b.get("pr_url", "").rstrip("/") == pr_url.rstrip("/") and b.get("status") != BUILD_STATUS_MERGED:
                            b["status"] = BUILD_STATUS_MERGED
                            b["merged_at"] = merged_at
                            b["merged_by"] = merged_by
                            branch_ref = b.get("branch", "")
                            if branch_ref and token and gh_owner and gh_repo:
                                del_r = subprocess.run([
                                    "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                                    "-X", "DELETE",
                                    "-H", f"Authorization: token {token}",
                                    "-H", "Accept: application/vnd.github.v3+json",
                                    f"https://api.github.com/repos/{gh_owner}/{gh_repo}/git/refs/heads/{branch_ref}",
                                ], capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS)
                                b["branch_deleted"] = del_r.stdout.strip() in ("204", "422")
                            # Auto-deploy phase when its PR merges
                            phase_id = b.get("phase_id", "")
                            if phase_id:
                                for p in proj.get("phases", []):
                                    if p["id"] == phase_id and p.get("status") == PHASE_STATUS_BUILT:
                                        p["status"] = PHASE_STATUS_DEPLOYED
                                        p["deployed_at"] = merged_at
                                        p["deployed_by"] = merged_by
                            updated = True
                    if updated:
                        save_project_state(proj)
                self._json_response(200, {
                    "state": state_val, "merged": merged,
                    "merged_at": merged_at, "merged_by": merged_by,
                })
            except Exception as e:
                self._json_response(500, {"error": str(e)})
            return

        if path == "/api/build-review":
            review_file = os.path.join(FORGE_DIR, FILE_BUILD_REVIEW)
            if os.path.exists(review_file):
                try:
                    with open(review_file) as f:
                        self._json_response(200, json.load(f))
                except (OSError, json.JSONDecodeError) as exc:
                    logger.debug("build-review load: %s", exc)
                    self._json_response(200, {"status": STATUS_IDLE})
            else:
                self._json_response(200, {"status": STATUS_IDLE})
            return

        if path == "/api/secrets":
            import re as _re2
            proj = load_project_state()
            git_cfg = proj.get("git", {})
            repo_url = git_cfg.get("repo_url", "")
            token = git_cfg.get("token", "") or GIT_PAT
            gh_owner, gh_repo = "", ""
            if repo_url:
                m = _re2.search(r"github\.com[/:]([^/]+)/([^/\.]+)", repo_url)
                if m:
                    gh_owner, gh_repo = m.group(1), m.group(2)

            secrets_list = []
            search_paths = [
                os.path.join(FORGE_DIR, "15-build", "infra", "secrets-required.md"),
                os.path.join(FORGE_DIR, "15-build", "infra", "infra", "secrets-required.md"),
                os.path.join(FORGE_DIR, "15-build", "secrets-required.md"),
            ]
            for sp in search_paths:
                if os.path.exists(sp) and os.path.getsize(sp) > 0:
                    with open(sp, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("|") and "`" in line:
                                parts = [p.strip() for p in line.split("|") if p.strip()]
                                if len(parts) >= 2:
                                    name_raw = parts[0].strip("`").strip()
                                    if name_raw and name_raw.lower() not in ("secret name", ":---", "---"):
                                        secrets_list.append({
                                            "name": name_raw,
                                            "description": parts[1] if len(parts) > 1 else "",
                                            "workflow": parts[2] if len(parts) > 2 else "",
                                            "environment": parts[3] if len(parts) > 3 else "",
                                        })
                    break

            configured = {s["name"]: s for s in proj.get("secrets_configured", [])}
            for s in secrets_list:
                cfg = configured.get(s["name"])
                s["configured"] = bool(cfg)
                s["protected"] = cfg.get("protected", True) if cfg else True
                s["set_at"] = cfg.get("set_at", "") if cfg else ""

            self._json_response(200, {
                "secrets": secrets_list,
                "repo": f"{gh_owner}/{gh_repo}" if gh_owner else "",
                "has_token": bool(token),
                "gh_cli": subprocess.run(["which", "gh"], capture_output=True).returncode == 0,
            })
            return

        self._json_response(404, {"error": "not found"})

    def do_DELETE(self):
        # C2: token guard on all write methods
        if not self._check_token():
            self._json_response(403, {"error": "forbidden"})
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = min(int(self.headers.get("Content-Length", 0) or 0), MAX_BODY_BYTES)
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8")) if post_data else {}
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.debug("do_DELETE: bad JSON body: %s", exc)
            data = {}

        if path == "/api/projects":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            if target.get("status", PROJECT_STATUS_ACTIVE) != PROJECT_STATUS_ARCHIVED:
                self._json_response(409, {"error": "archive project before deleting"})
                return
            project_path = target.get("path", "")
            if not safe_project_path(project_path):
                self._json_response(400, {"error": "invalid project path"})
                return
            if os.path.isdir(project_path):
                # Soft-delete: move to .trash instead of immediate rmtree
                trash_dir = os.path.join(PROJECTS_ROOT, ".trash")
                os.makedirs(trash_dir, exist_ok=True)
                trash_path = os.path.join(trash_dir, f"{project_id}-{int(time.time())}")
                shutil.move(project_path, trash_path)
            index_data["projects"] = [
                p for p in index_data.get("projects", [])
                if p.get("id") != project_id
            ]
            if index_data.get("active_project_id") == project_id:
                choose_next_active_project(index_data)
            save_projects_index(index_data)
            self._json_response(200, {"status": "deleted", "project_id": project_id})
            return

        if path == "/api/raw-input":
            name = data.get("name")
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            fpath = os.path.normpath(os.path.join(RAW_INPUT_DIR, name))
            if not fpath.startswith(RAW_INPUT_DIR):
                self._json_response(400, {"error": "invalid path"})
                return
            if os.path.exists(fpath):
                os.remove(fpath)
                parent = os.path.dirname(fpath)
                while parent != RAW_INPUT_DIR and os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                    parent = os.path.dirname(parent)
                self._json_response(200, {"status": "deleted"})
            else:
                self._json_response(404, {"error": "not found"})
            return

        self._json_response(404, {"error": "not found"})

    def do_POST(self):
        # C2: token guard on all write methods
        if not self._check_token():
            self._json_response(403, {"error": "forbidden"})
            return

        # H5: cap request body at 4 MB to prevent memory exhaustion
        content_length = min(int(self.headers.get("Content-Length", 0) or 0), MAX_BODY_BYTES)
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8")) if post_data else {}
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.debug("do_POST: bad JSON body: %s", exc)
            data = {}

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/projects":
            name = (data.get("name") or "").strip()
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            base_slug = slugify_project_name(name)
            slug = ensure_unique_slug(index_data, base_slug)
            project_id = f"proj-{int(time.time() * 1000)}"
            project_root = os.path.join(PROJECTS_ROOT, slug)
            os.makedirs(project_root, exist_ok=True)
            forge_script = FORGE_SCRIPT or os.path.abspath(os.path.join(ORCHESTRATOR_ROOT, "forge"))
            init_result = subprocess.run(
                [sys.executable, forge_script, "--project", project_root, "init"],
                cwd=ORCHESTRATOR_ROOT,
                capture_output=True,
                text=True,
            )
            if init_result.returncode != 0:
                self._json_response(500, {"error": "project init failed", "details": init_result.stderr or init_result.stdout})
                return
            # Read the data_dir that forge init wrote into the dotfile and store it in the
            # index entry. This gives set_project_root a reliable fallback if the dotfile
            # is ever missing (e.g. the slug dir was accidentally deleted and re-created).
            _project_data_dir = ""
            try:
                _dotfile = os.path.join(project_root, ".forge")
                _meta = json.loads(open(_dotfile, "r", encoding="utf-8").read())
                _project_data_dir = _meta.get("data_dir", "")
            except (OSError, json.JSONDecodeError, ValueError):
                pass
            now = datetime.now().isoformat()
            entry = {
                "id": project_id,
                "name": name,
                "slug": slug,
                "path": project_root,
                "data_dir": _project_data_dir,
                "created_at": now,
                "updated_at": now,
                "last_opened_at": now,
            }
            index_data.setdefault("projects", []).append(entry)
            index_data["active_project_id"] = project_id
            save_projects_index(index_data)
            set_project_root(project_root)
            try:
                state = load_project_state()
                if not state.get("project_name"):
                    state["project_name"] = name
                    save_project_state(state)
            except OSError as exc:
                logger.warning("project create state init: %s", exc)
            self._json_response(200, {"status": "created", "project": entry, "active_project_id": project_id})
            return

        if path == "/api/projects/select":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            if target.get("status", PROJECT_STATUS_ACTIVE) != PROJECT_STATUS_ACTIVE:
                self._json_response(409, {"error": "restore project before opening"})
                return
            target["last_opened_at"] = datetime.now().isoformat()
            target["updated_at"] = target["last_opened_at"]
            index_data["active_project_id"] = project_id
            save_projects_index(index_data)
            set_project_root(target["path"], data_dir=target.get("data_dir", ""))
            # Backfill project_name into state file if missing
            try:
                _pstate = load_project_state()
                if not _pstate.get("project_name") and target.get("name"):
                    _pstate["project_name"] = target["name"]
                    save_project_state(_pstate)
            except OSError as exc:
                logger.warning("select backfill project_name: %s", exc)
            self._json_response(200, {"status": "selected", "project": target})
            return

        if path == "/api/projects/archive":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            now = datetime.now().isoformat()
            target["status"] = PROJECT_STATUS_ARCHIVED
            target["archived_at"] = now
            target["updated_at"] = now
            if index_data.get("active_project_id") == project_id:
                choose_next_active_project(index_data)
            save_projects_index(index_data)
            self._json_response(200, {"status": "archived", "project": target})
            return

        if path == "/api/projects/restore":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            now = datetime.now().isoformat()
            target["status"] = PROJECT_STATUS_ACTIVE
            target["archived_at"] = ""
            target["updated_at"] = now
            if not get_active_project(index_data):
                index_data["active_project_id"] = project_id
            save_projects_index(index_data)
            self._json_response(200, {"status": "restored", "project": target})
            return

        if path == "/api/raw-input":
            name = data.get("name")
            content = data.get("content", "")
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            fpath = os.path.normpath(os.path.join(RAW_INPUT_DIR, name))
            if not fpath.startswith(RAW_INPUT_DIR):
                self._json_response(400, {"error": "invalid path"})
                return
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/generate":
            stage = data.get("stage", "all")
            forge_script = FORGE_SCRIPT or os.path.abspath(os.path.join(FORGE_DIR, "..", "..", "forge"))

            # Concurrent operation guard
            status_file_check = os.path.join(FORGE_DIR, FILE_STATUS)
            if os.path.exists(status_file_check):
                try:
                    with open(status_file_check) as _scf:
                        processing_status = json.load(_scf)
                    if processing_status.get("status") == STATUS_RUNNING:
                        self._json_response(409, {"error": "A generation is already in progress"})
                        return
                except (OSError, json.JSONDecodeError) as exc:
                    logger.debug("status_file_check: %s", exc)

            def _run_stage_proc(cmd, cwd, env):
                """Launch one forge-generate subprocess, register it for cancel, wait for it."""
                global _active_generate_proc
                kwargs = {"cwd": cwd, "env": env}
                if hasattr(os, "setsid"):
                    kwargs["start_new_session"] = True  # own process group → clean SIGKILL
                proc = subprocess.Popen(cmd, **kwargs)
                with _generate_lock:
                    _active_generate_proc = proc
                proc.wait()
                with _generate_lock:
                    if _active_generate_proc is proc:
                        _active_generate_proc = None
                return proc.returncode

            def run_generate():
                global _active_generate_proc
                set_processing(STATUS_RUNNING, stage)
                tmp_combined = None
                try:
                    tmp_combined = get_combined_raw_input_path()
                    proj = load_project_state()
                    base_env = {
                        **os.environ,
                        "FORGE_TOOL": proj.get("tool", DEFAULT_TOOL),
                        "FORGE_MODEL": proj.get("model", ""),
                    }
                    if stage == "all":
                        pipeline_stages = [
                            "context", "requirements", "design", "analysis", "architecture",
                            "delivery", "engineering", "qa", "operations", "release", "marketing"
                        ]
                        skip_env = {**base_env, "FORGE_SKIP_EXISTING": "1"}
                        for s in pipeline_stages:
                            set_processing(STATUS_RUNNING, s)
                            cmd = [sys.executable, forge_script, "generate", s]
                            if tmp_combined and s == "context":
                                cmd.append(tmp_combined)
                            rc = _run_stage_proc(cmd, REPO_ROOT, skip_env)
                            if rc != 0:
                                break
                    else:
                        cmd = [sys.executable, forge_script, "generate", stage]
                        if tmp_combined and stage == "context":
                            cmd.append(tmp_combined)
                        _run_stage_proc(cmd, REPO_ROOT, base_env)
                finally:
                    with _generate_lock:
                        _active_generate_proc = None
                    set_processing(STATUS_IDLE)
                    if tmp_combined and os.path.exists(tmp_combined):
                        try:
                            os.remove(tmp_combined)
                        except OSError as exc:
                            logger.debug("cleanup tmp_combined: %s", exc)

            t = threading.Thread(target=run_generate, daemon=True)
            t.start()
            self._json_response(200, {"status": "started", "stage": stage})
            return

        if path == "/api/generate/cancel":
            global _active_generate_proc
            with _generate_lock:
                proc = _active_generate_proc
            if proc is None:
                self._json_response(200, {"status": "not_running"})
                return
            try:
                if hasattr(os, "killpg"):
                    import signal as _signal
                    try:
                        os.killpg(os.getpgid(proc.pid), _signal.SIGTERM)
                    except (ProcessLookupError, PermissionError):
                        proc.terminate()
                else:
                    proc.terminate()
                logger.info("generate cancel: sent SIGTERM to pid %s", proc.pid)
            except Exception as exc:
                logger.warning("generate cancel: %s", exc)
            # Write cancelled status immediately so the UI updates without waiting
            # for the thread's finally block to run.
            status_file = os.path.join(FORGE_DIR, FILE_STATUS)
            runs_dir = os.path.join(FORGE_DIR, "runs")
            if os.path.exists(runs_dir):
                try:
                    with open(status_file, "w") as _sf:
                        json.dump({
                            "status": STATUS_IDLE,
                            "stage": "",
                            "last_error": {
                                "stage": "",
                                "file": "",
                                "message": "Generation stopped by user.",
                                "timestamp": datetime.now().isoformat(),
                            }
                        }, _sf)
                except OSError as exc:
                    logger.warning("generate cancel status write: %s", exc)
            self._json_response(200, {"status": "cancelled"})
            return

        if path == "/api/build-review":
            proj = load_project_state()
            tool = proj.get("tool", DEFAULT_TOOL)
            model_id = proj.get("model", "")
            review_file = os.path.join(FORGE_DIR, FILE_BUILD_REVIEW)

            def _load_review():
                if os.path.exists(review_file):
                    try:
                        with open(review_file) as f:
                            return json.load(f)
                    except (OSError, json.JSONDecodeError) as exc:
                        logger.warning("_load_review: %s", exc)
                return {}

            def _save_review(entry):
                with open(review_file, "w") as f:
                    json.dump(entry, f)

            action = data.get("action", "")

            if action == "cancel":
                entry = _load_review()
                pid = entry.get("pid")
                if pid:
                    try:
                        import signal as _sig
                        os.kill(pid, _sig.SIGTERM)
                    except (OSError, ProcessLookupError) as exc:
                        logger.debug("kill pid %s: %s", pid, exc)
                subprocess.run(["git", "reset", "HEAD"], cwd=REPO_ROOT, capture_output=True)
                entry["status"] = "cancelled"
                entry.pop("pid", None)
                _save_review(entry)
                self._json_response(200, {"status": "cancelled"})
                return

            if action == "clear":
                subprocess.run(["git", "reset", "HEAD"], cwd=REPO_ROOT, capture_output=True)
                if os.path.exists(review_file):
                    os.remove(review_file)
                self._json_response(200, {"status": "cleared"})
                return

            if action == "human_review":
                verdict = (data.get("verdict") or "").strip()
                notes   = (data.get("notes")   or "").strip()
                if verdict not in ("approve", "request_changes", "comment"):
                    self._json_response(400, {"error": "verdict must be approve, request_changes, or comment"})
                    return
                entry = _load_review()
                entry["human_review"] = {
                    "verdict": verdict,
                    "notes": notes,
                    "reviewed_at": datetime.now().isoformat(),
                }
                _save_review(entry)
                self._json_response(200, {"status": "ok", "verdict": verdict})
                return

            existing = _load_review()
            if existing.get("status") == "reviewing":
                self._json_response(200, {"status": "already_reviewing"})
                return

            def do_review():
                import shutil as _shutil, signal as _sig, tempfile as _tmp
                review_entry = {
                    "status": "reviewing",
                    "diff_stat": "",
                    "review": "",
                    "verdict": "",
                    "timestamp": datetime.now().isoformat(),
                }
                _save_review(review_entry)
                ai_proc = None
                tmp_path = None
                try:
                    code_step_map = {"backend":"backend","frontend":"frontend",
                                     "integration":"integration","tests":"tests","infra":"infra"}
                    copied_dirs = []
                    for step_key, dest_name in code_step_map.items():
                        src = os.path.join(FORGE_DIR, "15-build", step_key)
                        if os.path.isdir(src) and list(os.scandir(src)):
                            _shutil.copytree(src, os.path.join(REPO_ROOT, dest_name), dirs_exist_ok=True)
                            copied_dirs.append(dest_name)

                    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
                        subprocess.run(["git", "init"], cwd=REPO_ROOT, capture_output=True)

                    subprocess.run(["git", "add", ".forge/"], cwd=REPO_ROOT, capture_output=True)
                    subprocess.run(["git", "add", "README.md"], cwd=REPO_ROOT, capture_output=True)
                    for d in copied_dirs:
                        subprocess.run(["git", "add", d + "/"], cwd=REPO_ROOT, capture_output=True)

                    has_commits = subprocess.run(
                        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True
                    ).returncode == 0

                    stat_r = subprocess.run(["git", "diff", "--cached", "--stat"],
                                            cwd=REPO_ROOT, capture_output=True, text=True)
                    diff_stat = stat_r.stdout.strip()

                    numstat_r = subprocess.run(["git", "diff", "--cached", "--numstat"],
                                               cwd=REPO_ROOT, capture_output=True, text=True)
                    total_changed = 0
                    for line in numstat_r.stdout.splitlines():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            try:
                                total_changed += int(parts[0]) + int(parts[1])
                            except ValueError:
                                pass

                    if not diff_stat:
                        subprocess.run(["git", "reset", "HEAD"], cwd=REPO_ROOT, capture_output=True)
                        review_entry["status"] = "no_changes"
                        review_entry["review"] = (
                            "No changes detected since the last commit.\n\n"
                            "Rebuild one or more Build System steps first, or edit the raw input "
                            "and regenerate docs to produce new content worth pushing."
                        )
                        _save_review(review_entry)
                        return

                    review_entry["diff_stat"] = diff_stat
                    review_entry["total_changed_lines"] = total_changed
                    # Parse full diff into per-file structured data for the human reviewer
                    _full_diff_raw = subprocess.run(
                        ["git", "diff", "--cached"],
                        cwd=REPO_ROOT, capture_output=True, text=True,
                    ).stdout
                    review_entry["diff_files"] = _parse_diff_files(_full_diff_raw[:200000])
                    review_entry["human_review"] = {"verdict": None, "notes": "", "reviewed_at": None}
                    _save_review(review_entry)

                    is_large = total_changed > LARGE_CHANGESET_THRESHOLD or not has_commits

                    if is_large:
                        header_r = subprocess.run(
                            ["git", "diff", "--cached", "--unified=0", "--diff-filter=M"],
                            cwd=REPO_ROOT, capture_output=True, text=True
                        )
                        header_lines = [l for l in header_r.stdout.splitlines()
                                        if l.startswith(("---", "+++", "@@", "diff --git"))]
                        diff_for_ai = "\n".join(header_lines[:DIFF_HEADER_LINES])
                        scope_note = (
                            f"NOTE: This {'first push' if not has_commits else 'large changeset'} has "
                            f"{total_changed} changed lines across many files. "
                            "Review focuses on modified file structure and spec compliance — "
                            "not line-by-line hunks.\n\n"
                        )
                    else:
                        full_diff_r = subprocess.run(["git", "diff", "--cached"],
                                                     cwd=REPO_ROOT, capture_output=True, text=True)
                        diff_for_ai = full_diff_r.stdout[:DIFF_CHAR_LIMIT]
                        if len(full_diff_r.stdout) > DIFF_CHAR_LIMIT:
                            diff_for_ai += f"\n... (+{len(full_diff_r.stdout)-DIFF_CHAR_LIMIT} chars truncated)"
                        scope_note = ""

                    spec_snippets = []
                    for label, rel in [
                        ("Engineering spec", "06-engineering/backend-spec.md"),
                        ("Frontend spec",    "06-engineering/frontend-spec.md"),
                        ("Architecture",     "04-architecture/system-architecture.md"),
                    ]:
                        p = os.path.join(FORGE_DIR, rel)
                        if os.path.exists(p) and os.path.getsize(p) > 0:
                            with open(p, encoding="utf-8", errors="replace") as f:
                                spec_snippets.append(f"### {label}\n{f.read()[:1000]}")
                    spec_context = "\n\n".join(spec_snippets) or "(no spec docs)"

                    prompt = (
                        "You are a principal engineer doing a pre-merge code review.\n\n"
                        + scope_note +
                        "## Spec Context\n\n" + spec_context +
                        "\n\n## Diff\n\n```diff\n" + diff_for_ai + "\n```\n\n"
                        "## Review\n\n"
                        "Be concise. Only flag production-blocking issues:\n\n"
                        "### 1. Spec Compliance — missing or wrong implementations\n"
                        "### 2. Security — hardcoded secrets, missing auth, injection risks\n"
                        "### 3. Incomplete Code — TODOs, stubs, placeholder logic\n"
                        "### 4. Critical Bugs — type errors, missing error handling, logic bugs\n\n"
                        "End with exactly one line:\n"
                        "`VERDICT: APPROVE` | `VERDICT: APPROVE WITH NOTES` | `VERDICT: REQUEST CHANGES`"
                    )

                    with _tmp.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as t:
                        tmp_path = t.name

                    if tool == TOOL_GEMINI:
                        cmd = [TOOL_GEMINI, GEMINI_ARG_SKIP_TRUST] + ([GEMINI_ARG_MODEL, model_id] if model_id else []) + [GEMINI_ARG_PROMPT, prompt]
                    elif tool == TOOL_CLAUDE:
                        cmd = [TOOL_CLAUDE, CLAUDE_ARG_PROMPT, prompt, CLAUDE_ARG_OUTPUT_FORMAT, CLAUDE_OUTPUT_TEXT]
                    else:
                        cmd = [TOOL_GEMINI, GEMINI_ARG_SKIP_TRUST, GEMINI_ARG_PROMPT, prompt]

                    with open(tmp_path, "w") as out_f:
                        ai_proc = subprocess.Popen(cmd, stdout=out_f, stderr=subprocess.PIPE)

                    review_entry["pid"] = ai_proc.pid
                    _save_review(review_entry)

                    ai_proc.wait(timeout=AI_POLL_TIMEOUT_SECS)
                    ai_proc = None

                    current = _load_review()
                    if current.get("status") == "cancelled":
                        return

                    with open(tmp_path, encoding="utf-8") as f:
                        review_text = f.read().strip()

                    verdict = "unknown"
                    for line in review_text.splitlines():
                        if "VERDICT:" in line.upper():
                            u = line.upper()
                            if "REQUEST CHANGES" in u: verdict = "request_changes"
                            elif "APPROVE WITH NOTES" in u: verdict = "approve_with_notes"
                            elif "APPROVE" in u: verdict = "approve"
                            break

                    review_entry["review"] = review_text
                    review_entry["verdict"] = verdict
                    review_entry["status"] = "done"
                    review_entry["copied_dirs"] = copied_dirs
                    review_entry.pop("pid", None)

                except subprocess.TimeoutExpired:
                    if ai_proc:
                        ai_proc.kill()
                    review_entry["status"] = "error"
                    review_entry["review"] = "AI review timed out after 5 minutes."
                    review_entry["verdict"] = "error"
                    review_entry.pop("pid", None)
                except Exception as e:
                    current = _load_review()
                    if current.get("status") == "cancelled":
                        return
                    review_entry["status"] = "error"
                    review_entry["review"] = f"Review failed: {e}"
                    review_entry["verdict"] = "error"
                    review_entry.pop("pid", None)
                finally:
                    _save_review(review_entry)
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except OSError as exc:
                            logger.debug("do_review cleanup: %s", exc)

            t = threading.Thread(target=do_review, daemon=True)
            t.start()
            self._json_response(200, {"status": "started"})
            return

        if path == "/api/build":
            proj = load_project_state()
            git_cfg = proj.get("git", {})
            repo_url = git_cfg.get("repo_url", "")
            token = git_cfg.get("token", "") or GIT_PAT
            branch_prefix = git_cfg.get("branch_prefix", "forge")
            username = git_cfg.get("username", "")
            email = git_cfg.get("email", "")

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            # Phase-aware branch naming: forge/<phase-id>-<timestamp>
            _active_pid = proj.get("active_phase_id", "") or ""
            if _active_pid:
                branch_name = f"{branch_prefix}/{_active_pid}-{timestamp}"
            else:
                branch_name = f"{branch_prefix}/build-{timestamp}"
            build_entry = {
                "id": timestamp,
                "branch": branch_name,
                "status": "pending",
                "pr_url": "",
                "created_at": datetime.now().isoformat(),
                "phase_id": _active_pid or None,
                "log": []
            }

            def do_build():
                import shutil as _shutil
                import re as _re
                logs = []
                try:
                    def _redact(s):
                        if token:
                            s = s.replace(token, "***")
                            s = _re.sub(r'https://[^@]+@', 'https://***@', s)
                        return s

                    def run_git(args, cwd=REPO_ROOT):
                        result = subprocess.run(
                            ["git"] + args, cwd=cwd,
                            capture_output=True, text=True
                        )
                        safe_args = [a.replace(token, "***") if token and token in a else a for a in args]
                        logs.append(f"$ git {' '.join(safe_args)}: {result.returncode}")
                        if result.stdout.strip():
                            logs.append(_redact(result.stdout.strip()))
                        if result.stderr.strip():
                            logs.append(_redact(result.stderr.strip()))
                        return result

                    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
                        run_git(["init"])
                        if email:
                            run_git(["config", "user.email", email])
                        if username:
                            run_git(["config", "user.name", username])
                    else:
                        if email:
                            run_git(["config", "user.email", email])
                        if username:
                            run_git(["config", "user.name", username])

                    code_step_map = {
                        "backend": "backend",
                        "frontend": "frontend",
                        "integration": "integration",
                        "tests": "tests",
                        "infra": "infra",
                    }
                    copied_dirs = []
                    for step_key, dest_name in code_step_map.items():
                        src = os.path.join(FORGE_DIR, "15-build", step_key)
                        if os.path.isdir(src):
                            entries = list(os.scandir(src))
                            if entries:
                                dst = os.path.join(REPO_ROOT, dest_name)
                                _shutil.copytree(src, dst, dirs_exist_ok=True)
                                copied_dirs.append(dest_name)
                                logs.append(f"Copied .forge/15-build/{step_key}/ -> {dest_name}/")

                    project_name = proj.get("project_name", "") or os.path.basename(REPO_ROOT)
                    dir_descriptions = {
                        "backend": "FastAPI backend — models, services, REST API endpoints",
                        "frontend": "Frontend UI — components, pages, routing",
                        "integration": "Integration layer — third-party adapters, API clients",
                        "tests": "Test suite — unit, integration, and end-to-end tests",
                        "infra": "Infrastructure — Docker, CI/CD pipelines, deployment config",
                    }
                    dir_lines = "\n".join(
                        f"├── {d}/{'  ← ' + dir_descriptions[d] if d in dir_descriptions else ''}"
                        for d in copied_dirs
                    )
                    readme_lines = [
                        f"# {project_name}",
                        "",
                        f"> Generated by [Forge OS](https://github.com/mrinalxdev/forge-os) on {timestamp[:8][:4]}-{timestamp[:8][4:6]}-{timestamp[:8][6:]}",
                        "",
                        "## Repository Structure",
                        "",
                        "```",
                        f"{project_name}/",
                        f"├── .forge/          ← Spec docs, architecture decisions, agent definitions",
                    ]
                    if dir_lines:
                        readme_lines.append(dir_lines)
                    readme_lines += [
                        "```",
                        "",
                        "## Getting Started",
                        "",
                    ]
                    if "backend" in copied_dirs:
                        readme_lines += [
                            "### Backend",
                            "```bash",
                            "cd backend",
                            "cp .env.example .env   # fill in your secrets",
                            "docker compose up --build",
                            "```",
                            "",
                        ]
                    if "frontend" in copied_dirs:
                        readme_lines += [
                            "### Frontend",
                            "```bash",
                            "cd frontend",
                            "npm install",
                            "npm run dev",
                            "```",
                            "",
                        ]
                    if "tests" in copied_dirs:
                        readme_lines += [
                            "### Tests",
                            "```bash",
                            "cd tests",
                            "pip install -r requirements.txt",
                            "pytest",
                            "```",
                            "",
                        ]
                    readme_lines += [
                        "## Spec Docs",
                        "",
                        "All product and engineering decisions live in `.forge/`:",
                        "",
                        "| Directory | Contents |",
                        "|---|---|",
                        "| `.forge/01-requirements/` | BRD, PRD, success metrics |",
                        "| `.forge/04-architecture/` | System design, ADRs, data model |",
                        "| `.forge/06-engineering/` | Backend, frontend, integration specs |",
                        "| `.forge/07-quality/` | Test strategy, acceptance criteria |",
                        "| `.forge/08-operations/` | Runbooks, monitoring, incident response |",
                        "",
                        "_Do not edit `.forge/` manually — it is managed by Forge OS._",
                    ]
                    readme_path = os.path.join(REPO_ROOT, "README.md")
                    with open(readme_path, "w", encoding="utf-8") as rf:
                        rf.write("\n".join(readme_lines) + "\n")
                    logs.append("Generated README.md")

                    run_git(["add", ".forge/"])
                    run_git(["add", "README.md"])
                    for d in copied_dirs:
                        run_git(["add", d + "/"])

                    run_git(["checkout", "-b", branch_name])
                    build_entry["status"] = "branched"
                    save_build_progress(build_entry)

                    components_line = ", ".join(copied_dirs) if copied_dirs else "docs only"
                    commit_msg = (
                        f"forge: generated code [{timestamp}]\n\n"
                        f"Components: {components_line}\n"
                        f"Spec docs: .forge/01-requirements, .forge/04-architecture, .forge/06-engineering"
                    )
                    run_git(["commit", "-m", commit_msg])
                    build_entry["status"] = "committed"
                    save_build_progress(build_entry)

                    pr_body_lines = [
                        "## Generated by Forge OS",
                        "",
                        f"**Branch:** `{branch_name}`",
                        f"**Timestamp:** {timestamp}",
                        "",
                        "### Generated Components",
                    ]
                    if copied_dirs:
                        for d in copied_dirs:
                            pr_body_lines.append(f"- `{d}/` — sourced from `.forge/15-build/{d}/`")
                    else:
                        pr_body_lines.append("- Spec documents only (no code generated yet)")
                    pr_body_lines += [
                        "",
                        "### Spec Documents Included",
                        "- **Requirements:** `.forge/01-requirements/`",
                        "- **Architecture:** `.forge/04-architecture/`",
                        "- **Engineering specs:** `.forge/06-engineering/`",
                        "- **Quality plan:** `.forge/07-quality/`",
                        "",
                        "### Review Checklist",
                        "- [ ] Code matches engineering spec in `.forge/06-engineering/`",
                        "- [ ] Architecture decisions from `.forge/04-architecture/` are implemented",
                        "- [ ] Tests in `tests/` cover all critical paths",
                        "- [ ] Environment variables and secrets are NOT hardcoded",
                        "- [ ] Docker/infra configs reviewed before merge",
                        "- [ ] No generated placeholder comments (`# TODO`, `# IMPLEMENT`) remain",
                        "",
                        "_Generated by [Forge OS](https://github.com/mrinalxdev/forge-os)_",
                    ]
                    pr_body = "\n".join(pr_body_lines)

                    if repo_url:
                        default_branch = git_cfg.get("default_branch", "main")
                        push_url = repo_url
                        if token and "github.com" in repo_url:
                            push_url = repo_url.replace("https://", f"https://{username}:{token}@")

                        ls = run_git(["ls-remote", "--heads", push_url])
                        remote_is_empty = ls.returncode == 0 and default_branch not in ls.stdout

                        if remote_is_empty:
                            logs.append(f"Remote is empty — bootstrapping {default_branch} branch")
                            run_git(["branch", "-M", default_branch])
                            boot = run_git(["push", "-u", push_url, default_branch])
                            if boot.returncode != 0:
                                build_entry["status"] = "error"
                                raise RuntimeError(f"Failed to bootstrap {default_branch}")
                            run_git(["checkout", "-b", branch_name])

                        build_entry["status"] = "pushing"
                        save_build_progress(build_entry)
                        result = run_git(["push", "-u", push_url, branch_name])
                        if result.returncode == 0:
                            build_entry["status"] = "pushed"
                            save_build_progress(build_entry)
                            if "github.com" in repo_url and token:
                                clean_url = repo_url.rstrip("/").replace(".git", "")
                                gh_path = clean_url.replace("https://github.com/", "")
                                gh_parts = gh_path.split("/")
                                if len(gh_parts) >= 2:
                                    gh_owner, gh_repo = gh_parts[0], gh_parts[1]
                                    pr_title = f"[Forge] Generated code — {timestamp}"
                                    if copied_dirs:
                                        pr_title = f"[Forge] {', '.join(d.capitalize() for d in copied_dirs)} — {timestamp}"
                                    api_payload = json.dumps({
                                        "title": pr_title,
                                        "body": pr_body,
                                        "head": branch_name,
                                        "base": default_branch,
                                    }).encode()
                                    try:
                                        curl_res = subprocess.run([
                                            "curl", "-s", "-X", "POST",
                                            "-H", f"Authorization: token {token}",
                                            "-H", "Accept: application/vnd.github.v3+json",
                                            "-H", "Content-Type: application/json",
                                            "-H", "User-Agent: ForgeOS/0.2.0",
                                            "-d", api_payload.decode(),
                                            f"https://api.github.com/repos/{gh_owner}/{gh_repo}/pulls",
                                        ], capture_output=True, text=True, timeout=NETWORK_TIMEOUT_SECS)
                                        pr_json = json.loads(curl_res.stdout)
                                        pr_url = pr_json.get("html_url", "")
                                        if pr_url:
                                            build_entry["pr_url"] = pr_url
                                            build_entry["status"] = "pr_created"
                                            logs.append(f"PR created: {pr_url}")
                                            save_build_progress(build_entry)
                                            subprocess.run([
                                                "curl", "-s", "-X", "PATCH",
                                                "-H", f"Authorization: token {token}",
                                                "-H", "Accept: application/vnd.github.v3+json",
                                                "-H", "Content-Type: application/json",
                                                "-H", "User-Agent: ForgeOS/0.2.0",
                                                "-d", '{"delete_branch_on_merge":true}',
                                                f"https://api.github.com/repos/{gh_owner}/{gh_repo}",
                                            ], capture_output=True, text=True, timeout=HTTP_CHECK_TIMEOUT_SECS)
                                            logs.append("Repo configured: delete branch on merge")
                                        else:
                                            err_msg = pr_json.get("message", curl_res.stdout[:200])
                                            raise RuntimeError(err_msg)
                                    except Exception as api_err:
                                        logs.append(f"GitHub API error: {api_err}")
                                        push_out = result.stderr + result.stdout
                                        m = _re.search(r'https://github\.com/\S+/pull/new/\S+', push_out)
                                        if m:
                                            pr_url = m.group(0).strip()
                                        else:
                                            pr_url = f"{clean_url}/compare/{default_branch}...{branch_name}?expand=1"
                                        build_entry["pr_url"] = pr_url
                                        build_entry["status"] = "pushed"
                            elif "github.com" in repo_url:
                                clean_url = repo_url.rstrip("/").replace(".git", "")
                                pr_url = f"{clean_url}/compare/{default_branch}...{branch_name}?expand=1"
                                build_entry["pr_url"] = pr_url
                        else:
                            build_entry["status"] = "error"
                    else:
                        build_entry["status"] = "committed"
                except Exception as e:
                    logs.append(f"Error: {e}")
                    build_entry["status"] = "error"
                finally:
                    build_entry["log"] = logs
                    proj2 = load_project_state()
                    proj2.setdefault("builds", []).append(build_entry)
                    save_project_state(proj2)
                    clear_build_progress()

            t = threading.Thread(target=do_build, daemon=True)
            t.start()
            self._json_response(200, {"status": "started", "branch": branch_name})
            return

        # ── Phase management ─────────────────────────────────────────────────
        if path == "/api/phases":
            proj = load_project_state()
            action = data.get("action", "")

            if action == "sync":
                # Re-parse delivery docs and merge into phase list
                phases = sync_phases(proj)
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": phases})
                return

            if action == "create":
                # Manual phase creation
                name = data.get("name", "").strip()
                if not name:
                    self._json_response(400, {"error": "name required"}); return
                slug = _re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
                phases = proj.setdefault("phases", [])
                if any(p["id"] == slug for p in phases):
                    self._json_response(409, {"error": "Phase already exists"}); return
                new_phase = {
                    "id": slug, "name": name,
                    "description": data.get("description", ""),
                    "order": len(phases),
                    "status": "pending",
                    "issue_ids": [],
                    "created_at": datetime.now().isoformat(),
                }
                phases.append(new_phase)
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": phases})
                return

            if action == "activate":
                phase_id = data.get("id")
                phases = proj.get("phases", [])
                phase = next((p for p in phases if p["id"] == phase_id), None)
                if not phase:
                    self._json_response(404, {"error": "Phase not found"}); return
                # Check ordering: previous phase must be built
                idx = phases.index(phase)
                if idx > 0:
                    prev = phases[idx - 1]
                    if prev["status"] not in ("built", "deployed"):
                        self._json_response(400, {
                            "error": f"Complete '{prev['name']}' before activating this phase."
                        }); return
                phase["status"] = "active"
                proj["active_phase_id"] = phase_id
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": phases})
                return

            if action == "complete":
                phase_id = data.get("id")
                phases = proj.get("phases", [])
                phase = next((p for p in phases if p["id"] == phase_id), None)
                if not phase:
                    self._json_response(404, {"error": "Phase not found"}); return
                # Validate: all build steps must be complete for this phase
                build_status_file = os.path.join(FORGE_DIR, FILE_BUILD_SYSTEM)
                build_status = {}
                if os.path.exists(build_status_file):
                    try:
                        with open(build_status_file) as f:
                            build_status = json.load(f)
                    except (OSError, json.JSONDecodeError):
                        pass
                step_keys = ["backend", "frontend", "integration", "tests", "infra"]
                incomplete = [
                    s for s in step_keys
                    if build_status.get(s, {}).get("status") != "complete"
                    or (build_status.get(s, {}).get("phase_id") or "") != phase_id
                ]
                if incomplete and not data.get("force"):
                    self._json_response(400, {
                        "error": f"Build steps not complete for this phase: {', '.join(incomplete)}. "
                                 "Run all build steps first, or pass force=true to override.",
                        "incomplete_steps": incomplete,
                    }); return
                phase["status"] = PHASE_STATUS_BUILT
                phase["completed_at"] = datetime.now().isoformat()
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": phases})
                return

            if action == "deploy":
                phase_id = data.get("id")
                phases = proj.get("phases", [])
                phase = next((p for p in phases if p["id"] == phase_id), None)
                if not phase:
                    self._json_response(404, {"error": "Phase not found"}); return
                if phase.get("status") not in (PHASE_STATUS_BUILT, PHASE_STATUS_DEPLOYED):
                    self._json_response(400, {"error": "Phase must be built before it can be deployed"}); return
                phase["status"] = PHASE_STATUS_DEPLOYED
                phase["deployed_at"] = datetime.now().isoformat()
                phase["deployed_by"] = data.get("deployed_by", "")
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": phases})
                return

            if action == "delete":
                phase_id = data.get("id")
                phases = proj.get("phases", [])
                proj["phases"] = [p for p in phases if p["id"] != phase_id]
                if proj.get("active_phase_id") == phase_id:
                    proj["active_phase_id"] = None
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": proj["phases"]})
                return

            # Default: tag issue to phase
            if action == "tag_issue":
                phase_id = data.get("phase_id")
                issue_id = data.get("issue_id")
                phases = proj.setdefault("phases", [])
                # Remove from all phases first
                for p in phases:
                    p.setdefault("issue_ids", [])
                    if issue_id in p["issue_ids"]:
                        p["issue_ids"].remove(issue_id)
                # Tag to new phase (None = unassigned)
                if phase_id:
                    phase = next((p for p in phases if p["id"] == phase_id), None)
                    if phase:
                        phase["issue_ids"].append(issue_id)
                save_project_state(proj)
                self._json_response(200, {"status": "ok", "phases": phases})
                return

            self._json_response(400, {"error": "Unknown action"})
            return

        if path == "/api/issue":
            proj = load_project_state()
            issues = proj.setdefault("issues", [])
            issue_id = data.get("id")
            if issue_id:
                for issue in issues:
                    if issue["id"] == issue_id:
                        for k in ("type", "title", "description", "priority", "status", "phase_id"):
                            if k in data:
                                issue[k] = data[k]
                        issue["updated_at"] = datetime.now().isoformat()
                        break
            else:
                new_id = f"{ISSUE_ID_PREFIX}{len(issues) + 1:03d}"
                new_issue = {
                    "id": new_id,
                    "type": data.get("type", ISSUE_DEFAULT_TYPE),
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "priority": data.get("priority", ISSUE_DEFAULT_PRIORITY),
                    "status": ISSUE_STATUS_OPEN,
                    "phase_id": data.get("phase_id", None),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
                issues.append(new_issue)
            save_project_state(proj)
            self._json_response(200, {"status": "ok", "issues": proj["issues"]})
            return

        if path == "/api/user":
            user = load_user()
            if "role" in data:
                user["role"] = data["role"]
            if "department" in data:
                user["department"] = data["department"]
            save_user(user)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/distill":
            stage = data.get("stage")
            _org = os.environ.get("FORGE_ORG", "")
            if not stage:
                self._json_response(400, {"error": "missing stage"})
                return
            if not _org:
                self._json_response(400, {"error": "FORGE_ORG not set — connect GitHub org first"})
                return
            _stage_dirs = STAGE_DIR_MAP
            _sdir = _stage_dirs.get(stage)
            if not _sdir:
                self._json_response(400, {"error": "invalid stage"})
                return
            _stage_path = os.path.join(FORGE_DIR, _sdir)
            if not os.path.isdir(_stage_path):
                self._json_response(404, {"error": "stage directory not found"})
                return
            _reviews = load_reviews()
            _reviewed = [
                os.path.join(FORGE_DIR, _sdir, _fn)
                for _fn in sorted(os.listdir(_stage_path))
                if _fn.endswith(MARKDOWN_EXTENSION) and _reviews.get(os.path.join(_sdir, _fn)) == REVIEW_REVIEWED
            ]
            if not _reviewed:
                self._json_response(400, {"error": "no reviewed files in this stage"})
                return
            _proj = load_project_state()

            def _run_distill():
                _status_file = os.path.join(FORGE_DIR, FILE_STATUS)
                _result_file = os.path.join(FORGE_DIR, FILE_DISTILL_RESULT)
                _ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                _out_path = None
                try:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(_status_file, "w") as _sf:
                            json.dump({"status": STATUS_DISTILLING, "stage": stage, "updated_at": datetime.now().isoformat()}, _sf)
                    _out_dir = os.path.expanduser(f"~/.forge/org-cache/{_org}/patterns")
                    os.makedirs(_out_dir, exist_ok=True)
                    _out_path = os.path.join(_out_dir, f"{stage}-{_ts}.md")
                    _base_env = {
                        **os.environ,
                        "FORGE_TOOL": _proj.get("tool", DEFAULT_TOOL),
                        "FORGE_MODEL": _proj.get("model", ""),
                    }
                    _cmd = [
                        sys.executable,
                        os.path.join(FORGE_DIR, "scripts/run.py"),
                        "distill",
                        "--distill-stage", stage,
                        "--distill-output", _out_path,
                        "--distill-sources", ",".join(_reviewed),
                    ]
                    _sub = subprocess.run(_cmd, cwd=REPO_ROOT, env=_base_env)

                    _kb_url = _proj.get("git", {}).get("kb_repo_url", "")
                    _token = _proj.get("git", {}).get("token", "") or GIT_PAT
                    _pr_url = None
                    _pr_error = None
                    if _sub.returncode == 0 and _kb_url and _token and _out_path and os.path.exists(_out_path):
                        _pr_url, _pr_error = _push_distill_to_kb(_kb_url, _token, _out_path, stage, _ts)

                    _result = {
                        "stage": stage,
                        "file": _out_path,
                        "timestamp": _ts,
                        "prUrl": _pr_url,
                        "prError": _pr_error,
                        "success": _sub.returncode == 0,
                    }
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(_result_file, "w") as _rf:
                            json.dump(_result, _rf, indent=2)
                finally:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(_status_file, "w") as _sf:
                            json.dump({"status": STATUS_IDLE, "stage": stage, "updated_at": datetime.now().isoformat()}, _sf)

            _t = threading.Thread(target=_run_distill, daemon=True)
            _t.start()
            self._json_response(200, {"status": "started", "stage": stage})
            return

        if path == "/api/knowledge/configure":
            repo_owner = (data.get("repo_owner") or "").strip()
            repo_name = (data.get("repo_name") or "").strip()
            branch = (data.get("branch") or "main").strip()
            if not repo_owner or not repo_name:
                self._json_response(400, {"error": "repo_owner and repo_name are required"})
                return
            proj = load_project_state()
            proj["knowledge_base"] = {
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "branch": branch,
                "ref": proj.get("knowledge_base", {}).get("ref", ""),
                "last_synced": proj.get("knowledge_base", {}).get("last_synced", ""),
            }
            # Keep backcompat field
            proj.setdefault("git", {})["kb_repo_url"] = f"https://github.com/{repo_owner}/{repo_name}"
            save_project_state(proj)
            self._json_response(200, {"status": "saved", "config": proj["knowledge_base"]})
            return

        if path == "/api/knowledge/export":
            proj = load_project_state()
            kb_cfg = _kb_config_from_state(proj)
            if not kb_cfg.get("repo_owner") or not kb_cfg.get("repo_name"):
                self._json_response(400, {"error": "Configure knowledge base repo first"})
                return
            token = proj.get("git", {}).get("token", "") or GIT_PAT
            if not token:
                self._json_response(400, {"error": "GitHub token required — configure it in Settings"})
                return
            docs = _collect_reviewed_docs()
            if not docs:
                self._json_response(400, {"error": "No reviewed documents to export"})
                return

            def _do_export():
                _kb_st2 = _load_kb_state()
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                entry = {"id": ts, "slug": slugify_project_name(proj.get("project_name", "project")),
                         "doc_count": len(docs), "status": KB_STATUS_EXPORTING,
                         "created_at": datetime.now().isoformat(), "pr_url": None, "error": None}
                _kb_st2.setdefault("exports", []).insert(0, entry)
                _save_kb_state(_kb_st2)
                pr_url, error = _run_export_to_kb(kb_cfg, proj, token, docs)
                entry["pr_url"] = pr_url
                entry["error"] = error
                entry["status"] = KB_STATUS_ERROR if error else KB_STATUS_DONE
                _save_kb_state(_kb_st2)

            threading.Thread(target=_do_export, daemon=True).start()
            self._json_response(200, {"status": "started", "doc_count": len(docs)})
            return

        if path == "/api/knowledge/distill":
            proj = load_project_state()
            kb_cfg = _kb_config_from_state(proj)
            if not kb_cfg.get("repo_owner") or not kb_cfg.get("repo_name"):
                self._json_response(400, {"error": "Configure knowledge base repo first"})
                return
            token = proj.get("git", {}).get("token", "") or GIT_PAT
            if not token:
                self._json_response(400, {"error": "GitHub token required — configure it in Settings"})
                return
            docs = _collect_reviewed_docs()
            if not docs:
                self._json_response(400, {"error": "No reviewed documents to distill"})
                return

            def _do_distill():
                _kb_st2 = _load_kb_state()
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                entry = {"id": ts, "slug": slugify_project_name(proj.get("project_name", "project")),
                         "doc_count": len(docs), "status": KB_STATUS_DISTILLING,
                         "created_at": datetime.now().isoformat(), "pr_url": None, "files": [], "error": None}
                _kb_st2.setdefault("distillations", []).insert(0, entry)
                _save_kb_state(_kb_st2)
                result, error = _run_distill_to_kb(kb_cfg, proj, token, docs)
                if error:
                    entry["error"] = error
                    entry["status"] = KB_STATUS_ERROR
                else:
                    entry["pr_url"] = result.get("pr_url")
                    entry["files"] = result.get("files", [])
                    entry["status"] = KB_STATUS_DONE
                _save_kb_state(_kb_st2)

            threading.Thread(target=_do_distill, daemon=True).start()
            self._json_response(200, {"status": "started", "doc_count": len(docs)})
            return

        if path == "/api/knowledge/sync":
            ref = (data.get("ref") or "").strip()
            if not ref:
                self._json_response(400, {"error": "ref is required"})
                return
            proj = load_project_state()
            proj.setdefault("knowledge_base", {})["ref"] = ref
            proj["knowledge_base"]["last_synced"] = datetime.now().isoformat()
            save_project_state(proj)
            self._json_response(200, {"status": "synced", "ref": ref})
            return

        if path == "/api/settings":
            proj = load_project_state()
            new_pat = None
            if "git" in data:
                new_pat = data["git"].pop("token", None)  # extract before merge
                proj["git"].update(data["git"])
            if "environments" in data:
                for env_key in ("staging", "production"):
                    if env_key in data["environments"]:
                        proj["environments"].setdefault(env_key, {}).update(data["environments"][env_key])
            if "tool" in data:
                # C2: validate tool against known set
                if data["tool"] not in KNOWN_TOOLS:
                    self._json_response(400, {"error": "unsupported tool"})
                    return
                proj["tool"] = data["tool"]
            if "model" in data:
                # C2: validate model_id against allowlist for the current tool
                _tool_key = data.get("tool") or proj.get("tool", "")
                _tool_models = [m["id"] for m in KNOWN_TOOLS.get(_tool_key, {}).get("models", [])]
                if _tool_models and data["model"] not in _tool_models:
                    self._json_response(400, {"error": "unsupported model for tool"})
                    return
                proj["model"] = data["model"]
            if "project_name" in data:
                proj["project_name"] = data["project_name"]
            if "project_type" in data:
                proj["project_type"] = data["project_type"]
            if "skip_org_context" in data:
                proj["skip_org_context"] = data["skip_org_context"]
            if "git" in data and "kb_repo_url" in data["git"]:
                proj["git"]["kb_repo_url"] = data["git"]["kb_repo_url"]
            save_project_state(proj)
            # Signal Electron to persist new PAT in safeStorage (never write to disk).
            # The file is 0600, lives briefly, and is deleted by the Electron poller.
            if new_pat:
                _signal = os.path.expanduser(PAT_SIGNAL_PATH)
                try:
                    _forge_dir_local = os.path.dirname(_signal)
                    os.makedirs(_forge_dir_local, exist_ok=True)
                    # Write to a temp file then rename for atomic delivery
                    _fd, _tmp = tempfile.mkstemp(dir=_forge_dir_local, prefix="_pat_tmp_")
                    try:
                        with os.fdopen(_fd, "w") as _sf:
                            _sf.write(new_pat)
                        os.chmod(_tmp, 0o600)
                        os.replace(_tmp, _signal)
                    except OSError:
                        try:
                            os.unlink(_tmp)
                        except OSError:
                            pass
                        raise
                except OSError as exc:
                    logger.warning("PAT signal write failed: %s", exc)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/gate":
            gate_name = data.get("gate")
            # H4+M1: validate gate_name
            if gate_name not in GATE_STAGE_MAP:
                self._json_response(400, {"error": "invalid gate"})
                return
            gate_path = os.path.join(FORGE_DIR, DIR_GATES, f"{gate_name}.md")
            if os.path.exists(gate_path):
                with open(gate_path, "r") as f:
                    content = f.read()
                content = content.replace(GATE_STATUS_PENDING, GATE_STATUS_PASSED)
                with open(gate_path, "w") as f:
                    f.write(content)
                self._json_response(200, {"status": "success"})
            else:
                self._json_response(404, {"error": "gate not found"})
            return

        if path == "/api/review":
            file_path = data.get("path")
            status = data.get("status")
            if not file_path or status not in (REVIEW_REVIEWED, REVIEW_NEEDS_REVIEW):
                self._json_response(400, {"error": "invalid"})
                return
            reviews = load_reviews()
            if status == REVIEW_REVIEWED:
                reviews[file_path] = REVIEW_REVIEWED
            else:
                reviews.pop(file_path, None)
            save_reviews(reviews)
            for gate_name in GATE_STAGE_MAP:
                gate_status = evaluate_gate(gate_name)
                gate_path = os.path.join(FORGE_DIR, DIR_GATES, f"{gate_name}.md")
                if os.path.exists(gate_path):
                    with open(gate_path, "r") as gf:
                        lines = gf.readlines()
                    new_lines = []
                    in_status = False
                    changed = False
                    for line in lines:
                        if line.strip().startswith("## Status"):
                            in_status = True
                            new_lines.append(line)
                            continue
                        if in_status and line.strip():
                            in_status = False
                            if line.strip() != gate_status:
                                new_lines.append(gate_status + "\n")
                                changed = True
                                continue
                        new_lines.append(line)
                    if changed:
                        with open(gate_path, "w") as gf:
                            gf.writelines(new_lines)
            self._json_response(200, {"status": "success"})
            return

        if path == "/api/fix":
            file_path = data.get("path")
            critique = data.get("critique")
            if not file_path or not critique:
                self._json_response(400, {"error": "missing fields"})
                return
            # M2: validate file_path stays within FORGE_DIR
            _fp_abs = os.path.normpath(os.path.join(FORGE_DIR, file_path))
            if not _fp_abs.startswith(FORGE_DIR + os.sep):
                self._json_response(400, {"error": "invalid path"})
                return

            # Concurrent operation guard
            status_file_fix = os.path.join(FORGE_DIR, FILE_STATUS)
            if os.path.exists(status_file_fix):
                try:
                    with open(status_file_fix) as _scf:
                        _cur_status = json.load(_scf)
                    if _cur_status.get("status") == STATUS_RUNNING:
                        self._json_response(409, {"error": "A generation is already in progress"})
                        return
                except (OSError, json.JSONDecodeError) as exc:
                    logger.debug("status_file_fix read: %s", exc)

            stage = file_path.split("/")[0].split("-", 1)[1] if "-" in file_path.split("/")[0] else "context"
            status_file = os.path.join(FORGE_DIR, FILE_STATUS)

            def run_fix():
                _consistency = None
                try:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(status_file, "w") as sf:
                            json.dump({"status": STATUS_FIXING, "stage": stage, "file": file_path, "updated_at": datetime.now().isoformat()}, sf)
                    cmd = [sys.executable, os.path.join(FORGE_DIR, "scripts/run.py"), stage, "--output", file_path, "--critique", critique]
                    result = subprocess.run(cmd, cwd=REPO_ROOT)
                    if result.returncode == 0:
                        _proj = load_project_state()
                        _consistency = _run_consistency_check(file_path, _proj)
                finally:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        _payload = {"status": STATUS_IDLE, "stage": stage, "file": file_path, "updated_at": datetime.now().isoformat()}
                        if _consistency:
                            _payload["consistency_check"] = _consistency
                        with open(status_file, "w") as sf:
                            json.dump(_payload, sf)

            t = threading.Thread(target=run_fix, daemon=True)
            t.start()
            self._json_response(200, {"status": "started"})
            return

        if path == "/api/version/restore":
            file_path = data.get("path")
            ver_id    = data.get("id")
            if not file_path or not ver_id:
                self._json_response(400, {"error": "missing path or id"})
                return
            # C1: validate ver_id to timestamp format only — prevents directory traversal
            if not re.fullmatch(r'\d{8}-\d{6}', ver_id):
                self._json_response(400, {"error": "invalid version id"})
                return
            # C1: validate file_path stays within FORGE_DIR
            stem = file_path[:-3] if file_path.endswith(".md") else file_path
            ver_path  = os.path.normpath(os.path.join(FORGE_DIR, "versions", stem, f"{ver_id}.md"))
            dest_path = os.path.normpath(os.path.join(FORGE_DIR, file_path))
            _versions_base = os.path.join(FORGE_DIR, "versions") + os.sep
            if not ver_path.startswith(_versions_base):
                self._json_response(403, {"error": "forbidden"})
                return
            if not dest_path.startswith(FORGE_DIR + os.sep):
                self._json_response(403, {"error": "forbidden"})
                return
            if not os.path.exists(ver_path):
                self._json_response(404, {"error": "version not found"})
                return
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                ver_dir = os.path.join(FORGE_DIR, "versions", stem)
                os.makedirs(ver_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                shutil.copy2(dest_path, os.path.join(ver_dir, f"{ts}.md"))
            with open(ver_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._json_response(200, {"status": "restored"})
            return

        if path == "/api/reset":
            stage_dirs = ALL_STAGE_DIRS
            cleared = 0
            for d in stage_dirs:
                dir_path = os.path.join(FORGE_DIR, d)
                if os.path.isdir(dir_path):
                    for fname in os.listdir(dir_path):
                        if fname.endswith(MARKDOWN_EXTENSION):
                            with open(os.path.join(dir_path, fname), "w") as f:
                                f.write("")
                            cleared += 1
            save_reviews({})
            gates = ALL_GATE_NAMES
            for gate in gates:
                gate_path = os.path.join(FORGE_DIR, DIR_GATES, f"{gate}.md")
                if os.path.exists(gate_path):
                    with open(gate_path, "r") as gf:
                        lines = gf.readlines()
                    new_lines = []
                    in_status = False
                    for line in lines:
                        if line.strip().startswith("## Status"):
                            in_status = True
                            new_lines.append(line)
                            continue
                        if in_status and line.strip():
                            in_status = False
                            new_lines.append(GATE_STATUS_PENDING + "\n")
                            continue
                        new_lines.append(line)
                    with open(gate_path, "w") as gf:
                        gf.writelines(new_lines)
            status_file = os.path.join(FORGE_DIR, FILE_STATUS)
            with open(status_file, "w") as sf:
                json.dump({"status": STATUS_IDLE, "stage": "", "updated_at": datetime.now().isoformat()}, sf)
            self._json_response(200, {"status": "reset", "cleared": cleared})
            return

        if path == "/api/build-system":
            step = data.get("step", "")
            # Allow caller to pass explicit phase_id; fall back to active_phase_id in state
            req_phase_id = data.get("phase_id", "").strip()
            step_keys = ["backend", "frontend", "integration", "tests", "infra"]
            if step != "all" and step not in step_keys:
                self._json_response(400, {"error": "Unknown step: " + step})
                return

            def run_build_system():
                set_processing(STATUS_RUNNING, step)
                try:
                    proj = load_project_state()
                    # Resolve phase: explicit > active > none
                    phase_id = req_phase_id or proj.get("active_phase_id", "") or ""
                    phase_name = ""
                    if phase_id:
                        phase_name = next(
                            (p["name"] for p in proj.get("phases", []) if p["id"] == phase_id), ""
                        )
                    env = {
                        **os.environ,
                        "FORGE_TOOL":  proj.get("tool", DEFAULT_TOOL),
                        "FORGE_MODEL": proj.get("model", ""),
                        "AEOS_REPO_ROOT": REPO_ROOT,
                        FORGE_PHASE_ID_ENV:   phase_id,
                        FORGE_PHASE_NAME_ENV: phase_name,
                    }
                    steps_to_run = step_keys if step == "all" else [step]
                    build_runner = os.path.join(FORGE_DIR, "scripts", "build_runner.py")
                    for s in steps_to_run:
                        set_processing(STATUS_RUNNING, s)
                        subprocess.run([sys.executable, build_runner, s], cwd=REPO_ROOT, env=env)
                finally:
                    set_processing(STATUS_IDLE)

            t = threading.Thread(target=run_build_system, daemon=True)
            t.start()
            self._json_response(200, {"status": "started"})
            return

        if path == "/api/secrets":
            proj = load_project_state()
            git_cfg = proj.get("git", {})
            repo_url = git_cfg.get("repo_url", "")
            token = git_cfg.get("token", "") or GIT_PAT

            gh_owner, gh_repo = "", ""
            if repo_url:
                import re as _re2
                m = _re2.search(r"github\.com[/:]([^/]+)/([^/\.]+)", repo_url)
                if m:
                    gh_owner, gh_repo = m.group(1), m.group(2)

            name = data.get("name", "").strip().upper()
            value = data.get("value", "")
            protected = data.get("protected", True)

            if not name or not value:
                self._json_response(400, {"error": "name and value required"})
                return

            if not gh_owner or not gh_repo:
                self._json_response(400, {"error": "Git repo URL not configured in Settings"})
                return

            if not token:
                self._json_response(400, {"error": "GitHub token not configured in Settings"})
                return

            # Try gh CLI first (handles libsodium encryption for secrets)
            gh_check = subprocess.run(["which", "gh"], capture_output=True, text=True)
            if gh_check.returncode == 0:
                if protected:
                    cmd = ["gh", "secret", "set", name, "--body", value,
                           "--repo", f"{gh_owner}/{gh_repo}"]
                else:
                    cmd = ["gh", "variable", "set", name, "--body", value,
                           "--repo", f"{gh_owner}/{gh_repo}"]
                env = {**os.environ, "GH_TOKEN": token, "GITHUB_TOKEN": token}
                r = subprocess.run(cmd, capture_output=True, text=True, env=env)
                if r.returncode != 0:
                    self._json_response(500, {"error": r.stderr.strip() or r.stdout.strip()})
                    return
            else:
                # H2: no gh CLI available — for protected secrets, fail fast with clear message
                if protected:
                    self._json_response(400, {"error": "Install GitHub CLI (gh) to push protected secrets. Run: brew install gh"})
                    return
                else:
                    # Variables use plain text via API (safe, no crypto needed)
                    chk = subprocess.run([
                        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                        "-H", f"Authorization: token {token}",
                        f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/variables/{name}"
                    ], capture_output=True, text=True, timeout=GIT_TIMEOUT_SECS)
                    method = "PATCH" if chk.stdout.strip() == "200" else "POST"
                    url_var = f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/variables"
                    if method == "PATCH":
                        url_var += f"/{name}"
                    api_payload = json.dumps({"name": name, "value": value}).encode()
                    curl_r = subprocess.run([
                        "curl", "-s", "-X", method,
                        "-H", f"Authorization: token {token}",
                        "-H", "Accept: application/vnd.github.v3+json",
                        "-H", "Content-Type: application/json",
                        "-d", api_payload,
                        url_var
                    ], capture_output=True, text=True, timeout=NETWORK_TIMEOUT_SECS)
                    if curl_r.returncode != 0:
                        self._json_response(500, {"error": curl_r.stderr.strip()})
                        return

            # Track which secrets have been configured (without storing values)
            proj = load_project_state()
            configured = proj.get("secrets_configured", [])
            entry = {"name": name, "protected": protected, "set_at": datetime.now().isoformat()}
            proj["secrets_configured"] = [s for s in configured if s.get("name") != name] + [entry]
            save_project_state(proj)

            self._json_response(200, {"status": "ok", "name": name, "protected": protected})
            return

        self._json_response(404, {"error": "not found"})


# ---------------------------------------------------------------------------
# Post-fix consistency check
# ---------------------------------------------------------------------------

def _parse_diff_files(diff_text):
    """Parse raw `git diff` output into a list of per-file dicts."""
    files = []
    current = None
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            if current is not None:
                current["patch"] = "\n".join(current["_lines"])[:8000]
                del current["_lines"]
                files.append(current)
            parts = line.split(" ")
            # Extract path from "b/<path>" at end of header
            path = parts[-1][2:] if parts[-1].startswith("b/") else parts[-1]
            current = {"path": path, "additions": 0, "deletions": 0, "_lines": []}
        elif current is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current["additions"] += 1
                current["_lines"].append(line)
            elif line.startswith("-") and not line.startswith("---"):
                current["deletions"] += 1
                current["_lines"].append(line)
            elif line.startswith(("@@", " ", "\\")):
                current["_lines"].append(line)
    if current is not None:
        current["patch"] = "\n".join(current["_lines"])[:8000]
        del current["_lines"]
        files.append(current)
    return files


def _run_consistency_check(fixed_rel, proj):
    """
    After a fix, scan reviewed downstream docs for inconsistencies with the
    updated file. Marks affected docs as needs_review and returns a results
    dict (or None on failure/skip).

    This is best-effort — any exception is swallowed so the fix always
    completes cleanly even when the AI call fails.
    """
    try:
        fixed_abs = os.path.join(FORGE_DIR, fixed_rel)
        if not os.path.exists(fixed_abs):
            return None
        with open(fixed_abs, "r", encoding=FILE_ENCODING) as f:
            fixed_content = f.read()
        if not fixed_content.strip():
            return None

        fixed_stage_dir = fixed_rel.split("/")[0]
        try:
            fixed_idx = ALL_STAGE_DIRS.index(fixed_stage_dir)
        except ValueError:
            return None

        # Collect reviewed docs from all stages downstream of the fixed file
        reviews = load_reviews()
        downstream = []
        for stage_dir in ALL_STAGE_DIRS[fixed_idx + 1:]:
            if len(downstream) >= CONSISTENCY_CHECK_MAX_DOWNSTREAM:
                break
            stage_path = os.path.join(FORGE_DIR, stage_dir)
            if not os.path.isdir(stage_path):
                continue
            for fname in sorted(os.listdir(stage_path)):
                if not fname.endswith(MARKDOWN_EXTENSION):
                    continue
                rel = f"{stage_dir}/{fname}"
                if reviews.get(rel) == REVIEW_REVIEWED:
                    downstream.append((rel, os.path.join(stage_path, fname)))
                if len(downstream) >= CONSISTENCY_CHECK_MAX_DOWNSTREAM:
                    break

        if not downstream:
            return None

        # Build downstream block (one snippet per doc)
        downstream_block = ""
        for rel, abs_path in downstream:
            try:
                with open(abs_path, "r", encoding=FILE_ENCODING) as f:
                    snippet = f.read()[:CONSISTENCY_CHECK_DOC_CHARS]
                downstream_block += f"\n\n=== {rel} ===\n{snippet}"
            except OSError:
                pass
        if not downstream_block.strip():
            return None

        prompt = CONSISTENCY_CHECK_PROMPT.format(
            fixed_rel=fixed_rel,
            fixed_content=fixed_content[:CONSISTENCY_CHECK_FIXED_CHARS],
            downstream_block=downstream_block,
        )

        tool = proj.get("tool", DEFAULT_TOOL)
        model_id = proj.get("model", "")
        ai_result, ai_error = invoke_ai(prompt, tool, model_id)
        if ai_error or not ai_result or not ai_result.strip():
            return None

        # Parse FILE: / REASON: pairs from AI output
        affected = []
        lines = ai_result.splitlines()
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.lower().startswith("file:"):
                fname = stripped[5:].strip()
                reason = ""
                if i + 1 < len(lines) and lines[i + 1].strip().lower().startswith("reason:"):
                    reason = lines[i + 1].strip()[7:].strip()
                    i += 1
                if fname:
                    affected.append({"file": fname, "reason": reason})
            i += 1

        if not affected:
            return None

        # Mark affected docs as needs_review (only if they are valid downstream paths)
        valid_rels = {r for r, _ in downstream}
        reviews = load_reviews()
        marked = []
        for item in affected:
            rel = item["file"]
            if rel in valid_rels and reviews.get(rel) == REVIEW_REVIEWED:
                reviews[rel] = REVIEW_NEEDS_REVIEW
                marked.append(item)
        if marked:
            save_reviews(reviews)

        result = {
            "source": fixed_rel,
            "checked_at": datetime.now().isoformat(),
            "affected_count": len(marked),
            "affected": marked,
        }

        check_file = os.path.join(FORGE_DIR, FILE_CONSISTENCY_CHECK)
        os.makedirs(os.path.dirname(check_file), exist_ok=True)
        with open(check_file, "w", encoding=FILE_ENCODING) as f:
            json.dump(result, f, indent=2)

        logger.info("consistency_check: %d downstream docs marked for re-review after fix of %s", len(marked), fixed_rel)
        return result

    except Exception as exc:
        logger.warning("_run_consistency_check: %s", exc)
        return None


def run_server(port=DEFAULT_PORT):
    # C1: Bind to loopback only — never expose to 0.0.0.0 in production
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, ForgeHandler)
    print(f"Forge Dashboard running at http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run_server(port)
