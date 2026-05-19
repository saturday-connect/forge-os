# Timeouts (seconds)
GENERATE_TIMEOUT_SECS   = 600   # AI generation subprocess
AI_POLL_TIMEOUT_SECS    = 300   # background AI process wait
GIT_TIMEOUT_SECS        = 15    # git subprocess calls
NETWORK_TIMEOUT_SECS    = 20    # network/HTTP operations
HTTP_CHECK_TIMEOUT_SECS = 10    # health-check HTTP request

# Request / body limits
MAX_BODY_BYTES = 4 * 1024 * 1024  # 4 MB POST/DELETE body cap

# Diff / review thresholds
DIFF_CHAR_LIMIT              = 4000  # max diff chars passed to AI
LARGE_CHANGESET_THRESHOLD    = 800   # changed lines -> large-changeset review mode
DIFF_HEADER_LINES            = 200   # max header lines included in AI diff

# Error message display
ERROR_PREVIEW_LEN   = 220  # chars shown for quota/rate-limit errors
DESCRIPTION_MAX_LEN = 200  # chars for phase description truncation

# Server
DEFAULT_PORT = 8080

# Git defaults
DEFAULT_BRANCH        = "main"
DEFAULT_BRANCH_PREFIX = "forge"

# Build source-block markers (used in collect_docs and build_runner)
SOURCE_MARKER     = "=== SOURCE: "
SOURCE_MARKER_END = " ==="

# OpenAI direct API
OPENAI_API_URL       = "https://api.openai.com/v1/chat/completions"
OPENAI_DEFAULT_MODEL = "gpt-4o"
