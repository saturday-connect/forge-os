import os
import json as _json
from pprint import pformat

FORGE_VERSION = "0.3.4"

PFORMAT_WIDE   = 120
PFORMAT_NORMAL = 100

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def _load_tools():
    with open(os.path.join(_DATA_DIR, "tools.json"), encoding="utf-8") as fh:
        return _json.load(fh)

KNOWN_TOOLS = _load_tools()

def _generate_known_tools_code(tools):
    return "KNOWN_TOOLS = " + pformat(tools, width=PFORMAT_WIDE)

def _generate_allowed_models_code(tools):
    allowed = {k: {m["id"] for m in v["models"]} for k, v in tools.items()}
    lines = ["_ALLOWED_MODELS = {"]
    for tool, models in allowed.items():
        model_list = ", ".join(f'"{m}"' for m in sorted(models))
        lines.append(f'    "{tool}": {{{model_list}}},')
    lines.append("}")
    return "\n".join(lines)

def _load_build_steps():
    with open(os.path.join(_DATA_DIR, "build_steps.json"), encoding="utf-8") as fh:
        data = _json.load(fh)
    return data["steps"], data["order"]

def _generate_steps_code(steps, order):
    return (
        "STEPS = " + pformat(steps, width=PFORMAT_WIDE) + "\n\n"
        "BUILD_ORDER = " + repr(order)
    )

def _load_agents():
    d = {}
    agents_dir = os.path.join(_DATA_DIR, "agents")
    for fname in sorted(os.listdir(agents_dir)):
        if fname.endswith(".md"):
            with open(os.path.join(agents_dir, fname), encoding="utf-8") as fh:
                d[fname[:-3]] = fh.read()
    return d

def _load_gates():
    d = {}
    gates_dir = os.path.join(_DATA_DIR, "gates")
    for fname in sorted(os.listdir(gates_dir)):
        if fname.endswith(".md"):
            with open(os.path.join(gates_dir, fname), encoding="utf-8") as fh:
                d[fname[:-3]] = fh.read()
    return d

def _load_stages():
    with open(os.path.join(_DATA_DIR, "stages.json"), encoding="utf-8") as fh:
        return _json.load(fh)

def _load_stage_pipeline():
    with open(os.path.join(_DATA_DIR, "stage_pipeline.json"), encoding="utf-8") as fh:
        return _json.load(fh)

STEPS, BUILD_ORDER = _load_build_steps()
_CODE_AGENT_KEYS = {v["agent"] for v in STEPS.values()}
_all_agents = _load_agents()
CODE_AGENTS = {k: v for k, v in _all_agents.items() if k in _CODE_AGENT_KEYS}
AGENTS = {k: v for k, v in _all_agents.items() if k not in _CODE_AGENT_KEYS}
GATES = _load_gates()
STAGE_OUTPUT_FILES = _load_stages()
STAGE_PIPELINE = _load_stage_pipeline()

STAGE_MULTI_OUTPUTS = f"STAGE_MULTI_OUTPUTS = {pformat(STAGE_OUTPUT_FILES, width=PFORMAT_NORMAL)}"
FILES_TO_TOUCH = pformat(
    [file_path for output_files in STAGE_OUTPUT_FILES.values() for file_path in output_files],
    width=PFORMAT_NORMAL,
)

def _assemble_dashboard_html():
    """Auto-assemble src/dashboard.html from src/dashboard/* before embedding."""
    import re as _re
    base = os.path.join(os.path.dirname(__file__), "dashboard")
    assembled_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    # Only assemble if the component source files exist
    index_path = os.path.join(base, "index.html")
    css_path = os.path.join(base, "styles.css")
    if not os.path.exists(index_path):
        return open(assembled_path, encoding='utf-8').read()
    html = open(index_path, encoding='utf-8').read()
    if os.path.exists(css_path):
        css = open(css_path, encoding='utf-8').read()
        html = html.replace("<!-- FORGE_DASHBOARD_CSS -->", css)
    scripts_dir = os.path.join(base, "scripts")
    for match in _re.findall(r'<!-- FORGE_DASHBOARD_SCRIPT:([\w\-\.]+) -->', html):
        js_path = os.path.join(scripts_dir, match)
        if os.path.exists(js_path):
            js = open(js_path, encoding='utf-8').read()
            html = html.replace(f"<!-- FORGE_DASHBOARD_SCRIPT:{match} -->", js)
    # Write assembled output so it's available as a build artifact too
    open(assembled_path, "w", encoding='utf-8').write(html)
    return html

DASHBOARD_HTML_CONTENT = _assemble_dashboard_html()

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, 'runtime', 'constants.py'), 'r', encoding='utf-8') as _f:
    CONSTANTS_PY_CONTENT = _f.read()

with open(os.path.join(_HERE, 'runtime', 'server.py'), 'r', encoding='utf-8') as _f:
    SERVER_PY_CONTENT = _f.read()
SERVER_PY_CONTENT = SERVER_PY_CONTENT.replace(
    "KNOWN_TOOLS = {}  # __FORGE_KNOWN_TOOLS__",
    _generate_known_tools_code(KNOWN_TOOLS)
)

with open(os.path.join(_HERE, 'runtime', 'build_runner.py'), 'r', encoding='utf-8') as _f:
    BUILD_RUNNER_PY_CONTENT = _f.read()
