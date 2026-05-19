import os
import json as _json
from pprint import pformat

from build_constants import (
    FORGE_VERSION,
    PFORMAT_WIDE,
    PFORMAT_NORMAL,
    FILE_ENCODING,
    DATA_DIR_NAME,
    AGENTS_DIR_NAME,
    GATES_DIR_NAME,
    DASHBOARD_DIR_NAME,
    SCRIPTS_DIR_NAME,
    RUNTIME_DIR_NAME,
    TOOLS_DATA_FILE,
    BUILD_STEPS_DATA_FILE,
    STAGES_DATA_FILE,
    STAGE_PIPELINE_DATA_FILE,
    JSON_KEY_STEPS,
    JSON_KEY_ORDER,
    JSON_KEY_MODELS,
    JSON_KEY_MODEL_ID,
    JSON_KEY_AGENT,
    JSON_KEY_STAGE_AGENT,
    JSON_KEY_STAGE_GATE,
    JSON_KEY_STAGE_INPUTS,
    JSON_KEY_DIRECTORIES,
    MARKDOWN_EXTENSION,
    RUNTIME_CONSTANTS_FILE,
    RUNTIME_SERVER_FILE,
    RUNTIME_BUILD_RUNNER_FILE,
    RUNTIME_CLI_TEMPLATE_FILE,
    DASHBOARD_OUTPUT_FILE,
    DASHBOARD_INDEX_FILE,
    DASHBOARD_STYLES_FILE,
    DASHBOARD_CSS_MARKER,
    DASHBOARD_SCRIPT_PATTERN,
    DASHBOARD_SCRIPT_MARKER_TEMPLATE,
    PLACEHOLDER_KNOWN_TOOLS,
    PLACEHOLDER_BUILD_STEPS,
    PLACEHOLDER_SERVER_PY,
    PLACEHOLDER_AGENT_PROMPT,
    PLACEHOLDER_DISTILL_PROMPT,
    PROMPTS_DIR_NAME,
    AGENT_PROMPT_FILE,
    DISTILL_PROMPT_FILE,
    CODEGEN_KNOWN_TOOLS,
    CODEGEN_ALLOWED_MODELS_OPEN,
    CODEGEN_ALLOWED_MODELS_CLOSE,
    CODEGEN_STEPS,
    CODEGEN_BUILD_ORDER,
    CODEGEN_STAGE_MULTI_OUTPUTS,
    CODEGEN_STAGE_AGENT,
    CODEGEN_STAGE_GATE,
    CODEGEN_STAGE_INPUTS,
    CODEGEN_PIPELINE_STAGES,
    CODEGEN_AGENT_CONTENT_OPEN,
    CODEGEN_AGENT_CONTENT_CLOSE,
    CODEGEN_GATE_CONTENT_OPEN,
    CODEGEN_GATE_CONTENT_CLOSE,
    CODEGEN_DIRECTORIES_OPEN,
    CODEGEN_DIRECTORIES_CLOSE,
    CODEGEN_AGENTS_OPEN,
    CODEGEN_AGENTS_CLOSE,
    CODEGEN_GATES_OPEN,
    CODEGEN_GATES_CLOSE,
    BUILD_OUTPUT_FILE,
    HOT_DEPLOY_GLOBS,
    HOT_DEPLOY_SIBLING_GLOB,
    HOT_DEPLOY_HOME_DIR,
    HOT_DEPLOY_FILES,
    LOG_BUILD_SUCCESS,
    LOG_HOT_DEPLOY_SINGULAR,
    LOG_HOT_DEPLOY_PLURAL,
)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_DIR_NAME)


def _load_tools():
    with open(os.path.join(_DATA_DIR, TOOLS_DATA_FILE), encoding=FILE_ENCODING) as fh:
        return _json.load(fh)


KNOWN_TOOLS = _load_tools()


def _generate_known_tools_code(tools):
    return CODEGEN_KNOWN_TOOLS + pformat(tools, width=PFORMAT_WIDE)


def _generate_allowed_models_code(tools):
    allowed = {k: {m[JSON_KEY_MODEL_ID] for m in v[JSON_KEY_MODELS]} for k, v in tools.items()}
    lines = [CODEGEN_ALLOWED_MODELS_OPEN]
    for tool, models in allowed.items():
        model_list = ", ".join(f'"{m}"' for m in sorted(models))
        lines.append(f'    "{tool}": {{{model_list}}},')
    lines.append(CODEGEN_ALLOWED_MODELS_CLOSE)
    return "\n".join(lines)


