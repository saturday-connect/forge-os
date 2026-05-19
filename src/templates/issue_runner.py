import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from template_constants import (
    ERROR_ISSUE_NOT_FOUND,
    ENV_FORGE_AI_TOOL,
    ENV_FORGE_AI_MODEL,
    FILE_ENCODING,
    FILE_ISSUES,
    FILE_LIFECYCLE,
    FILE_RUNTIME_CONFIG,
    FILE_STATUS,
    DIR_ISSUES,
    ISO_TIMESTAMP_FORMAT,
    LIFECYCLE_KEY_PHASE,
    LIFECYCLE_KEY_DOCS_STATUS,
    LIFECYCLE_KEY_BUILD_STATUS,
    LIFECYCLE_KEY_CURRENT_STAGE,
    LIFECYCLE_KEY_LAST_ISSUE_ID,
    LIFECYCLE_KEY_LAST_UPDATED_AT,
    PHASE_BUILDING_PRODUCT,
    PHASE_BUILD_FAILED,
    PHASE_DOCS_GENERATED,
    PHASE_DOCS_REITERATING,
    PHASE_INITIALIZED,
    PHASE_ISSUE_FAILED,
    PHASE_READY_FOR_EXECUTION,
    STATUS_COMPLETED,
    STATUS_DOCS_UPDATED,
    STATUS_FAILED,
    STATUS_IDLE,
    STATUS_KIND_ISSUE_DOCS,
    STATUS_NOT_REQUIRED,
    STATUS_PENDING,
    STATUS_RUNNING,
    TOOL_GEMINI,
    USAGE_ISSUE_RUNNER,
)

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(FORGE_ROOT)
ISSUES_DIR = os.path.join(FORGE_ROOT, DIR_ISSUES)
ISSUES_FILE = os.path.join(ISSUES_DIR, FILE_ISSUES.split("/")[-1])
LIFECYCLE_FILE = os.path.join(FORGE_ROOT, FILE_LIFECYCLE)
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


def load_runtime_config():
    return load_json(RUNTIME_CONFIG_FILE, {"tool": TOOL_GEMINI, "model": ""})


def load_lifecycle():
    default_state = {
        LIFECYCLE_KEY_PHASE: PHASE_INITIALIZED,
        LIFECYCLE_KEY_DOCS_STATUS: STATUS_PENDING,
        LIFECYCLE_KEY_BUILD_STATUS: STATUS_IDLE,
        LIFECYCLE_KEY_CURRENT_STAGE: "",
        LIFECYCLE_KEY_LAST_ISSUE_ID: "",
        LIFECYCLE_KEY_LAST_UPDATED_AT: now_iso(),
    }
    state = load_json(LIFECYCLE_FILE, default_state)
    for key, value in default_state.items():
        state.setdefault(key, value)
    return state


def save_lifecycle(state):
    state[LIFECYCLE_KEY_LAST_UPDATED_AT] = now_iso()
    write_json(LIFECYCLE_FILE, state)


def update_status(payload):
    write_json(STATUS_FILE, payload)


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


def set_issue_state(issue, status):
    issue["status"] = status
    issue["updatedAt"] = now_iso()


def run_docs_iteration(issue, runtime_config):
    stage_name = issue.get("stage", "")
    if "-" in stage_name:
        stage_name = stage_name.split("-", 1)[1]
    command = [sys.executable, "scripts/stage_runner.py", stage_name]
    env = dict(os.environ)
    if runtime_config.get("tool"):
        env[ENV_FORGE_AI_TOOL] = runtime_config["tool"]
    if runtime_config.get("model"):
        env[ENV_FORGE_AI_MODEL] = runtime_config["model"]
    return subprocess.run(command, cwd=FORGE_ROOT, env=env)


def run_build_step(issue_id):
    command = [sys.executable, "scripts/build_product.py", issue_id]
    return subprocess.run(command, cwd=FORGE_ROOT)


def main():
    if len(sys.argv) != 2:
        raise SystemExit(USAGE_ISSUE_RUNNER)

    issue_id = sys.argv[1]
    issues, issue = find_issue(issue_id)
    lifecycle = load_lifecycle()
    runtime_config = load_runtime_config()

    lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_DOCS_REITERATING
    lifecycle[LIFECYCLE_KEY_DOCS_STATUS] = STATUS_RUNNING
    lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_PENDING if issue.get("requiresCodeChanges") else STATUS_NOT_REQUIRED
    lifecycle[LIFECYCLE_KEY_CURRENT_STAGE] = issue.get("stage", "")
    lifecycle[LIFECYCLE_KEY_LAST_ISSUE_ID] = issue_id
    save_lifecycle(lifecycle)

    issue["lastRunAt"] = now_iso()
    set_issue_state(issue, PHASE_DOCS_REITERATING)
    save_issues(issues)

    update_status(
        {
            "status": STATUS_RUNNING,
            "kind": STATUS_KIND_ISSUE_DOCS,
            "issueId": issue_id,
            "stage": issue.get("stage", ""),
            "updatedAt": now_iso(),
        }
    )

    docs_result = run_docs_iteration(issue, runtime_config)
    if docs_result.returncode != 0:
        lifecycle[LIFECYCLE_KEY_DOCS_STATUS] = STATUS_FAILED
        lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_ISSUE_FAILED
        save_lifecycle(lifecycle)
        set_issue_state(issue, STATUS_FAILED)
        save_issues(issues)
        update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})
        raise SystemExit(docs_result.returncode)

    lifecycle[LIFECYCLE_KEY_DOCS_STATUS] = STATUS_COMPLETED
    lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_DOCS_GENERATED
    save_lifecycle(lifecycle)
    set_issue_state(issue, STATUS_DOCS_UPDATED)
    save_issues(issues)

    if issue.get("requiresCodeChanges"):
        lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_BUILDING_PRODUCT
        lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_RUNNING
        save_lifecycle(lifecycle)
        set_issue_state(issue, PHASE_BUILDING_PRODUCT)
        save_issues(issues)

        build_result = run_build_step(issue_id)
        if build_result.returncode != 0:
            lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_FAILED
            lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_ISSUE_FAILED
            save_lifecycle(lifecycle)
            set_issue_state(issue, STATUS_FAILED)
            save_issues(issues)
            update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})
            raise SystemExit(build_result.returncode)

        lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_COMPLETED
        lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_READY_FOR_EXECUTION
        save_lifecycle(lifecycle)
        set_issue_state(issue, STATUS_COMPLETED)
        issue["buildStatus"] = STATUS_COMPLETED
        save_issues(issues)
    else:
        lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_NOT_REQUIRED
        lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_READY_FOR_EXECUTION
        save_lifecycle(lifecycle)
        set_issue_state(issue, STATUS_COMPLETED)
        issue["buildStatus"] = STATUS_NOT_REQUIRED
        save_issues(issues)

    update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})


if __name__ == "__main__":
    main()
