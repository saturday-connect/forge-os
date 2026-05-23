"""
Build constants for the Forge build system.

All hardcoded strings, paths, markers, and log messages used by build_forge.py
are centralized here for maintainability and to prevent magic-string drift.
"""

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
FORGE_VERSION = "0.3.4"

# ---------------------------------------------------------------------------
# pformat widths
# ---------------------------------------------------------------------------
PFORMAT_WIDE = 120
PFORMAT_NORMAL = 100

# ---------------------------------------------------------------------------
# File encoding
# ---------------------------------------------------------------------------
FILE_ENCODING = "utf-8"

# ---------------------------------------------------------------------------
# Directory names (relative to src/)
# ---------------------------------------------------------------------------
DATA_DIR_NAME = "data"
AGENTS_DIR_NAME = "agents"
GATES_DIR_NAME = "gates"
DASHBOARD_DIR_NAME = "dashboard"
SCRIPTS_DIR_NAME = "scripts"
RUNTIME_DIR_NAME = "runtime"
PROMPTS_DIR_NAME = "prompts"

# ---------------------------------------------------------------------------
# Data file names (inside data/)
# ---------------------------------------------------------------------------
TOOLS_DATA_FILE = "tools.json"
BUILD_STEPS_DATA_FILE = "build_steps.json"
STAGES_DATA_FILE = "stages.json"
STAGE_PIPELINE_DATA_FILE = "stage_pipeline.json"

# ---------------------------------------------------------------------------
# Prompt files (inside data/prompts/)
# ---------------------------------------------------------------------------
AGENT_PROMPT_FILE = "agent_prompt.md"
DISTILL_PROMPT_FILE = "distill_prompt.md"

# ---------------------------------------------------------------------------
# Data JSON keys
# ---------------------------------------------------------------------------
JSON_KEY_STEPS = "steps"
JSON_KEY_ORDER = "order"
JSON_KEY_MODELS = "models"
JSON_KEY_MODEL_ID = "id"
JSON_KEY_AGENT = "agent"
JSON_KEY_STAGE_AGENT = "stage_agent"
JSON_KEY_STAGE_GATE = "stage_gate"
JSON_KEY_STAGE_INPUTS = "stage_inputs"
JSON_KEY_DIRECTORIES = "directories"

# ---------------------------------------------------------------------------
# Agent / gate file extension
# ---------------------------------------------------------------------------
MARKDOWN_EXTENSION = ".md"

# ---------------------------------------------------------------------------
# Runtime source files (relative to runtime/)
# ---------------------------------------------------------------------------
RUNTIME_CONSTANTS_FILE = "constants.py"
RUNTIME_SERVER_FILE = "server.py"
RUNTIME_BUILD_RUNNER_FILE = "build_runner.py"
RUNTIME_CLI_TEMPLATE_FILE = "forge_cli.py.tmpl"

# ---------------------------------------------------------------------------
# Dashboard source files
# ---------------------------------------------------------------------------
DASHBOARD_OUTPUT_FILE = "dashboard.html"
DASHBOARD_INDEX_FILE = "index.html"
DASHBOARD_STYLES_FILE = "styles.css"

# ---------------------------------------------------------------------------
# Dashboard template markers
# ---------------------------------------------------------------------------
DASHBOARD_CSS_MARKER = "<!-- FORGE_DASHBOARD_CSS -->"
DASHBOARD_SCRIPT_PATTERN = r'<!-- FORGE_DASHBOARD_SCRIPT:([\w\-\.]+) -->'
DASHBOARD_SCRIPT_MARKER_TEMPLATE = "<!-- FORGE_DASHBOARD_SCRIPT:{name} -->"

# ---------------------------------------------------------------------------
# Placeholder tokens in runtime source files (replaced during build)
# ---------------------------------------------------------------------------
PLACEHOLDER_KNOWN_TOOLS = "KNOWN_TOOLS = {}  # __FORGE_KNOWN_TOOLS__"
PLACEHOLDER_BUILD_STEPS = "STEPS = {}  # __FORGE_BUILD_STEPS__"
PLACEHOLDER_SERVER_PY = "__FORGE_SERVER_PY__"
PLACEHOLDER_AGENT_PROMPT = "__FORGE_AGENT_PROMPT__"
PLACEHOLDER_DISTILL_PROMPT = "__FORGE_DISTILL_PROMPT__"

# ---------------------------------------------------------------------------
# Code generation variable names (emitted into the built forge binary)
# ---------------------------------------------------------------------------
CODEGEN_KNOWN_TOOLS = "KNOWN_TOOLS = "
CODEGEN_ALLOWED_MODELS_OPEN = "_ALLOWED_MODELS = {"
CODEGEN_ALLOWED_MODELS_CLOSE = "}"
CODEGEN_STEPS = "STEPS = "
CODEGEN_BUILD_ORDER = "BUILD_ORDER = "
CODEGEN_STAGE_MULTI_OUTPUTS = "STAGE_MULTI_OUTPUTS = "
CODEGEN_STAGE_AGENT = "STAGE_AGENT = "
CODEGEN_STAGE_GATE = "STAGE_GATE = "
CODEGEN_STAGE_INPUTS = "STAGE_INPUTS = "
CODEGEN_PIPELINE_STAGES = "PIPELINE_STAGES = "
CODEGEN_AGENT_CONTENT_OPEN = "AGENT_CONTENT = {"
CODEGEN_AGENT_CONTENT_CLOSE = "}"
CODEGEN_GATE_CONTENT_OPEN = "GATE_CONTENT = {"
CODEGEN_GATE_CONTENT_CLOSE = "}"
CODEGEN_DIRECTORIES_OPEN = "    directories = ["
CODEGEN_DIRECTORIES_CLOSE = "    ]"
CODEGEN_AGENTS_OPEN = "    agents = ["
CODEGEN_AGENTS_CLOSE = "    ]"
CODEGEN_GATES_OPEN = "    gates = ["
CODEGEN_GATES_CLOSE = "    ]"

# ---------------------------------------------------------------------------
# Build output file name
# ---------------------------------------------------------------------------
BUILD_OUTPUT_FILE = "forge"

# ---------------------------------------------------------------------------
# Hot-deploy glob patterns (relative to repo root)
# ---------------------------------------------------------------------------
HOT_DEPLOY_GLOBS = [
    ".forge/scripts",
    ".projects/*/.forge/scripts",
    "test-projects/*/.forge/scripts",
]
HOT_DEPLOY_SIBLING_GLOB = "*/.forge/scripts"
HOT_DEPLOY_HOME_DIR = ".forge"
HOT_DEPLOY_HOME_PROJECTS_GLOB = "projects/*/scripts"  # ~/.forge/projects/<uuid>/scripts

# ---------------------------------------------------------------------------
# Hot-deploy target file names
# ---------------------------------------------------------------------------
HOT_DEPLOY_FILES = [
    DASHBOARD_OUTPUT_FILE,
    RUNTIME_SERVER_FILE,
    RUNTIME_CONSTANTS_FILE,
    RUNTIME_BUILD_RUNNER_FILE,
]

# ---------------------------------------------------------------------------
# Log / output messages
# ---------------------------------------------------------------------------
LOG_BUILD_SUCCESS = "forge built successfully."
LOG_HOT_DEPLOY_SINGULAR = "Dashboard + server hot-deployed to {count} runtime directory."
LOG_HOT_DEPLOY_PLURAL = "Dashboard + server hot-deployed to {count} runtime directories."
