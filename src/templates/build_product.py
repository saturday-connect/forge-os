import json
import os
import subprocess
import sys
from datetime import datetime, timezone

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(FORGE_ROOT)
ISSUES_FILE = os.path.join(FORGE_ROOT, "issues", "issues.json")
RUNTIME_CONFIG_FILE = os.path.join(FORGE_ROOT, "runtime-config.json")
STATUS_FILE = os.path.join(FORGE_ROOT, "runs", "status.json")
MAX_CONTEXT_FILES = 12
TOOL_GEMINI = "gemini"
TOOL_CODEX = "codex"
STATUS_BUILDING = "building"
STATUS_FAILED = "failed"
DEFAULT_CONTEXT_DIRECTORIES = [
    "06-engineering",
    "04-architecture",
    "05-delivery",
    "01-requirements",
    "02-design",
    "03-analysis",
]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path, default_value):
    if not os.path.exists(path):
        return default_value
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, value):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


def update_status(payload):
    write_json(STATUS_FILE, payload)


def load_runtime_config():
    return load_json(RUNTIME_CONFIG_FILE, {"tool": TOOL_GEMINI, "model": ""})


def load_issues():
    return load_json(ISSUES_FILE, [])


def save_issues(issues):
    write_json(ISSUES_FILE, issues)


def find_issue(issue_id):
    issues = load_issues()
    for issue in issues:
        if issue.get("id") == issue_id:
            return issues, issue
    raise SystemExit(f"Issue not found: {issue_id}")


def collect_context_files(issue=None):
    context_files = []
    preferred_dirs = []

    requested_stage = issue.get("stage", "") if issue else ""
    if requested_stage:
        preferred_dirs.append(os.path.join(FORGE_ROOT, requested_stage))

    preferred_dirs.extend(
        [os.path.join(FORGE_ROOT, directory) for directory in DEFAULT_CONTEXT_DIRECTORIES]
    )

    seen_paths = set()
    for directory in preferred_dirs:
        if not os.path.isdir(directory):
            continue
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".md"):
                continue
            full_path = os.path.join(directory, filename)
            if full_path in seen_paths:
                continue
            seen_paths.add(full_path)
            context_files.append(full_path)
            if len(context_files) >= MAX_CONTEXT_FILES:
                return context_files
    return context_files


def build_issue_prompt(issue):
    prompt_parts = []
    prompt_parts.append("Implement the requested product change in this repository.\n")
    prompt_parts.append("Use the documentation context below as the source of truth.\n")
    prompt_parts.append("If code changes are required, edit the codebase directly.\n")
    prompt_parts.append("Do not rewrite documentation unless it is necessary to keep code and docs aligned.\n")
    prompt_parts.append("Prefer minimal, working changes.\n\n")
    prompt_parts.append(f"Issue ID: {issue['id']}\n")
    prompt_parts.append(f"Title: {issue['title']}\n")
    prompt_parts.append(f"Stage: {issue['stage']}\n")
    prompt_parts.append(f"Description:\n{issue['description']}\n\n")
    prompt_parts.append("Context files:\n")

    for path in collect_context_files(issue):
        rel_path = os.path.relpath(path, REPO_ROOT)
        with open(path, "r", encoding="utf-8") as f:
            prompt_parts.append(f"\n--- START OF {rel_path} ---\n")
            prompt_parts.append(f.read())
            prompt_parts.append(f"\n--- END OF {rel_path} ---\n")

    prompt_parts.append("\nReturn a concise summary of what changed when done.\n")
    return "".join(prompt_parts)


def build_baseline_prompt():
    prompt_parts = []
    prompt_parts.append("Implement the product described by the current Forge documentation.\n")
    prompt_parts.append("Use the generated documentation as the source of truth.\n")
    prompt_parts.append("Edit the codebase directly and keep documentation aligned when necessary.\n")
    prompt_parts.append("Prefer the smallest working implementation that satisfies the documented plan.\n\n")
    prompt_parts.append("Context files:\n")

    for path in collect_context_files():
        rel_path = os.path.relpath(path, REPO_ROOT)
        with open(path, "r", encoding="utf-8") as f:
            prompt_parts.append(f"\n--- START OF {rel_path} ---\n")
            prompt_parts.append(f.read())
            prompt_parts.append(f"\n--- END OF {rel_path} ---\n")

    prompt_parts.append("\nReturn a concise summary of what changed when done.\n")
    return "".join(prompt_parts)


def run_gemini(prompt, model_name):
    command = ["gemini", "--skip-trust", "--approval-mode", "auto_edit"]
    if model_name:
        command.extend(["--model", model_name])
    command.extend(["--prompt", prompt])
    return subprocess.run(command, cwd=REPO_ROOT)


def run_codex(prompt, model_name):
    command = [
        "codex",
        "--ask-for-approval",
        "never",
        "exec",
        "--skip-git-repo-check",
        "--sandbox",
        "workspace-write",
    ]
    if model_name:
        command.extend(["--model", model_name])
    command.append(prompt)
    return subprocess.run(command, cwd=REPO_ROOT)


def main():
    if len(sys.argv) > 2:
        raise SystemExit("Usage: python3 scripts/build_product.py [issue-id]")

    issue_id = sys.argv[1] if len(sys.argv) == 2 else ""
    issues = None
    issue = None
    if issue_id:
        issues, issue = find_issue(issue_id)
    runtime_config = load_runtime_config()
    tool_name = runtime_config.get("tool", TOOL_GEMINI)
    model_name = runtime_config.get("model", "")
    prompt = build_issue_prompt(issue) if issue else build_baseline_prompt()

    update_status(
        {
            "status": STATUS_BUILDING,
            "kind": "build",
            "issueId": issue_id,
            "tool": tool_name,
            "model": model_name,
            "updatedAt": now_iso(),
        }
    )

    if tool_name == TOOL_GEMINI:
        result = run_gemini(prompt, model_name)
    elif tool_name == TOOL_CODEX:
        result = run_codex(prompt, model_name)
    else:
        raise SystemExit(f"Selected tool does not support code build orchestration: {tool_name}")

    if issue is not None:
        issue["buildStatus"] = "completed" if result.returncode == 0 else STATUS_FAILED
        issue["updatedAt"] = now_iso()
        save_issues(issues)

    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
