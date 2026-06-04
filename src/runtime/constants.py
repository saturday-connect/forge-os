"""
Runtime constants for the Forge OS server, build runner, and CLI template.

All reusable string literals, file paths, status values, phase names, tool
identifiers, directory names, and configuration defaults used at runtime are
centralized here.  This file is deployed to .forge/scripts/constants.py and
imported by both server.py and build_runner.py.
"""

# ---------------------------------------------------------------------------
# Timeouts (seconds)
# ---------------------------------------------------------------------------
GENERATE_TIMEOUT_SECS = 1800    # AI generation subprocess (30 min — Claude on large steps needs 15-20 min)
AI_POLL_TIMEOUT_SECS = 300      # background AI process wait
GIT_TIMEOUT_SECS = 15           # git subprocess calls
NETWORK_TIMEOUT_SECS = 20       # network/HTTP operations
HTTP_CHECK_TIMEOUT_SECS = 10    # health-check HTTP request

# ---------------------------------------------------------------------------
# Request / body limits
# ---------------------------------------------------------------------------
MAX_BODY_BYTES = 4 * 1024 * 1024  # 4 MB POST/DELETE body cap

# ---------------------------------------------------------------------------
# Diff / review thresholds
# ---------------------------------------------------------------------------
DIFF_CHAR_LIMIT = 4000              # max diff chars passed to AI
LARGE_CHANGESET_THRESHOLD = 800     # changed lines -> large-changeset review
DIFF_HEADER_LINES = 200             # max header lines included in AI diff

# ---------------------------------------------------------------------------
# Error message display
# ---------------------------------------------------------------------------
ERROR_PREVIEW_LEN = 220     # chars shown for quota/rate-limit errors
DESCRIPTION_MAX_LEN = 200   # chars for phase description truncation

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
DEFAULT_PORT = 8080

# ---------------------------------------------------------------------------
# File encoding and timestamp format
# ---------------------------------------------------------------------------
FILE_ENCODING = "utf-8"
ISO_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
VERSION_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"

# ---------------------------------------------------------------------------
# Git defaults
# ---------------------------------------------------------------------------
DEFAULT_BRANCH = "main"
DEFAULT_BRANCH_PREFIX = "forge"

# ---------------------------------------------------------------------------
# Build source-block markers (used in collect_docs and build_runner)
# ---------------------------------------------------------------------------
SOURCE_MARKER = "=== SOURCE: "
SOURCE_MARKER_END = " ==="

# ---------------------------------------------------------------------------
# OpenAI direct API
# ---------------------------------------------------------------------------
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_DEFAULT_MODEL = "gpt-4o"

# ---------------------------------------------------------------------------
# AI tool identifiers
# ---------------------------------------------------------------------------
TOOL_ANTIGRAVITY = "agy"           # Antigravity CLI — successor to Gemini CLI (June 2026+)
TOOL_GEMINI = "gemini"             # deprecated — ends June 18 2026; kept for enterprise
TOOL_CLAUDE = "claude"
TOOL_CODEX = "codex"
TOOL_OPENAI = "openai"
DEFAULT_TOOL = TOOL_ANTIGRAVITY

# ---------------------------------------------------------------------------
# AI tool CLI arguments
# ---------------------------------------------------------------------------
# Antigravity CLI (agy) — different interface from Gemini CLI
ANTIGRAVITY_ARG_PRINT = "-p"                          # non-interactive single-prompt mode
ANTIGRAVITY_ARG_SKIP_PERMISSIONS = "--dangerously-skip-permissions"
# Gemini CLI (deprecated)
GEMINI_ARG_SKIP_TRUST = "--skip-trust"
GEMINI_ARG_MODEL = "-m"
GEMINI_ARG_PROMPT = "-p"
CLAUDE_ARG_PROMPT = "-p"
CLAUDE_ARG_MODEL = "--model"
CLAUDE_ARG_OUTPUT_FORMAT = "--output-format"
CLAUDE_OUTPUT_TEXT = "text"

