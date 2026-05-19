"""
Shared constants for Forge template scripts.

These scripts (product_build_runner.py, build_product.py, issue_runner.py)
run standalone inside .forge/scripts/ at runtime.  They cannot import from
the src/ build tree, so constants are centralized here and co-deployed.
"""

# ---------------------------------------------------------------------------
# File encoding and timestamp format
# ---------------------------------------------------------------------------
FILE_ENCODING = "utf-8"
ISO_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# ---------------------------------------------------------------------------
# File names (relative to FORGE_ROOT)
# ---------------------------------------------------------------------------
FILE_LIFECYCLE = "lifecycle.json"
FILE_STATUS = "runs/status.json"
FILE_RUNTIME_CONFIG = "runtime-config.json"
FILE_ISSUES = "issues/issues.json"

# ---------------------------------------------------------------------------
# Directory names
# ---------------------------------------------------------------------------
DIR_ISSUES = "issues"
DIR_RUNS = "runs"
DIR_SCRIPTS = "scripts"

# ---------------------------------------------------------------------------
# Lifecycle phase values
# ---------------------------------------------------------------------------
PHASE_INITIALIZED = "initialized"
PHASE_BUILDING_PRODUCT = "building_product"
PHASE_READY_FOR_EXECUTION = "ready_for_execution"
PHASE_BUILD_FAILED = "build_failed"
PHASE_DOCS_GENERATED = "docs_generated"
PHASE_DOCS_REITERATING = "reiterating_docs"
PHASE_ISSUE_FAILED = "issue_failed"

# ---------------------------------------------------------------------------
# Status values
# ---------------------------------------------------------------------------
STATUS_IDLE = "idle"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_PENDING = "pending"
STATUS_BUILDING = "building"
STATUS_NOT_REQUIRED = "not_required"
STATUS_DOCS_UPDATED = "docs_updated"

# ---------------------------------------------------------------------------
# AI tool identifiers
# ---------------------------------------------------------------------------
TOOL_GEMINI = "gemini"
TOOL_CODEX = "codex"

# ---------------------------------------------------------------------------
# AI tool CLI arguments
# ---------------------------------------------------------------------------
GEMINI_ARGS_BASE = ["gemini", "--skip-trust", "--approval-mode", "auto_edit"]
CODEX_ARGS_BASE = [
    "codex",
    "--ask-for-approval", "never",
    "exec",
    "--skip-git-repo-check",
    "--sandbox", "workspace-write",
]

# ---------------------------------------------------------------------------
# Context directories (ordered by priority for build_product.py)
# ---------------------------------------------------------------------------
DEFAULT_CONTEXT_DIRECTORIES = [
    "06-engineering",
    "04-architecture",
    "05-delivery",
    "01-requirements",
    "02-design",
    "03-analysis",
]

# ---------------------------------------------------------------------------
# Max context files
# ---------------------------------------------------------------------------
MAX_CONTEXT_FILES = 12

# ---------------------------------------------------------------------------
# Markdown extension
# ---------------------------------------------------------------------------
MARKDOWN_EXTENSION = ".md"

# ---------------------------------------------------------------------------
# Build status kind
# ---------------------------------------------------------------------------
STATUS_KIND_BUILD = "build"
STATUS_KIND_ISSUE_DOCS = "issue-docs"

# ---------------------------------------------------------------------------
# Lifecycle default state keys
# ---------------------------------------------------------------------------
LIFECYCLE_KEY_PHASE = "phase"
LIFECYCLE_KEY_DOCS_STATUS = "docsStatus"
LIFECYCLE_KEY_BUILD_STATUS = "buildStatus"
LIFECYCLE_KEY_CURRENT_STAGE = "currentStage"
LIFECYCLE_KEY_LAST_ISSUE_ID = "lastIssueId"
LIFECYCLE_KEY_LAST_UPDATED_AT = "lastUpdatedAt"

# ---------------------------------------------------------------------------
# Prompt fragments (build_product.py)
# ---------------------------------------------------------------------------
PROMPT_ISSUE_HEADER = (
    "Implement the requested product change in this repository.\n"
    "Use the documentation context below as the source of truth.\n"
    "If code changes are required, edit the codebase directly.\n"
    "Do not rewrite documentation unless it is necessary to keep code and docs aligned.\n"
    "Prefer minimal, working changes.\n\n"
)

PROMPT_BASELINE_HEADER = (
    "Implement the product described by the current Forge documentation.\n"
    "Use the generated documentation as the source of truth.\n"
    "Edit the codebase directly and keep documentation aligned when necessary.\n"
    "Prefer the smallest working implementation that satisfies the documented plan.\n\n"
)

PROMPT_CONTEXT_FILES_LABEL = "Context files:\n"

PROMPT_CONTEXT_FILE_START = "\n--- START OF {rel_path} ---\n"
PROMPT_CONTEXT_FILE_END = "\n--- END OF {rel_path} ---\n"

PROMPT_RETURN_SUMMARY = "\nReturn a concise summary of what changed when done.\n"

# ---------------------------------------------------------------------------
# Usage messages
# ---------------------------------------------------------------------------
USAGE_PRODUCT_BUILD_RUNNER = "Usage: python3 scripts/product_build_runner.py"
USAGE_BUILD_PRODUCT = "Usage: python3 scripts/build_product.py [issue-id]"
USAGE_ISSUE_RUNNER = "Usage: python3 scripts/issue_runner.py <issue-id>"

# ---------------------------------------------------------------------------
# Error messages
# ---------------------------------------------------------------------------
ERROR_ISSUE_NOT_FOUND = "Issue not found: {issue_id}"
ERROR_UNSUPPORTED_TOOL = "Selected tool does not support code build orchestration: {tool_name}"

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------
ENV_FORGE_AI_TOOL = "FORGE_AI_TOOL"
ENV_FORGE_AI_MODEL = "FORGE_AI_MODEL"
