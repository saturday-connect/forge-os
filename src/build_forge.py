import os
import json as _json
from pprint import pformat

FORGE_VERSION = "0.3.4"

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def _load_tools():
    with open(os.path.join(_DATA_DIR, "tools.json"), encoding="utf-8") as fh:
        return _json.load(fh)

KNOWN_TOOLS = _load_tools()

def _generate_known_tools_code(tools):
    return "KNOWN_TOOLS = " + pformat(tools, width=120)

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

STEPS, BUILD_ORDER = _load_build_steps()

def _generate_steps_code(steps, order):
    return (
        "STEPS = " + pformat(steps, width=120) + "\n\n"
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

_CODE_AGENT_KEYS = {"code-architect", "frontend-coder", "integration-engineer", "qa-coder", "devops-coder"}
_all_agents = _load_agents()
CODE_AGENTS = {k: v for k, v in _all_agents.items() if k in _CODE_AGENT_KEYS}
AGENTS = {k: v for k, v in _all_agents.items() if k not in _CODE_AGENT_KEYS}
GATES = _load_gates()
STAGE_OUTPUT_FILES = _load_stages()

STAGE_MULTI_OUTPUTS = f"STAGE_MULTI_OUTPUTS = {pformat(STAGE_OUTPUT_FILES, width=100)}"
FILES_TO_TOUCH = pformat(
    [file_path for output_files in STAGE_OUTPUT_FILES.values() for file_path in output_files],
    width=100,
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

TEMPLATE = '''#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from datetime import datetime

# -------------------------------------------------------------------------
# Shared Constants
# -------------------------------------------------------------------------
{CONSTANTS_PY_CONTENT}

FORGE_VERSION = "{FORGE_VERSION}"

# -------------------------------------------------------------------------
# Path Resolution
# -------------------------------------------------------------------------

def _resolve_data_dir(project_root=None):
    """Return (forge_data_dir, project_root) by reading the .forge dotfile.

    Falls back to <project_root>/.forge if no dotfile exists (pre-init or legacy dir).
    """
    if project_root is None:
        project_root = os.path.abspath(os.environ.get("FORGE_REPO_ROOT", "."))
    dotfile = os.path.join(project_root, ".forge")
    if os.path.isfile(dotfile):
        try:
            meta = json.loads(open(dotfile, "r", encoding="utf-8").read())
            return os.path.expanduser(meta["data_dir"]), project_root
        except Exception:
            pass
    if os.path.isdir(dotfile):
        # Legacy fallback: .forge/ directory still present
        return dotfile, project_root
    # Pre-init: no dotfile yet
    return os.path.join(project_root, ".forge"), project_root

# -------------------------------------------------------------------------
# Embedded Scripts for Initialization
# -------------------------------------------------------------------------

STAGE_RUNNER_PY = r"""import sys
import os
import subprocess
import json

{STAGE_MULTI_OUTPUTS}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/stage_runner.py <stage> [raw_input]")
        sys.exit(1)

    stage = sys.argv[1]
    raw_input = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"[STAGE-RUNNER] Stage: {{stage}}")

    if stage in STAGE_MULTI_OUTPUTS:
        outputs = STAGE_MULTI_OUTPUTS[stage]
        skip_existing = os.environ.get("FORGE_SKIP_EXISTING") == "1"
        if skip_existing:
            pending = [f for f in outputs if not (os.path.exists(f) and os.path.getsize(f) > 0)]
            skipped = len(outputs) - len(pending)
            if skipped:
                print(f"[STAGE-RUNNER] Skipping {{skipped}} already-generated file(s)")
        else:
            pending = outputs
        print(f"[STAGE-RUNNER] Documents to generate: {{len(pending)}}")

        success_count = 0
        failed_count = 0
        last_err = None

        total_files = len(pending)
        status_file = os.path.join("runs", "status.json")
        run_error_file = os.path.join("runs", "last-run-error.json")

        for file_idx, output_file in enumerate(pending):
            print(f"[STAGE-RUNNER] Generating: {{output_file}} ({{file_idx+1}}/{{total_files}})")

            if os.path.exists("runs"):
                with open(status_file, "w", encoding='utf-8') as sf:
                    json.dump({{
                        "status": "running",
                        "stage": stage,
                        "file": output_file,
                        "file_index": file_idx + 1,
                        "file_total": total_files,
                        "updated_at": __import__("datetime").datetime.now().isoformat()
                    }}, sf)

            # Clear any prior error file before each run
            if os.path.exists(run_error_file):
                try: os.remove(run_error_file)
                except Exception: pass

            cmd = [sys.executable, "scripts/run.py", stage, "--output", output_file]
            if raw_input:
                cmd.extend(["--raw-input", raw_input])

            result = subprocess.run(cmd)

            if result.returncode == 0:
                success_count += 1
                try:
                    reviews_path = "reviews.json"
                    if os.path.exists(reviews_path):
                        with open(reviews_path, encoding='utf-8') as rf:
                            _reviews = json.load(rf)
                    else:
                        _reviews = {{}}
                    _reviews.pop(output_file, None)
                    with open(reviews_path, "w", encoding='utf-8') as rf:
                        json.dump(_reviews, rf, indent=2)
                except Exception:
                    pass
            else:
                failed_count += 1
                print(f"[ERROR] Failed to generate: {{output_file}}")
                # Read friendly message written by run.py
                err_msg = "Generation failed — the AI model may have reached its usage limit. Try again in a few minutes."
                if os.path.exists(run_error_file):
                    try:
                        with open(run_error_file, encoding='utf-8') as ef:
                            err_msg = json.load(ef).get("message", err_msg)
                    except Exception:
                        pass
                last_err = {{
                    "stage": stage,
                    "file": output_file,
                    "message": err_msg,
                    "timestamp": __import__("datetime").datetime.now().isoformat()
                }}

        print(f"[STAGE-RUNNER] Stage complete. Success: {{success_count}}, Failed: {{failed_count}}")
        if os.path.exists("runs"):
            idle_data = {{
                "status": "idle",
                "stage": stage,
                "updated_at": __import__("datetime").datetime.now().isoformat()
            }}
            if last_err:
                idle_data["last_error"] = last_err
            with open(status_file, "w", encoding='utf-8') as sf:
                json.dump(idle_data, sf)
        if failed_count > 0:
            sys.exit(1)
    else:
        print(f"[STAGE-RUNNER] Standard execution for stage: {{stage}}")
        cmd = [sys.executable, "scripts/run.py", stage]
        if raw_input:
            cmd.extend(["--raw-input", raw_input])
            
        result = subprocess.run(cmd)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
"""

RUN_PY = r"""import argparse
import os
import sys
import subprocess
import tempfile
import json
import urllib.request
import urllib.error
import shutil
from datetime import datetime, timezone

# Configuration
REPO_ROOT = os.environ.get("FORGE_REPO_ROOT", ".")
LOG_LEVEL = os.environ.get("FORGE_LOG_LEVEL", "info")
os.environ["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
_forge_data = os.environ.get("FORGE_DATA_DIR")
FORGE_DIR = os.path.expanduser(_forge_data) if _forge_data else os.path.join(REPO_ROOT, ".forge")
AGENTS_DIR = os.path.join(FORGE_DIR, "11-agents")
VERSIONS_DIR = os.path.join(FORGE_DIR, "versions")
GATES_DIR = os.path.join(FORGE_DIR, "12-gates")
RUNS_LOG = os.path.join(FORGE_DIR, "runs/run-log.md")

FORGE_ORG = os.environ.get("FORGE_ORG", "")
ORG_CACHE_DIR = os.path.expanduser(f"~/.forge/org-cache/{{FORGE_ORG}}") if FORGE_ORG else ""

def _list_org_context_files():
    if not ORG_CACHE_DIR or not os.path.isdir(ORG_CACHE_DIR):
        return [], [], []
    def _md_files(subdir):
        d = os.path.join(ORG_CACHE_DIR, subdir)
        if not os.path.isdir(d):
            return []
        return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md"))
    return _md_files("knowledge"), _md_files("patterns"), _md_files("agents")

STAGE_AGENT = {{
    "context": "product-strategist",
    "requirements": "product-manager",
    "design": "product-designer",
    "analysis": "business-analyst",
    "architecture": "architect",
    "delivery": "product-manager",
    "engineering": "backend-engineer",
    "qa": "qa-engineer",
    "operations": "devops-engineer",
    "release": "release-manager",
    "marketing": "marketing-strategist"
}}

STAGE_GATE = {{
    "context": "",
    "requirements": "context-gate",
    "design": "prd-gate",
    "analysis": "prd-gate",
    "architecture": "design-gate",
    "delivery": "architecture-gate",
    "engineering": "architecture-gate",
    "qa": "engineering-gate",
    "operations": "qa-gate",
    "release": "release-gate",
    "marketing": "release-gate"
}}

STAGE_INPUTS = {{
    "context": [],
    "requirements": ["00-context"],
    "design": ["00-context", "01-requirements"],
    "analysis": ["01-requirements"],
    "architecture": ["01-requirements", "02-design", "03-analysis"],
    "delivery": ["01-requirements", "04-architecture"],
    "engineering": ["04-architecture", "02-design"],
    "qa": ["01-requirements", "06-engineering"],
    "operations": ["04-architecture", "06-engineering"],
    "release": ["05-delivery", "07-quality"],
    "marketing": ["00-context", "05-delivery"]
}}

class RunState:
    def __init__(self):
        self.stage = ""
        self.agent = ""
        self.gate = ""
        self.model = ""
        self.run_id = "RUN-001"
        self.timestamp = ""

state = RunState()

def log_error(msg):
    print(f"[ERROR] {{msg}}")

def log_info(msg):
    print(f"[Forge] {{msg}}")

def parse_args():
    parser = argparse.ArgumentParser(description="Forge Pipeline Runner")
    parser.add_argument("stage", help="Stage name (e.g., context, requirements)")
    parser.add_argument("--model", default=os.environ.get("AI_MODEL", "gemini"), help="AI model to use")
    parser.add_argument("--output", help="Specific output file for multi-output stages")
    parser.add_argument("--raw-input", help="Raw input file for context stage")
    parser.add_argument("--critique", help="User critique or feedback to fix the file")
    parser.add_argument("--distill-stage", dest="distill_stage", help="Source stage for distillation mode")
    parser.add_argument("--distill-output", dest="distill_output", help="Output file path for distilled patterns")
    parser.add_argument("--distill-sources", dest="distill_sources", help="Comma-separated source files for distillation")
    return parser.parse_args()

def validate_environment(stage):
    state.stage = stage
    if stage not in STAGE_AGENT:
        log_error(f"Unknown stage: {{stage}}")
        sys.exit(1)
        
    state.agent = STAGE_AGENT[stage]
    state.gate = STAGE_GATE.get(stage, "")

def check_gate():
    if not state.gate:
        return
        
    gate_path = os.path.join(GATES_DIR, f"{{state.gate}}.md")
    if not os.path.exists(gate_path):
        log_error(f"Gate file not found: {{gate_path}}")
        sys.exit(1)
        
    with open(gate_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "PASSED" not in content and "APPROVED" not in content:
            log_error(f"Gate {{state.gate}} is not PASSED/APPROVED. Cannot proceed.")
            sys.exit(1)
    log_info(f"Gate {{state.gate}} PASSED.")

def resolve_inputs(stage, raw_input):
    inputs = []
    
    if stage == "context":
        if raw_input:
            if os.path.exists(raw_input):
                inputs.append(os.path.abspath(raw_input))
            else:
                log_error(f"Raw input file not found: {{raw_input}}")
                sys.exit(1)
        elif os.path.exists("../raw-input.md"):
            inputs.append(os.path.abspath("../raw-input.md"))
        else:
            log_error("No raw input file provided for context stage.")
            sys.exit(1)
        return inputs
        
    dirs = STAGE_INPUTS.get(stage, [])
    for d in dirs:
        dir_path = os.path.join(REPO_ROOT, d)
        if os.path.isdir(dir_path):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".md"):
                        inputs.append(os.path.join(root, file))
    return inputs

def build_prompt(agent_path, inputs, output_file, critique=None):
    prompt_parts = []
    
    prompt_parts.append(f"You are an AI generating content for the file: {{output_file}}\\n")
    if critique:
        prompt_parts.append(f"CRITICAL MISSION: The user has reviewed the previous version of this file and provided the following critique/feedback:\\n")
        prompt_parts.append(f"\\\"{{critique}}\\\"\\n")
        prompt_parts.append(f"You MUST completely rewrite the file incorporating this feedback.\\n\\n")
    prompt_parts.append("CRITICAL SYSTEM INSTRUCTION: DO NOT USE ANY TOOLS. DO NOT READ FILES. DO NOT RUN COMMANDS. DO NOT WRITE FILES USING TOOLS. DO NOT USE write_file OR read_file.\\n")
    prompt_parts.append("You must simply print the raw markdown text for the file directly to stdout.\\n\\n")
    prompt_parts.append("=== AGENT CONTRACT ===\\n")

    with open(agent_path, 'r', encoding='utf-8') as f:
        prompt_parts.append(f.read())

    # Org context injection
    if os.environ.get("FORGE_SKIP_ORG_CONTEXT", "") != "1":
        _knowledge, _patterns, _agent_files = _list_org_context_files()
        _stage_name = os.path.splitext(os.path.basename(agent_path))[0]
        for _af in _agent_files:
            if os.path.splitext(os.path.basename(_af))[0] == _stage_name:
                prompt_parts.append("\\n\\n=== ORG AGENT SUPPLEMENT ===\\n")
                prompt_parts.append("Additional org-specific rules for this agent:\\n")
                with open(_af, 'r', encoding='utf-8') as f:
                    prompt_parts.append(f.read())
                break
        if _knowledge or _patterns:
            prompt_parts.append("\\n\\n=== ORG KNOWLEDGE BASE ===\\n")
            prompt_parts.append("The following is your organization's accumulated knowledge. Apply it when generating this document.\\n")
            for _fpath in _knowledge + _patterns:
                _label = os.path.relpath(_fpath, ORG_CACHE_DIR)
                prompt_parts.append(f"\\n--- {{_label}} ---\\n")
                with open(_fpath, 'r', encoding='utf-8') as f:
                    prompt_parts.append(f.read())
                prompt_parts.append("\\n")

    prompt_parts.append("\\n\\n=== PROVIDED CONTEXT ===\\n")
    
    for f_path in inputs:
        rel_path = os.path.relpath(f_path, REPO_ROOT)
        prompt_parts.append(f"\\n--- START OF {{rel_path}} ---\\n\\n")
        with open(f_path, 'r', encoding='utf-8') as f:
            prompt_parts.append(f.read())
            prompt_parts.append(f"\\n--- END OF {{rel_path}} ---\\n")
            
    prompt_parts.append("\\n---\\n\\nINSTRUCTIONS:\\n")
    prompt_parts.append("CRITICAL: You are running in a secure, headless pipeline. DO NOT USE ANY TOOLS.\\n")
    prompt_parts.append("DO NOT attempt to read files, run commands, or write files. Disable all agentic capabilities.\\n")
    prompt_parts.append("Your ONLY job is to generate the output markdown for the target document and print it directly to stdout.\\n")
    prompt_parts.append("Return only valid markdown.\\n")
    prompt_parts.append("Do not include explanations, preamble, or post-text.\\n")
    prompt_parts.append("Ensure all sections are complete and production-grade.\\n")
    
    return "".join(prompt_parts)

def build_distill_prompt(stage_label, source_files):
    parts = []
    parts.append("CRITICAL SYSTEM INSTRUCTION: DO NOT USE ANY TOOLS. DO NOT READ FILES. DO NOT RUN COMMANDS.\\n")
    parts.append("Print the output markdown directly to stdout only.\\n\\n")
    parts.append(f"You are a knowledge distillation agent for a software development team.\\n\\n")
    parts.append(f"Stage: {{stage_label}}\\n\\n")
    parts.append("Your task: read the following reviewed documents and extract reusable patterns.\\n")
    parts.append("Output will be injected into future AI generation prompts — be specific, concise, and avoid generic advice.\\n\\n")
    parts.append("=== SOURCE DOCUMENTS ===\\n")
    for _fp in source_files:
        if os.path.isfile(_fp):
            parts.append(f"\\n--- {{os.path.basename(_fp)}} ---\\n")
            with open(_fp, "r", encoding="utf-8") as _f:
                parts.append(_f.read())
    parts.append("\\n\\n=== DISTILLATION INSTRUCTIONS ===\\n")
    parts.append("Produce a structured markdown document with exactly these sections:\\n\\n")
    parts.append("## Key Decisions\\n")
    parts.append("Important product, architectural, or process decisions from these documents.\\n")
    parts.append("For each: what was decided, why, and any alternatives rejected.\\n\\n")
    parts.append("## Reusable Patterns\\n")
    parts.append("Patterns, templates, or approaches that should apply to future projects.\\n")
    parts.append("Use the team's actual terminology. Be concrete, not generic.\\n\\n")
    parts.append("## Constraints and Anti-Patterns\\n")
    parts.append("Constraints, limitations, or things to avoid specific to this team or domain.\\n\\n")
    parts.append("## Team Conventions\\n")
    parts.append("Naming conventions, structural patterns, or process standards present in these documents.\\n\\n")
    parts.append("Rules:\\n- Total output: under 600 words.\\n- Use the team's actual language.\\n- Omit sections with nothing specific to add.\\n- Return only markdown. No preamble.\\n")
    return "".join(parts)

def run_distill_mode(args):
    if not args.distill_stage or not args.distill_output:
        log_error("Distill mode requires --distill-stage and --distill-output")
        sys.exit(1)
    source_files = [s for s in (args.distill_sources or "").split(",") if s.strip()]
    if not source_files:
        log_error("No source files provided for distillation (--distill-sources)")
        sys.exit(1)

    state.tool = os.environ.get("FORGE_TOOL", state.model)
    state.model_id = os.environ.get("FORGE_MODEL", "")

    log_info(f"Distilling stage '{{args.distill_stage}}' from {{len(source_files)}} file(s)")
    prompt = build_distill_prompt(args.distill_stage, source_files)

    try:
        invoke_model(prompt, args.distill_output)
    except subprocess.CalledProcessError:
        log_error("AI tool returned an error during distillation.")
        sys.exit(1)
    except Exception as _e:
        log_error(f"Distillation failed: {{_e}}")
        sys.exit(1)

    log_info(f"Distilled patterns saved: {{args.distill_output}}")

{ALLOWED_MODELS_CODE}

def invoke_model(prompt, output_path):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
        tmp_path = tmp.name

    try:
        tool = getattr(state, "tool", state.model)
        model_id = getattr(state, "model_id", "")
        if model_id and tool in _ALLOWED_MODELS and model_id not in _ALLOWED_MODELS[tool]:
            log_error(f"Unsupported model '{{model_id}}' for tool '{{tool}}'. Aborting.")
            sys.exit(1)
        if tool == "gemini":
            cmd = ["gemini", "--skip-trust"]
            if model_id:
                cmd += ["-m", model_id]
            cmd += ["-p", prompt]
            subprocess.run(cmd, stdout=open(tmp_path, 'w', encoding='utf-8'), check=True)
        elif tool == "claude":
            subprocess.run(["claude"], input=prompt, text=True, stdout=open(tmp_path, 'w', encoding='utf-8'), check=True)
        elif tool == "codex":
            cmd = ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", "--ephemeral",
                   "-o", tmp_path]
            if model_id:
                cmd += ["-m", model_id]
            subprocess.run(cmd, input=prompt, text=True, check=True)
        elif tool == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                log_error("OPENAI_API_KEY environment variable is not set.")
                sys.exit(1)
            model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
            
            data = json.dumps({{
                "model": model_name,
                "messages": [{{"role": "user", "content": prompt}}]
            }}).encode('utf-8')
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=data,
                headers={{
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {{api_key}}"
                }}
            )
            try:
                with urllib.request.urlopen(req, encoding='utf-8') as response:
                    res_body = response.read().decode('utf-8')
                    res_json = json.loads(res_body)
                    content = res_json['choices'][0]['message']['content']
                    with open(tmp_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            except urllib.error.URLError as e:
                log_error(f"OpenAI API request failed: {{e}}")
                sys.exit(1)
        else:
            log_error(f"Unsupported tool: '{{tool}}'. Supported: gemini, claude, openai")
            sys.exit(1)
            
        with open(tmp_path, 'r', encoding='utf-8') as f:
            result_content = f.read()

        if not result_content.strip():
            log_error(f"Model returned empty output for: {{output_path}}")
            sys.exit(1)
            
        # Save existing content as a version before overwriting
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            try:
                rel = os.path.relpath(output_path, REPO_ROOT)          # e.g. 00-context/product-vision.md
                stem = os.path.splitext(rel)[0]
                ver_dir = os.path.join(VERSIONS_DIR, stem)
                os.makedirs(ver_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                shutil.copy2(output_path, os.path.join(ver_dir, f"{{ts}}.md"))
            except Exception as e:
                log_info(f"Version save skipped: {{e}}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result_content)

        log_info(f"Output written: {{output_path}}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def log_run():
    state.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    log_entry = f"| {{state.timestamp}} | {{state.run_id}} | {{state.stage}} | {{state.model}} | {{state.agent}} | SUCCESS |\\n"
    if os.path.exists(RUNS_LOG):
        with open(RUNS_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    log_info(f"Run logged: {{state.run_id}}")

def main():
    args = parse_args()
    state.model = args.model

    if args.stage == "distill":
        run_distill_mode(args)
        return

    log_info(f"Stage: {{args.stage}}")

    validate_environment(args.stage)
    check_gate()
    
    agent_path = os.path.join(AGENTS_DIR, f"{{state.agent}}.md")
    if not os.path.exists(agent_path):
        log_error(f"Agent contract not found: {{agent_path}}")
        sys.exit(1)
        
    log_info(f"Agent: {{agent_path}}")
    log_info(f"Model: {{state.model}}")
    
    inputs = resolve_inputs(args.stage, args.raw_input)
    log_info("Loading inputs...")
    for f in inputs:
        rel_f = os.path.relpath(f, REPO_ROOT)
        log_info(f"  -> {{rel_f}}")
        
    output_file = args.output
    if not output_file:
        output_file = f"01-requirements/prd.md" if args.stage == "requirements" else f"out-{{args.stage}}.md"
        
    output_path = os.path.join(REPO_ROOT, output_file)
    
    # FORGE_TOOL / FORGE_MODEL env vars (set by server) take precedence over --model arg
    state.tool = os.environ.get("FORGE_TOOL", state.model)
    state.model_id = os.environ.get("FORGE_MODEL", "")

    prompt = build_prompt(agent_path, inputs, output_file, args.critique)

    log_info(f"Invoking model: {{state.tool}} {{state.model_id or '(default)'}}")
    try:
        invoke_model(prompt, output_path)
    except subprocess.CalledProcessError as e:
        if e.returncode == 127:
            msg = "AI tool not found — make sure it is installed and available in your terminal."
        else:
            msg = "The AI model returned an error. It may have reached its usage limit — wait a minute and try again."
        log_error(msg)
        _write_run_error(output_file, msg)
        sys.exit(1)
    except Exception as e:
        msg = "An unexpected error occurred during generation."
        log_error(str(e))
        _write_run_error(output_file, msg)
        sys.exit(1)

    log_run()
    log_info("Stage complete.")

def _write_run_error(output_file, message):
    err_path = os.path.join(REPO_ROOT, "runs", "last-run-error.json")
    try:
        os.makedirs(os.path.dirname(err_path), exist_ok=True)
        with open(err_path, "w", encoding='utf-8') as f:
            json.dump({{
                "file": output_file,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }}, f)
    except Exception:
        pass

if __name__ == "__main__":
    main()
"""

VALIDATE_GATES_PY = r"""import sys
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_gates.py <gate-name>")
        sys.exit(1)

    gate = sys.argv[1]
    gate_file = f"12-gates/{{gate}}.md"

    if not os.path.exists(gate_file):
        print(f"Gate file not found: {{gate_file}}")
        sys.exit(1)

    with open(gate_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "PASSED" in content or "APPROVED" in content:
            print(f"Gate {{gate}} validation passed.")
            sys.exit(0)
        else:
            print(f"Gate {{gate}} validation failed. Human review required.")
            sys.exit(1)

if __name__ == "__main__":
    main()
"""

SERVER_PY = r\"\"\"__FORGE_SERVER_PY__\"\"\"

DASHBOARD_HTML = r\"\"\"{DASHBOARD_HTML_CONTENT}\"\"\"

BUILD_RUNNER_PY = r\"\"\"{BUILD_RUNNER_PY_CONTENT}\"\"\"

CONSTANTS_PY = r\"\"\"{CONSTANTS_PY_CONTENT}\"\"\"

# -------------------------------------------------------------------------
# Commands
# -------------------------------------------------------------------------

def cmd_init():
    import uuid as _uuid
    print("Initializing Forge Environment...")

    project_root = os.path.abspath(os.environ.get("FORGE_REPO_ROOT", "."))
    dotfile_path = os.path.join(project_root, ".forge")

    # Block migration path — .forge/ directory still present
    if os.path.isdir(dotfile_path):
        print("[Forge] Legacy .forge/ directory found.")
        print("[Forge] Run: forge migrate    to move data to ~/.forge/ and create the dotfile.")
        return

    # Load existing dotfile or create new project identity
    if os.path.isfile(dotfile_path):
        try:
            meta = json.loads(open(dotfile_path, "r", encoding="utf-8").read())
            project_id = meta["project_id"]
            data_dir = os.path.expanduser(meta["data_dir"])
        except Exception as _e:
            print(f"[Forge] Could not read .forge dotfile: {{_e}}")
            return
    else:
        project_id = str(_uuid.uuid4())
        data_dir = os.path.expanduser(f"~/.forge/projects/{{project_id}}")
        meta = {{
            "project_id": project_id,
            "project_name": os.path.basename(project_root),
            "org": "",
            "data_dir": f"~/.forge/projects/{{project_id}}"
        }}
        with open(dotfile_path, "w", encoding="utf-8") as _f:
            json.dump(meta, _f, indent=2)
        print(f"[Forge] Created .forge dotfile (commit this file to your repo)")

    FORGE_DIR = data_dir
    os.makedirs(FORGE_DIR, exist_ok=True)

    directories = [
        "00-context",
        "01-requirements",
        "02-design",
        "03-analysis",
        "04-architecture/adr",
        "05-delivery",
        "06-engineering",
        "07-quality",
        "08-operations",
        "09-release",
        "10-marketing",
        "11-agents",
        "12-gates",
        "13-decisions",
        "14-assets/logos",
        "14-assets/mockups",
        "14-assets/diagrams",
        "14-assets/screenshots",
        "14-assets/presentations",
        "14-assets/prototypes",
        "runs",
        "scripts",
        "15-build/backend",
        "15-build/frontend",
        "15-build/integration",
        "15-build/tests",
        "15-build/infra",
    ]

    for d in directories:
        os.makedirs(os.path.join(FORGE_DIR, d), exist_ok=True)

    files_to_touch = {FILES_TO_TOUCH}

    for f in files_to_touch:
        with open(os.path.join(FORGE_DIR, f), 'a', encoding='utf-8'):
            pass

    # Agents
    agents = [
        "product-strategist",
        "product-manager",
        "business-analyst",
        "product-designer",
        "ux-designer",
        "design-system-reviewer",
        "architect",
        "backend-engineer",
        "frontend-engineer",
        "qa-engineer",
        "devops-engineer",
        "security-reviewer",
        "release-manager",
        "marketing-strategist",
        "brand-strategist",
        "content-writer",
        "seo-specialist",
        "growth-marketer",
        "product-analyst",
        "code-architect",
        "frontend-coder",
        "integration-engineer",
        "qa-coder",
        "devops-coder",
    ]

    agent_template = """# Agent: {{agent}}

## Responsibility
Define this agent's responsibility.

## Inputs
- TBD

## Outputs
- TBD

## Rules
- Do not invent missing facts.
- Mark assumptions clearly.
- Add open questions where required.
- Produce structured markdown only.

## Review Checklist
- Is the output complete?
- Are assumptions explicit?
- Are risks captured?
- Are next steps clear?
"""
{AGENT_CODE}

    # Gates
    gates = [
        "context-gate",
        "prd-gate",
        "design-gate",
        "architecture-gate",
        "engineering-gate",
        "qa-gate",
        "release-gate",
        "marketing-gate"
    ]

    gate_template = """# Gate: {{gate}}

## Status
PENDING

## Required Checks
- Input files are available.
- Output file is complete.
- Open questions are captured.
- Assumptions are documented.
- Human review is completed.

## Blocking Issues
- TBD

## Reviewer Notes
- TBD
"""
{GATE_CODE}

    with open(os.path.join(FORGE_DIR, "13-decisions/decision-log.md"), "w", encoding='utf-8') as f:
        f.write("# Decision Log\\n\\n| Date | Decision | Context | Owner | Status |\\n|---|---|---|---|---|\\n")

    with open(os.path.join(FORGE_DIR, "13-decisions/change-log.md"), "w", encoding='utf-8') as f:
        f.write("# Change Log\\n\\n| Date | Change | Reason | Owner |\\n|---|---|---|---|\\n")

    with open(os.path.join(FORGE_DIR, "13-decisions/adr-index.md"), "w", encoding='utf-8') as f:
        f.write("# ADR Index\\n\\n| ADR | Title | Status | Date |\\n|---|---|---|---|\\n")

    current_date = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    with open(os.path.join(FORGE_DIR, "runs/run-log.md"), "w", encoding='utf-8') as f:
        f.write(f"# Run Log\\n\\n| Date | Command | Status |\\n|---|---|---|\\n| {{current_date}} | init | SUCCESS |\\n")

    with open(os.path.join(FORGE_DIR, "runs/execution-history.md"), "w", encoding='utf-8') as f:
        f.write("# Execution History\\n")

    with open(os.path.join(FORGE_DIR, "runs/failed-runs.md"), "w", encoding='utf-8') as f:
        f.write("# Failed Runs\\n")

    # Seed Scripts
    with open(os.path.join(FORGE_DIR, "scripts/stage_runner.py"), "w", encoding='utf-8') as f:
        f.write(STAGE_RUNNER_PY)
    with open(os.path.join(FORGE_DIR, "scripts/run.py"), "w", encoding='utf-8') as f:
        f.write(RUN_PY)
    with open(os.path.join(FORGE_DIR, "scripts/validate_gates.py"), "w", encoding='utf-8') as f:
        f.write(VALIDATE_GATES_PY)
    with open(os.path.join(FORGE_DIR, "scripts/build_runner.py"), "w", encoding='utf-8') as f:
        f.write(BUILD_RUNNER_PY)
    with open(os.path.join(FORGE_DIR, "scripts/server.py"), "w", encoding='utf-8') as f:
        f.write(SERVER_PY)
    with open(os.path.join(FORGE_DIR, "scripts/constants.py"), "w", encoding='utf-8') as f:
        f.write(CONSTANTS_PY)
    with open(os.path.join(FORGE_DIR, "scripts/dashboard.html"), "w", encoding='utf-8') as f:
        f.write(DASHBOARD_HTML)
    print("Dashboard deployed to .forge/scripts/")

    reviews_path = os.path.join(FORGE_DIR, "reviews.json")
    if not os.path.exists(reviews_path):
        with open(reviews_path, "w", encoding='utf-8') as f:
            json.dump({{}}, f)

    os.makedirs(os.path.join(FORGE_DIR, "00-raw-input"), exist_ok=True)

    state_path = os.path.join(FORGE_DIR, "project-state.json")
    if not os.path.exists(state_path):
        with open(state_path, "w", encoding='utf-8') as f:
            json.dump({{}}, f)

    print(f"Forge OS environment initialized successfully in {{FORGE_DIR}}")

PIPELINE_STAGES = [
    "context", "requirements", "design", "analysis", "architecture",
    "delivery", "engineering", "qa", "operations", "release", "marketing"
]

def cmd_generate(stage, input_file=None):
    forge_data_dir, project_root = _resolve_data_dir()
    if not os.path.exists(forge_data_dir):
        print("Forge not initialized. Please run 'forge init' first.")
        sys.exit(1)

    abs_input = None
    if input_file:
        if not os.path.exists(input_file):
            print(f"Input file not found: {{input_file}}")
            sys.exit(1)
        abs_input = os.path.abspath(input_file)

    print(f"Generating {{stage}}...")

    cmd = [sys.executable, "scripts/stage_runner.py", stage]
    if abs_input:
        cmd.append(abs_input)

    env = {{**os.environ, "FORGE_REPO_ROOT": project_root, "FORGE_DATA_DIR": forge_data_dir}}
    result = subprocess.run(cmd, cwd=forge_data_dir, env=env)

    if result.returncode == 0:
        print(f"Forge {{stage}} generation completed successfully.")
    else:
        print(f"Forge {{stage}} generation failed.")
        sys.exit(1)

def cmd_pipeline(input_file=None):
    forge_data_dir, project_root = _resolve_data_dir()
    if not os.path.exists(forge_data_dir):
        print("Forge not initialized. Please run 'forge init' first.")
        sys.exit(1)

    raw = input_file or "raw-input.md"
    if not os.path.exists(raw):
        print(f"No raw-input.md found at: {{raw}}")
        print("Create one describing your project, then run again.")
        sys.exit(1)

    abs_raw = os.path.abspath(raw)
    print(f"Starting pipeline from: {{raw}}")
    print("Documents are marked 'needs_review' after generation.")
    print("Review in the dashboard and mark reviewed — gates auto-pass.")
    print()

    env = {{**os.environ, "FORGE_REPO_ROOT": project_root, "FORGE_DATA_DIR": forge_data_dir}}
    for stage in PIPELINE_STAGES:
        print(f"==> [{{stage}}]")
        cmd = [sys.executable, "scripts/stage_runner.py", stage, abs_raw]
        result = subprocess.run(cmd, cwd=forge_data_dir, env=env)
        if result.returncode != 0:
            print("")
            print(f"  Gate blocked at stage '{{stage}}'.")
            print(f"  Review docs in the dashboard, then run: ./forge generate {{stage}}")
            sys.exit(1)
        print(f"  Done. Review '{{stage}}' docs before the next gate.")

    print("==> All stages generated.")
    print("    Open dashboard, review and approve documents to pass gates.")

def cmd_dashboard(port=DEFAULT_PORT):
    forge_data_dir, project_root = _resolve_data_dir()
    if not os.path.exists(forge_data_dir):
        print("Forge not initialized. Please run 'forge init' first.")
        sys.exit(1)

    server_script = os.path.join(forge_data_dir, "scripts/server.py")
    if not os.path.exists(server_script):
        print("Dashboard scripts not found. Run 'forge init' to regenerate.")
        sys.exit(1)

    print(f"Starting Forge Dashboard on port {{port}}...")
    forge_abs = os.path.abspath(sys.argv[0])
    result = subprocess.run(
        [sys.executable, server_script, str(port)],
        env={{
            **os.environ,
            "FORGE_REPO_ROOT": project_root,
            "FORGE_DATA_DIR": forge_data_dir,
            "FORGE_VERSION": FORGE_VERSION,
            "FORGE_SCRIPT": forge_abs,
        }}
    )
    sys.exit(result.returncode)

def cmd_migrate():
    import uuid as _uuid, shutil as _shutil
    project_root = os.path.abspath(os.environ.get("FORGE_REPO_ROOT", "."))
    legacy_dir = os.path.join(project_root, ".forge")

    if not os.path.isdir(legacy_dir):
        print("[Forge] No legacy .forge/ directory found — nothing to migrate.")
        return

    project_id = str(_uuid.uuid4())
    data_dir = os.path.expanduser(f"~/.forge/projects/{{project_id}}")

    print(f"[Forge] Migrating {{legacy_dir}}")
    print(f"[Forge]       → {{data_dir}}")
    os.makedirs(os.path.dirname(data_dir), exist_ok=True)
    _shutil.copytree(legacy_dir, data_dir)
    _shutil.rmtree(legacy_dir)

    meta = {{
        "project_id": project_id,
        "project_name": os.path.basename(project_root),
        "org": "",
        "data_dir": f"~/.forge/projects/{{project_id}}"
    }}
    with open(legacy_dir, "w", encoding="utf-8") as _f:
        json.dump(meta, _f, indent=2)

    print("[Forge] Migration complete.")
    print(f"[Forge] Data directory: {{data_dir}}")
    print("[Forge] Next: git add .forge && git commit -m 'chore: add Forge OS project pointer'")

def cmd_upgrade():
    print(f"Forge OS v{{FORGE_VERSION}} — upgrading runtime scripts...")
    forge_data_dir, _ = _resolve_data_dir()
    if not os.path.exists(forge_data_dir):
        print("Forge not initialized. Run './forge init' first.")
        sys.exit(1)
    cmd_init()
    print("Upgrade complete. Runtime scripts updated, project data preserved.")

def cmd_dev(port=DEFAULT_PORT):
    forge_script = os.path.abspath(sys.argv[0])
    build_script = os.path.join(os.path.dirname(forge_script), "src/build_forge.py")

    print("==> Building forge...")
    result = subprocess.run([sys.executable, build_script])
    if result.returncode != 0:
        print("Build failed.")
        sys.exit(result.returncode)

    print("==> Initializing environment...")
    result = subprocess.run([forge_script, "init"])
    if result.returncode != 0:
        print("Init failed.")
        sys.exit(result.returncode)

    # Symlink src/dashboard.html so edits are live without rebuilding
    forge_data_dir, _ = _resolve_data_dir()
    src_dash = os.path.join(os.path.dirname(forge_script), "src/dashboard.html")
    dst_dash = os.path.join(forge_data_dir, "scripts/dashboard.html")
    if os.path.exists(src_dash):
        if os.path.exists(dst_dash) or os.path.islink(dst_dash):
            os.remove(dst_dash)
        os.symlink(src_dash, dst_dash)
        print("==> Live dashboard symlink established.")

    print(f"==> Starting dashboard on port {{port}}...")
    cmd_dashboard(port)

# -------------------------------------------------------------------------
# CLI Entry Point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    if args and args[0] == "--project":
        if len(args) < 2:
            print("Usage: ./forge --project <path> <command>")
            sys.exit(1)
        project_path = os.path.abspath(args[1])
        os.environ["FORGE_REPO_ROOT"] = project_path
        args = args[2:]

    if not args:
        print(f"Forge OS v{{FORGE_VERSION}}")
        print("Usage: ./forge [--project <path>] <version|init|migrate|upgrade|generate [stage]|pipeline|dashboard [port]|dev [port]>")
        sys.exit(1)

    command = args[0]

    if command in ("version", "--version", "-v"):
        print(f"Forge OS v{{FORGE_VERSION}}")
        sys.exit(0)
    elif command == "upgrade":
        cmd_upgrade()
    elif command == "init":
        cmd_init()
    elif command == "generate":
        if len(args) == 1:
            cmd_pipeline()
        elif len(args) == 2:
            cmd_generate(args[1], None)
        elif len(args) == 3:
            cmd_generate(args[1], args[2])
        else:
            print("Usage: ./forge generate [stage] [input-file]")
            sys.exit(1)
    elif command == "pipeline":
        input_file = args[1] if len(args) > 1 else None
        cmd_pipeline(input_file)
    elif command == "dashboard":
        port = int(args[1]) if len(args) > 1 else DEFAULT_PORT
        cmd_dashboard(port)
    elif command == "dev":
        port = int(args[1]) if len(args) > 1 else DEFAULT_PORT
        cmd_dev(port)
    elif command == "migrate":
        cmd_migrate()
    else:
        print(f"Unknown command: {{command}}")
        print("Available commands: version, init, migrate, upgrade, generate [stage], pipeline, dashboard [port], dev [port]")
        sys.exit(1)
'''

def build_forge():
    all_agents = {**AGENTS, **CODE_AGENTS}
    agent_code = ('    for agent in agents:\n'
                  '        agent_path = os.path.join(FORGE_DIR, f"11-agents/{agent}.md")\n'
                  '        needs_write = not os.path.exists(agent_path)\n'
                  '        if not needs_write:\n'
                  '            with open(agent_path, encoding="utf-8") as _af:\n'
                  '                _content = _af.read()\n'
                  '            needs_write = "Define this agent" in _content or "TBD" in _content\n'
                  '        if needs_write:\n'
                  '            with open(agent_path, "w", encoding="utf-8") as f:\n')
    first = True
    for agent, text in all_agents.items():
        if first:
            agent_code += f'                if agent == "{agent}":\n                    f.write("""{text}""")\n'
            first = False
        else:
            agent_code += f'                elif agent == "{agent}":\n                    f.write("""{text}""")\n'

    agent_code += '                else:\n                    f.write(agent_template.format(agent=agent))\n'
    
    gate_code = '    for gate in gates:\n        gate_path = os.path.join(FORGE_DIR, f"12-gates/{gate}.md")\n        if not os.path.exists(gate_path):\n            with open(gate_path, "w", encoding="utf-8") as f:\n'
    first_gate = True
    for gate, text in GATES.items():
        if first_gate:
            gate_code += f'                if gate == "{gate}":\n                    f.write("""{text}""")\n'
            first_gate = False
        else:
            gate_code += f'                elif gate == "{gate}":\n                    f.write("""{text}""")\n'
    gate_code += '                else:\n                    f.write(gate_template.format(gate=gate))\n'

    forge_content = TEMPLATE.format(
        STAGE_MULTI_OUTPUTS=STAGE_MULTI_OUTPUTS,
        FILES_TO_TOUCH=FILES_TO_TOUCH,
        AGENT_CODE=agent_code,
        GATE_CODE=gate_code,
        DASHBOARD_HTML_CONTENT=DASHBOARD_HTML_CONTENT,
        FORGE_VERSION=FORGE_VERSION,
        BUILD_RUNNER_PY_CONTENT=BUILD_RUNNER_PY_CONTENT,
        ALLOWED_MODELS_CODE=_generate_allowed_models_code(KNOWN_TOOLS),
        CONSTANTS_PY_CONTENT=CONSTANTS_PY_CONTENT,
    )

    forge_content = forge_content.replace("__FORGE_SERVER_PY__", SERVER_PY_CONTENT)
    with open("forge", "w", encoding='utf-8') as f:
        f.write(forge_content)

    # Hot-deploy dashboard.html, server.py, and constants.py to all existing .forge/scripts/
    # directories so a rebuild immediately takes effect without a manual upgrade.
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

    print("forge built successfully.")

if __name__ == "__main__":
    build_forge()