# ---------------------------------------------------------------------------
# Status values (shared across server, build_runner, template scripts)
# ---------------------------------------------------------------------------
STATUS_IDLE = "idle"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_PENDING = "pending"
STATUS_BUILDING = "building"
STATUS_ERROR = "error"
STATUS_COMPLETE = "complete"
STATUS_NOT_REQUIRED = "not_required"
STATUS_DISTILLING = "distilling"
STATUS_FIXING = "fixing"
STATUS_REVIEWING = "reviewing"

# ---------------------------------------------------------------------------
# Review status values
# ---------------------------------------------------------------------------
REVIEW_REVIEWED = "reviewed"
REVIEW_NEEDS_REVIEW = "needs_review"
REVIEW_EMPTY = "empty"

# ---------------------------------------------------------------------------
# Phase values
# ---------------------------------------------------------------------------
PHASE_INPUT = "input"
PHASE_GENERATE = "generate"
PHASE_REVIEW = "review"
PHASE_BUILD = "build"
PHASE_DEPLOY = "deploy"

# ---------------------------------------------------------------------------
# Lifecycle phases (template scripts)
# ---------------------------------------------------------------------------
PHASE_INITIALIZED = "initialized"
PHASE_BUILDING_PRODUCT = "building_product"
PHASE_READY_FOR_EXECUTION = "ready_for_execution"
PHASE_BUILD_FAILED = "build_failed"
PHASE_DOCS_GENERATED = "docs_generated"
PHASE_DOCS_REITERATING = "reiterating_docs"
PHASE_ISSUE_FAILED = "issue_failed"

# ---------------------------------------------------------------------------
# Project status values
# ---------------------------------------------------------------------------
PROJECT_STATUS_ACTIVE = "active"
PROJECT_STATUS_ARCHIVED = "archived"

# ---------------------------------------------------------------------------
# Build verdict values
# ---------------------------------------------------------------------------
VERDICT_APPROVE = "approve"
VERDICT_APPROVE_WITH_NOTES = "approve_with_notes"
VERDICT_REQUEST_CHANGES = "request_changes"
VERDICT_UNKNOWN = "unknown"
VERDICT_ERROR = "error"

# ---------------------------------------------------------------------------
# Build entry status values
# ---------------------------------------------------------------------------
BUILD_STATUS_BRANCHED = "branched"
BUILD_STATUS_COMMITTED = "committed"
BUILD_STATUS_PUSHING = "pushing"
BUILD_STATUS_PUSHED = "pushed"
BUILD_STATUS_PR_CREATED = "pr_created"
BUILD_STATUS_MERGED = "merged"
BUILD_STATUS_LOCAL = "local"           # committed locally; no remote configured
BUILD_STATUS_VALIDATING = "validating" # running syntax / test / docker-config checks

# ---------------------------------------------------------------------------
# Gate status values
# ---------------------------------------------------------------------------
GATE_STATUS_PASSED = "PASSED"
GATE_STATUS_PENDING = "PENDING"
GATE_STATUS_APPROVED = "APPROVED"

# ---------------------------------------------------------------------------
# Directory names (.forge/ subdirectories)
# ---------------------------------------------------------------------------
DIR_RAW_INPUT = "00-raw-input"
DIR_CONTEXT = "00-context"
DIR_REQUIREMENTS = "01-requirements"
DIR_DESIGN = "02-design"
DIR_ANALYSIS = "03-analysis"
DIR_ARCHITECTURE = "04-architecture"
DIR_DELIVERY = "05-delivery"
DIR_ENGINEERING = "06-engineering"
DIR_QUALITY = "07-quality"
DIR_OPERATIONS = "08-operations"
DIR_RELEASE = "09-release"
DIR_MARKETING = "10-marketing"
DIR_AGENTS = "11-agents"
DIR_GATES = "12-gates"
DIR_DECISIONS = "13-decisions"
DIR_ASSETS = "14-assets"
DIR_BUILD = "15-build"
DIR_RUNS = "runs"
DIR_SCRIPTS = "scripts"
DIR_VERSIONS = "versions"
DIR_ISSUES = "issues"