def _load_build_steps():
    with open(os.path.join(_DATA_DIR, BUILD_STEPS_DATA_FILE), encoding=FILE_ENCODING) as fh:
        data = _json.load(fh)
    return data[JSON_KEY_STEPS], data[JSON_KEY_ORDER]


def _generate_steps_code(steps, order):
    return (
        CODEGEN_STEPS + pformat(steps, width=PFORMAT_WIDE) + "\n\n"
        + CODEGEN_BUILD_ORDER + repr(order)
    )


def _load_agents():
    d = {}
    agents_dir = os.path.join(_DATA_DIR, AGENTS_DIR_NAME)
    for fname in sorted(os.listdir(agents_dir)):
        if fname.endswith(MARKDOWN_EXTENSION):
            with open(os.path.join(agents_dir, fname), encoding=FILE_ENCODING) as fh:
                d[fname[:-len(MARKDOWN_EXTENSION)]] = fh.read()
    return d


def _load_gates():
    d = {}
    gates_dir = os.path.join(_DATA_DIR, GATES_DIR_NAME)
    for fname in sorted(os.listdir(gates_dir)):
        if fname.endswith(MARKDOWN_EXTENSION):
            with open(os.path.join(gates_dir, fname), encoding=FILE_ENCODING) as fh:
                d[fname[:-len(MARKDOWN_EXTENSION)]] = fh.read()
    return d


def _load_stages():
    with open(os.path.join(_DATA_DIR, STAGES_DATA_FILE), encoding=FILE_ENCODING) as fh:
        return _json.load(fh)


def _load_stage_pipeline():
    with open(os.path.join(_DATA_DIR, STAGE_PIPELINE_DATA_FILE), encoding=FILE_ENCODING) as fh:
        return _json.load(fh)


STEPS, BUILD_ORDER = _load_build_steps()
_CODE_AGENT_KEYS = {v[JSON_KEY_AGENT] for v in STEPS.values()}
_all_agents = _load_agents()
CODE_AGENTS = {k: v for k, v in _all_agents.items() if k in _CODE_AGENT_KEYS}
AGENTS = {k: v for k, v in _all_agents.items() if k not in _CODE_AGENT_KEYS}
GATES = _load_gates()
STAGE_OUTPUT_FILES = _load_stages()
STAGE_PIPELINE = _load_stage_pipeline()

STAGE_MULTI_OUTPUTS = f"{CODEGEN_STAGE_MULTI_OUTPUTS}{pformat(STAGE_OUTPUT_FILES, width=PFORMAT_NORMAL)}"
FILES_TO_TOUCH = pformat(
    [file_path for output_files in STAGE_OUTPUT_FILES.values() for file_path in output_files],
    width=PFORMAT_NORMAL,
)


def _assemble_dashboard_html():
    """Auto-assemble src/dashboard.html from src/dashboard/* before embedding."""
    import re as _re
    base = os.path.join(os.path.dirname(__file__), DASHBOARD_DIR_NAME)
    assembled_path = os.path.join(os.path.dirname(__file__), DASHBOARD_OUTPUT_FILE)
    # Only assemble if the component source files exist
    index_path = os.path.join(base, DASHBOARD_INDEX_FILE)
    css_path = os.path.join(base, DASHBOARD_STYLES_FILE)
    if not os.path.exists(index_path):
        return open(assembled_path, encoding=FILE_ENCODING).read()
    html = open(index_path, encoding=FILE_ENCODING).read()
    if os.path.exists(css_path):
        css = open(css_path, encoding=FILE_ENCODING).read()
        html = html.replace(DASHBOARD_CSS_MARKER, css)
    scripts_dir = os.path.join(base, SCRIPTS_DIR_NAME)
    for match in _re.findall(DASHBOARD_SCRIPT_PATTERN, html):
        js_path = os.path.join(scripts_dir, match)
        if os.path.exists(js_path):
            js = open(js_path, encoding=FILE_ENCODING).read()
            html = html.replace(DASHBOARD_SCRIPT_MARKER_TEMPLATE.format(name=match), js)
    # Write assembled output so it's available as a build artifact too
    open(assembled_path, "w", encoding=FILE_ENCODING).write(html)
    return html