BUILD_RUNNER_PY_CONTENT = BUILD_RUNNER_PY_CONTENT.replace(
    "STEPS = {}  # __FORGE_BUILD_STEPS__",
    _generate_steps_code(STEPS, BUILD_ORDER)
)

def _stage_agent_code():
    return "STAGE_AGENT = " + pformat(STAGE_PIPELINE["stage_agent"], width=PFORMAT_NORMAL, sort_dicts=False)

def _stage_gate_code():
    return "STAGE_GATE = " + pformat(STAGE_PIPELINE["stage_gate"], width=PFORMAT_NORMAL, sort_dicts=False)

def _stage_inputs_code():
    return "STAGE_INPUTS = " + pformat(STAGE_PIPELINE["stage_inputs"], width=PFORMAT_NORMAL, sort_dicts=False)

def _pipeline_stages_code():
    stages = list(STAGE_OUTPUT_FILES.keys())
    return "PIPELINE_STAGES = " + repr(stages)

def _directories_code():
    lines = ["    directories = ["]
    for d in STAGE_PIPELINE["directories"]:
        lines.append(f"        {repr(d)},")
    lines.append("    ]")
    return "\n".join(lines)

def _agents_list_code():
    all_agents = {**AGENTS, **CODE_AGENTS}
    lines = ["    agents = ["]
    for a in all_agents:
        lines.append(f"        {repr(a)},")
    lines.append("    ]")
    return "\n".join(lines)

def _gates_list_code():
    lines = ["    gates = ["]
    for g in GATES:
        lines.append(f"        {repr(g)},")
    lines.append("    ]")
    return "\n".join(lines)

with open(os.path.join(_HERE, 'runtime', 'forge_cli.py.tmpl'), 'r', encoding='utf-8') as _f:
    TEMPLATE = _f.read()

def _agent_content_code():
    all_agents = {**AGENTS, **CODE_AGENTS}
    lines = ["AGENT_CONTENT = {"]
    for agent, text in all_agents.items():
        lines.append(f"    {repr(agent)}: {repr(text)},")
    lines.append("}")
    return "\n".join(lines)

def _gate_content_code():
    lines = ["GATE_CONTENT = {"]
    for gate, text in GATES.items():
        lines.append(f"    {repr(gate)}: {repr(text)},")
    lines.append("}")
    return "\n".join(lines)

def _render_template():
    forge_content = TEMPLATE.format(
        STAGE_MULTI_OUTPUTS=STAGE_MULTI_OUTPUTS,
        FILES_TO_TOUCH=FILES_TO_TOUCH,
        AGENT_CONTENT_CODE=_agent_content_code(),
        GATE_CONTENT_CODE=_gate_content_code(),
        DASHBOARD_HTML_CONTENT=DASHBOARD_HTML_CONTENT,
        FORGE_VERSION=FORGE_VERSION,
        BUILD_RUNNER_PY_CONTENT=BUILD_RUNNER_PY_CONTENT,
        ALLOWED_MODELS_CODE=_generate_allowed_models_code(KNOWN_TOOLS),
        CONSTANTS_PY_CONTENT=CONSTANTS_PY_CONTENT,
        STAGE_AGENT_CODE=_stage_agent_code(),
        STAGE_GATE_CODE=_stage_gate_code(),
        STAGE_INPUTS_CODE=_stage_inputs_code(),
        PIPELINE_STAGES_CODE=_pipeline_stages_code(),
        DIRECTORIES_CODE=_directories_code(),
        AGENTS_LIST_CODE=_agents_list_code(),
        GATES_LIST_CODE=_gates_list_code(),
    )
    return forge_content.replace("__FORGE_SERVER_PY__", SERVER_PY_CONTENT)

def _hot_deploy_runtime():
    import glob, shutil
    src_dir = os.path.dirname(__file__)
    dashboard_src = os.path.join(src_dir, "dashboard.html")
    server_src = os.path.join(src_dir, "runtime", "server.py")
    constants_src = os.path.join(src_dir, "runtime", "constants.py")
    repo_root = os.path.normpath(os.path.join(src_dir, ".."))
    parent_dir = os.path.dirname(repo_root)
    home_forge_scripts = os.path.join(os.path.expanduser("~"), ".forge", "scripts")
    scripts_dirs = (
        glob.glob(os.path.join(repo_root, ".forge/scripts"))
        + glob.glob(os.path.join(repo_root, ".projects/*/.forge/scripts"))
        + glob.glob(os.path.join(repo_root, "test-projects/*/.forge/scripts"))
        + glob.glob(os.path.join(parent_dir, "*/.forge/scripts"))
        + ([home_forge_scripts] if os.path.isdir(home_forge_scripts) else [])
    )
    copied = 0
    for sd in scripts_dirs:
        sd = os.path.normpath(sd)
        if not os.path.isdir(sd):
            continue
        try:
            shutil.copy2(dashboard_src, os.path.join(sd, "dashboard.html"))
            shutil.copy2(server_src, os.path.join(sd, "server.py"))
            shutil.copy2(constants_src, os.path.join(sd, "constants.py"))
            copied += 1
        except Exception:
            pass
    if copied:
        print(f"Dashboard + server hot-deployed to {copied} runtime director{'y' if copied==1 else 'ies'}.")

def build_forge():
    forge_content = _render_template()
    with open("forge", "w", encoding='utf-8') as f:
        f.write(forge_content)
    _hot_deploy_runtime()
    print("forge built successfully.")

if __name__ == "__main__":
    build_forge()