# ---------------------------------------------------------------------------
# File names (inside .forge/)
# ---------------------------------------------------------------------------
FILE_PROJECT_STATE = "project-state.json"
FILE_REVIEWS = "reviews.json"
FILE_STATUS = "runs/status.json"
FILE_BUILD_SYSTEM = "runs/build-system.json"
FILE_STACK = "runs/stack.json"          # locked technology stack (pinned once, enforced every step)
# Cross-run build cache (shared by build_runner + server): ~/.forge/<dirname>
BUILD_CACHE_DIRNAME = "build-cache"
BUILD_CACHE_META_FILE = "_cache_meta.json"
FILE_BUILD_REVIEW = "runs/build-review.json"
FILE_BUILD_IN_PROGRESS = "runs/build-in-progress.json"
FILE_DISTILL_RESULT = "runs/distill-result.json"
FILE_RUN_LOG = "runs/run-log.md"
FILE_RUN_ERROR = "runs/last-run-error.json"
FILE_EXECUTION_HISTORY = "runs/execution-history.md"
FILE_FAILED_RUNS = "runs/failed-runs.md"
FILE_LIFECYCLE = "lifecycle.json"
FILE_RUNTIME_CONFIG = "runtime-config.json"
FILE_ISSUES = "issues/issues.json"
FILE_API_CONTRACT = "15-build/api-contract.md"
FILE_DECISION_LOG = "13-decisions/decision-log.md"
FILE_CHANGE_LOG = "13-decisions/change-log.md"
FILE_ADR_INDEX = "13-decisions/adr-index.md"

# ---------------------------------------------------------------------------
# User/Electron paths
# ---------------------------------------------------------------------------
USER_FILE_PATH = "~/.forge/user.json"
PAT_SIGNAL_PATH = "~/.forge/_pat_signal"

# ---------------------------------------------------------------------------
# Gate-to-stage mapping
# ---------------------------------------------------------------------------
GATE_STAGE_MAP = {
    "context-gate": DIR_CONTEXT,
    "prd-gate": DIR_REQUIREMENTS,
    "design-gate": DIR_DESIGN,
    "architecture-gate": DIR_ARCHITECTURE,
    "engineering-gate": DIR_ENGINEERING,
    "qa-gate": DIR_QUALITY,
    "release-gate": DIR_RELEASE,
    "marketing-gate": DIR_MARKETING,
}

# ---------------------------------------------------------------------------
# Stage directory mapping (stage name -> directory)
# ---------------------------------------------------------------------------
STAGE_DIR_MAP = {
    "context": DIR_CONTEXT,
    "requirements": DIR_REQUIREMENTS,
    "design": DIR_DESIGN,
    "analysis": DIR_ANALYSIS,
    "architecture": DIR_ARCHITECTURE,
    "delivery": DIR_DELIVERY,
    "engineering": DIR_ENGINEERING,
    "qa": DIR_QUALITY,
    "operations": DIR_OPERATIONS,
    "release": DIR_RELEASE,
    "marketing": DIR_MARKETING,
}

# ---------------------------------------------------------------------------
# All stage directories in order (for reset, tree building)
# ---------------------------------------------------------------------------
ALL_STAGE_DIRS = [
    DIR_CONTEXT, DIR_REQUIREMENTS, DIR_DESIGN, DIR_ANALYSIS,
    DIR_ARCHITECTURE, DIR_DELIVERY, DIR_ENGINEERING, DIR_QUALITY,
    DIR_OPERATIONS, DIR_RELEASE, DIR_MARKETING,
]

# ---------------------------------------------------------------------------
# Pipeline stage names in execution order
# ---------------------------------------------------------------------------
PIPELINE_STAGE_NAMES = [
    "context", "requirements", "design", "analysis", "architecture",
    "delivery", "engineering", "qa", "operations", "release", "marketing",
]

# ---------------------------------------------------------------------------
# Gate names (for reset)
# ---------------------------------------------------------------------------
ALL_GATE_NAMES = list(GATE_STAGE_MAP.keys())