DASHBOARD_HTML_CONTENT = _assemble_dashboard_html()

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, RUNTIME_DIR_NAME, RUNTIME_CONSTANTS_FILE), 'r', encoding=FILE_ENCODING) as _f:
    CONSTANTS_PY_CONTENT = _f.read()

with open(os.path.join(_HERE, RUNTIME_DIR_NAME, RUNTIME_SERVER_FILE), 'r', encoding=FILE_ENCODING) as _f:
    SERVER_PY_CONTENT = _f.read()
SERVER_PY_CONTENT = SERVER_PY_CONTENT.replace(
    PLACEHOLDER_KNOWN_TOOLS,
    _generate_known_tools_code(KNOWN_TOOLS)
)

with open(os.path.join(_HERE, RUNTIME_DIR_NAME, RUNTIME_BUILD_RUNNER_FILE), 'r', encoding=FILE_ENCODING) as _f:
    BUILD_RUNNER_PY_CONTENT = _f.read()
BUILD_RUNNER_PY_CONTENT = BUILD_RUNNER_PY_CONTENT.replace(
    PLACEHOLDER_BUILD_STEPS,
    _generate_steps_code(STEPS, BUILD_ORDER)
)


def _stage_agent_code():
    return CODEGEN_STAGE_AGENT + pformat(STAGE_PIPELINE[JSON_KEY_STAGE_AGENT], width=PFORMAT_NORMAL, sort_dicts=False)


def _stage_gate_code():
    return CODEGEN_STAGE_GATE + pformat(STAGE_PIPELINE[JSON_KEY_STAGE_GATE], width=PFORMAT_NORMAL, sort_dicts=False)


def _stage_inputs_code():
    return CODEGEN_STAGE_INPUTS + pformat(STAGE_PIPELINE[JSON_KEY_STAGE_INPUTS], width=PFORMAT_NORMAL, sort_dicts=False)


def _pipeline_stages_code():
    stages = list(STAGE_OUTPUT_FILES.keys())
    return CODEGEN_PIPELINE_STAGES + repr(stages)


def _directories_code():
    lines = [CODEGEN_DIRECTORIES_OPEN]
    for d in STAGE_PIPELINE[JSON_KEY_DIRECTORIES]:
        lines.append(f"        {repr(d)},")
    lines.append(CODEGEN_DIRECTORIES_CLOSE)
    return "\n".join(lines)


def _agents_list_code():
    all_agents = {**AGENTS, **CODE_AGENTS}
    lines = [CODEGEN_AGENTS_OPEN]
    for a in all_agents:
        lines.append(f"        {repr(a)},")
    lines.append(CODEGEN_AGENTS_CLOSE)
    return "\n".join(lines)


def _gates_list_code():
    lines = [CODEGEN_GATES_OPEN]
    for g in GATES:
        lines.append(f"        {repr(g)},")
    lines.append(CODEGEN_GATES_CLOSE)
    return "\n".join(lines)


with open(os.path.join(_HERE, RUNTIME_DIR_NAME, RUNTIME_CLI_TEMPLATE_FILE), 'r', encoding=FILE_ENCODING) as _f:
    TEMPLATE = _f.read()


def _agent_content_code():
    all_agents = {**AGENTS, **CODE_AGENTS}
    lines = [CODEGEN_AGENT_CONTENT_OPEN]
    for agent, text in all_agents.items():
        lines.append(f"    {repr(agent)}: {repr(text)},")
    lines.append(CODEGEN_AGENT_CONTENT_CLOSE)
    return "\n".join(lines)


def _gate_content_code():
    lines = [CODEGEN_GATE_CONTENT_OPEN]
    for gate, text in GATES.items():
        lines.append(f"    {repr(gate)}: {repr(text)},")
    lines.append(CODEGEN_GATE_CONTENT_CLOSE)
    return "\n".join(lines)


