import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from template_constants import (
    DEFAULT_CONTEXT_DIRECTORIES,
    ERROR_ISSUE_NOT_FOUND,
    ERROR_UNSUPPORTED_TOOL,
    FILE_ENCODING,
    FILE_ISSUES,
    FILE_RUNTIME_CONFIG,
    FILE_STATUS,
    GEMINI_ARGS_BASE,
    CODEX_ARGS_BASE,
    ISO_TIMESTAMP_FORMAT,
    MARKDOWN_EXTENSION,
    MAX_CONTEXT_FILES,
    PROMPT_BASELINE_HEADER,
    PROMPT_CONTEXT_FILE_END,
    PROMPT_CONTEXT_FILE_START,
    PROMPT_CONTEXT_FILES_LABEL,
    PROMPT_ISSUE_HEADER,
    PROMPT_RETURN_SUMMARY,
    STATUS_BUILDING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_KIND_BUILD,
    TOOL_CODEX,
    TOOL_GEMINI,
    USAGE_BUILD_PRODUCT,
)

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(FORGE_ROOT)
ISSUES_FILE = os.path.join(FORGE_ROOT, FILE_ISSUES)
RUNTIME_CONFIG_FILE = os.path.join(FORGE_ROOT, FILE_RUNTIME_CONFIG)
STATUS_FILE = os.path.join(FORGE_ROOT, FILE_STATUS)


def now_iso():
    return datetime.now(timezone.utc).strftime(ISO_TIMESTAMP_FORMAT)


def load_json(path, default_value):
    if not os.path.exists(path):
        return default_value
    with open(path, "r", encoding=FILE_ENCODING) as f:
        return json.load(f)


def write_json(path, value):
    with open(path, "w", encoding=FILE_ENCODING) as f:
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
    raise SystemExit(ERROR_ISSUE_NOT_FOUND.format(issue_id=issue_id))


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
            if not filename.endswith(MARKDOWN_EXTENSION):
                continue
            full_path = os.path.join(directory, filename)
            if full_path in seen_paths:
                continue
            seen_paths.add(full_path)
            context_files.append(full_path)
            if len(context_files) >= MAX_CONTEXT_FILES:
                return context_files
    return context_files


def _append_context_files(prompt_parts, context_file_list):
    prompt_parts.append(PROMPT_CONTEXT_FILES_LABEL)
    for path in context_file_list:
        rel_path = os.path.relpath(path, REPO_ROOT)
        with open(path, "r", encoding=FILE_ENCODING) as f:
            prompt_parts.append(PROMPT_CONTEXT_FILE_START.format(rel_path=rel_path))
            prompt_parts.append(f.read())
            prompt_parts.append(PROMPT_CONTEXT_FILE_END.format(rel_path=rel_path))
    prompt_parts.append(PROMPT_RETURN_SUMMARY)


def build_issue_prompt(issue):
    prompt_parts = [PROMPT_ISSUE_HEADER]
    prompt_parts.append(f"Issue ID: {issue['id']}\n")
    prompt_parts.append(f"Title: {issue['title']}\n")
    prompt_parts.append(f"Stage: {issue['stage']}\n")
    prompt_parts.append(f"Description:\n{issue['description']}\n\n")
    _append_context_files(prompt_parts, collect_context_files(issue))
    return "".join(prompt_parts)


def build_baseline_prompt():
    prompt_parts = [PROMPT_BASELINE_HEADER]
    _append_context_files(prompt_parts, collect_context_files())
    return "".join(prompt_parts)


def run_gemini(prompt, model_name):
    command = list(GEMINI_ARGS_BASE)
    if model_name:
        command.extend(["--model", model_name])
    command.extend(["--prompt", prompt])
    return subprocess.run(command, cwd=REPO_ROOT)


def run_codex(prompt, model_name):
    command = list(CODEX_ARGS_BASE)
    if model_name:
        command.extend(["--model", model_name])
    command.append(prompt)
    return subprocess.run(command, cwd=REPO_ROOT)


def main():
    if len(sys.argv) > 2:
        raise SystemExit(USAGE_BUILD_PRODUCT)

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
            "kind": STATUS_KIND_BUILD,
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
        raise SystemExit(ERROR_UNSUPPORTED_TOOL.format(tool_name=tool_name))

    if issue is not None:
        issue["buildStatus"] = STATUS_COMPLETED if result.returncode == 0 else STATUS_FAILED
        issue["updatedAt"] = now_iso()
        save_issues(issues)

    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