# ---------------------------------------------------------------------------
# Local preview runner
# ---------------------------------------------------------------------------
FILE_LOCAL_RUN = "runs/local-run.json"
LOCAL_RUN_MAX_LOG = 300          # keep last N lines of process output
LOCAL_RUN_HEALTH_TIMEOUT = 90    # seconds to wait for a service to become reachable
LOCAL_RUN_HEALTH_POLL = 3        # seconds between health-check probes

# ---------------------------------------------------------------------------
# Build stuck-detection thresholds (seconds since last heartbeat)
# ---------------------------------------------------------------------------
BUILD_STUCK_WARN_SECS = 30   # show "taking longer than expected" strip
BUILD_STUCK_KILL_SECS = 60   # show prominent Stop button

# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------
BUILD_STEP_KEYS = ["backend", "frontend", "integration", "tests", "infra"]

# ---------------------------------------------------------------------------
# Build step output directories (relative to .forge/)
# ---------------------------------------------------------------------------
BUILD_STEP_DIRS = {step: f"{DIR_BUILD}/{step}" for step in BUILD_STEP_KEYS}

# ---------------------------------------------------------------------------
# Departments (role-based stage visibility)
# ---------------------------------------------------------------------------
DEPARTMENTS = {
    "all":         list(range(11)),
    "product":     [0, 1],
    "design":      [2, 3],
    "engineering": [4, 5, 6, 7],
    "operations":  [8, 9],
    "marketing":   [10],
}

# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_REPOS = GITHUB_API_BASE + "/repos"
GITHUB_ACCEPT_HEADER = "application/vnd.github+json"
GITHUB_ACCEPT_V3_HEADER = "application/vnd.github.v3+json"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_USER_AGENT = "forge-os"
GITHUB_CONTENT_TYPE = "application/json"

# ---------------------------------------------------------------------------
# Git commit metadata
# ---------------------------------------------------------------------------
GIT_COMMIT_EMAIL = "forge-os@forge-os.local"
GIT_COMMIT_NAME = "Forge OS"

# ---------------------------------------------------------------------------
# HTTP headers and content types
# ---------------------------------------------------------------------------
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_HTML = "text/html; charset=utf-8"
CONTENT_TYPE_PLAIN = "text/plain; charset=utf-8"
CORS_ALLOW_ORIGIN = "*"
CORS_ALLOW_METHODS = "GET, POST, DELETE, OPTIONS"
CORS_ALLOW_HEADERS = "Content-Type, X-Forge-Token"
CACHE_CONTROL_NO_CACHE = "no-cache, no-store, must-revalidate"

# ---------------------------------------------------------------------------
# Spec file paths for build review (relative to .forge/)
# ---------------------------------------------------------------------------
SPEC_FILES_FOR_REVIEW = [
    ("Engineering spec", "06-engineering/backend-spec.md"),
    ("Frontend spec", "06-engineering/frontend-spec.md"),
    ("Architecture", "04-architecture/system-architecture.md"),
]

# ---------------------------------------------------------------------------
# Delivery doc scan directories and files (phase parsing)
# ---------------------------------------------------------------------------
DELIVERY_SCAN_DIRS = ["05-delivery", "01-requirements", "03-analysis"]
DELIVERY_SCAN_FILES = [
    "roadmap.md", "milestones.md", "epics.md", "release-roadmap.md",
    "sprint-plan.md", "brd.md", "user-stories.md",
]

# ---------------------------------------------------------------------------
# Default context directories (build_product.py)
# ---------------------------------------------------------------------------
DEFAULT_CONTEXT_DIRECTORIES = [
    DIR_ENGINEERING,
    DIR_ARCHITECTURE,
    DIR_DELIVERY,
    DIR_REQUIREMENTS,
    DIR_DESIGN,
    DIR_ANALYSIS,
]

# ---------------------------------------------------------------------------
# Quota / rate-limit error markers (for AI error normalization)
# ---------------------------------------------------------------------------
QUOTA_ERROR_MARKERS = [
    "you've hit your limit",
    "hit your limit",
    "usage limit",
    "quota",
    "rate limit",
    "too many requests",
    "status 429",
]