def _render_template():
    forge_content = TEMPLATE.format(
        STAGE_MULTI_OUTPUTS=STAGE_MULTI_OUTPUTS,
        FILES_TO_TOUCH=FILES_TO_TOUCH,
        AGENT_CONTENT_CODE=_agent_content_code(),
        GATE_CONTENT_CODE=_gate_content_code(),
        DASHBOARD_HTML_CONTENT=_json.dumps(DASHBOARD_HTML_CONTENT),
        FORGE_VERSION=FORGE_VERSION,
        BUILD_RUNNER_PY_CONTENT=_json.dumps(BUILD_RUNNER_PY_CONTENT),
        ALLOWED_MODELS_CODE=_generate_allowed_models_code(KNOWN_TOOLS),
        CONSTANTS_PY_CONTENT=CONSTANTS_PY_CONTENT,
        CONSTANTS_PY_STRING_LITERAL=_json.dumps(CONSTANTS_PY_CONTENT),
        STAGE_AGENT_CODE=_stage_agent_code(),
        STAGE_GATE_CODE=_stage_gate_code(),
        STAGE_INPUTS_CODE=_stage_inputs_code(),
        PIPELINE_STAGES_CODE=_pipeline_stages_code(),
        DIRECTORIES_CODE=_directories_code(),
        AGENTS_LIST_CODE=_agents_list_code(),
        GATES_LIST_CODE=_gates_list_code(),
    )

    with open(os.path.join(_DATA_DIR, PROMPTS_DIR_NAME, AGENT_PROMPT_FILE), encoding=FILE_ENCODING) as f:
        agent_prompt = f.read()

    with open(os.path.join(_DATA_DIR, PROMPTS_DIR_NAME, DISTILL_PROMPT_FILE), encoding=FILE_ENCODING) as f:
        distill_prompt = f.read()

    return forge_content.replace(
        PLACEHOLDER_SERVER_PY, _json.dumps(SERVER_PY_CONTENT)
    ).replace(
        PLACEHOLDER_AGENT_PROMPT, _json.dumps(agent_prompt)
    ).replace(
        PLACEHOLDER_DISTILL_PROMPT, _json.dumps(distill_prompt)
    )


def _hot_deploy_runtime():
    import glob, shutil
    src_dir = os.path.dirname(__file__)
    dashboard_src = os.path.join(src_dir, DASHBOARD_OUTPUT_FILE)
    constants_src = os.path.join(src_dir, RUNTIME_DIR_NAME, RUNTIME_CONSTANTS_FILE)
    repo_root = os.path.normpath(os.path.join(src_dir, ".."))
    parent_dir = os.path.dirname(repo_root)
    home_forge_scripts = os.path.join(
        os.path.expanduser("~"), HOT_DEPLOY_HOME_DIR, SCRIPTS_DIR_NAME
    )
    scripts_dirs = []
    for glob_pattern in HOT_DEPLOY_GLOBS:
        scripts_dirs.extend(glob.glob(os.path.join(repo_root, glob_pattern)))
    scripts_dirs.extend(glob.glob(os.path.join(parent_dir, HOT_DEPLOY_SIBLING_GLOB)))
    if os.path.isdir(home_forge_scripts):
        scripts_dirs.append(home_forge_scripts)

    copied = 0
    for sd in scripts_dirs:
        sd = os.path.normpath(sd)
        if not os.path.isdir(sd):
            continue
        try:
            # dashboard.html — copy file directly
            shutil.copy2(dashboard_src, os.path.join(sd, HOT_DEPLOY_FILES[0]))
            # server.py — write the injected content (KNOWN_TOOLS populated), not the raw source
            with open(os.path.join(sd, HOT_DEPLOY_FILES[1]), "w", encoding=FILE_ENCODING) as _sf:
                _sf.write(SERVER_PY_CONTENT)
            # constants.py — copy file directly
            shutil.copy2(constants_src, os.path.join(sd, HOT_DEPLOY_FILES[2]))
            copied += 1
        except Exception:
            pass
    if copied:
        message = LOG_HOT_DEPLOY_SINGULAR if copied == 1 else LOG_HOT_DEPLOY_PLURAL
        print(message.format(count=copied))


def build_forge():
    forge_content = _render_template()
    with open(BUILD_OUTPUT_FILE, "w", encoding=FILE_ENCODING) as f:
        f.write(forge_content)
    _hot_deploy_runtime()
    print(LOG_BUILD_SUCCESS)


if __name__ == "__main__":
    build_forge()