# ---------------------------------------------------------------------------
# Max context files for build product
# ---------------------------------------------------------------------------
MAX_CONTEXT_FILES = 12

# ---------------------------------------------------------------------------
# Markdown file extension
# ---------------------------------------------------------------------------
MARKDOWN_EXTENSION = ".md"

# ---------------------------------------------------------------------------
# Phase status values (for phase management)
# ---------------------------------------------------------------------------
PHASE_STATUS_PENDING = "pending"
PHASE_STATUS_ACTIVE = "active"
PHASE_STATUS_BUILT = "built"
PHASE_STATUS_MERGED = "merged"   # PR merged to main — code in mainline, not yet running
PHASE_STATUS_DEPLOYED = "deployed"  # Live URL confirmed

# ---------------------------------------------------------------------------
# Phase build env vars (passed to build_runner subprocess)
# ---------------------------------------------------------------------------
FORGE_PHASE_ID_ENV   = "FORGE_PHASE_ID"
FORGE_PHASE_NAME_ENV = "FORGE_PHASE_NAME"

# ---------------------------------------------------------------------------
# Issue defaults
# ---------------------------------------------------------------------------
ISSUE_ID_PREFIX = "ISSUE-"
ISSUE_DEFAULT_TYPE = "bug"
ISSUE_DEFAULT_PRIORITY = "medium"
ISSUE_STATUS_OPEN = "open"

# ---------------------------------------------------------------------------
# Secrets search paths (relative to .forge/)
# ---------------------------------------------------------------------------
SECRETS_SEARCH_PATHS = [
    "15-build/infra/secrets-required.md",
    "15-build/infra/infra/secrets-required.md",
    "15-build/secrets-required.md",
]

# ---------------------------------------------------------------------------
# Org context subdirectories
# ---------------------------------------------------------------------------
ORG_SUBDIRS = ("knowledge", "patterns")
ORG_AGENTS_SUBDIR = "agents"

# ---------------------------------------------------------------------------
# Build-review spec context snippet length
# ---------------------------------------------------------------------------
SPEC_SNIPPET_MAX_CHARS = 1000

# ---------------------------------------------------------------------------
# Valid stage prefix count (00 through 10)
# ---------------------------------------------------------------------------
VALID_STAGE_PREFIX_COUNT = 11

# ---------------------------------------------------------------------------
# State file schema versions — increment when the format of a state file
# changes in a backwards-incompatible way and add a migration branch in
# server.py (_migrate_index_schema / _migrate_project_state_schema).
# ---------------------------------------------------------------------------
INDEX_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1

# ---------------------------------------------------------------------------
# Consistency check
# ---------------------------------------------------------------------------
FILE_CONSISTENCY_CHECK = "runs/consistency-check.json"
CONSISTENCY_CHECK_MAX_DOWNSTREAM = 10   # max downstream docs to examine
CONSISTENCY_CHECK_DOC_CHARS = 1500      # chars per downstream doc in prompt
CONSISTENCY_CHECK_FIXED_CHARS = 4000    # chars of the fixed doc in prompt

# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------
KB_STATUS_IDLE = "idle"
KB_STATUS_EXPORTING = "exporting"
KB_STATUS_DISTILLING = "distilling"
KB_STATUS_DONE = "done"
KB_STATUS_ERROR = "error"

KB_PROJECTS_DIR = "projects"
KB_GLOBAL_PATTERNS = "global/patterns"
KB_GLOBAL_DECISIONS = "global/decisions"
KB_GLOBAL_LEARNINGS = "global/learnings"
KB_BRANCH_EXPORT_PREFIX = "kb/export"
KB_BRANCH_DISTILL_PREFIX = "kb/distill"
KB_REGISTRY_FILE = "registry.json"
KB_REGISTRY_SCHEMA_VERSION = 1
KB_VISIBILITY_ORG = "org"
KB_VISIBILITY_PUBLIC = "public"
KB_VISIBILITY_PRIVATE = "private"
FILE_KB_STATE = "runs/kb-state.json"
