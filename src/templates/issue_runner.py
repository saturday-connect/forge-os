import json
import os
import subprocess
import sys
from datetime import datetime, timezone

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(FORGE_ROOT)
ISSUES_DIR = os.path.join(FORGE_ROOT, "issues")
ISSUES_FILE = os.path.join(ISSUES_DIR, "issues.json")
LIFECYCLE_FILE = os.path.join(FORGE_ROOT, "lifecycle.json")
RUNTIME_CONFIG_FILE = os.path.join(FORGE_ROOT, "runtime-config.json")
STATUS_FILE = os.path.join(FORGE_ROOT, "runs", "status.json")
STATUS_IDLE = "idle"
STATUS_RUNNING = "running"
PHASE_DOCS_REITERATING = "reiterating_docs"
PHASE_BUILDING = "building_product"
PHASE_READY = "ready_for_execution"
PHASE_DOCS_READY = "docs_generated"


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


def load_runtime_config():
    return load_json(RUNTIME_CONFIG_FILE, {"tool": "gemini", "model": ""})


def load_lifecycle():
    default_state = {
        "phase": "initialized",
        "docsStatus": "pending",
        "buildStatus": "idle",
        "currentStage": "",
        "lastIssueId": "",
        "lastUpdatedAt": now_iso(),
    }
    state = load_json(LIFECYCLE_FILE, default_state)
    for key, value in default_state.items():
        state.setdefault(key, value)
    return state


def save_lifecycle(state):
    state["lastUpdatedAt"] = now_iso()
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
    raise SystemExit(f"Issue not found: {issue_id}")


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
        env["FORGE_AI_TOOL"] = runtime_config["tool"]
    if runtime_config.get("model"):
        env["FORGE_AI_MODEL"] = runtime_config["model"]
    return subprocess.run(command, cwd=FORGE_ROOT, env=env)


def run_build_step(issue_id):
    command = [sys.executable, "scripts/build_product.py", issue_id]
    return subprocess.run(command, cwd=FORGE_ROOT)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/issue_runner.py <issue-id>")

    issue_id = sys.argv[1]
    issues, issue = find_issue(issue_id)
    lifecycle = load_lifecycle()
    runtime_config = load_runtime_config()

    lifecycle["phase"] = PHASE_DOCS_REITERATING
    lifecycle["docsStatus"] = STATUS_RUNNING
    lifecycle["buildStatus"] = "pending" if issue.get("requiresCodeChanges") else "not_required"
    lifecycle["currentStage"] = issue.get("stage", "")
    lifecycle["lastIssueId"] = issue_id
    save_lifecycle(lifecycle)

    issue["lastRunAt"] = now_iso()
    set_issue_state(issue, PHASE_DOCS_REITERATING)
    save_issues(issues)

    update_status(
        {
            "status": STATUS_RUNNING,
            "kind": "issue-docs",
            "issueId": issue_id,
            "stage": issue.get("stage", ""),
            "updatedAt": now_iso(),
        }
    )

    docs_result = run_docs_iteration(issue, runtime_config)
    if docs_result.returncode != 0:
        lifecycle["docsStatus"] = "failed"
        lifecycle["phase"] = "issue_failed"
        save_lifecycle(lifecycle)
        set_issue_state(issue, "failed")
        save_issues(issues)
        update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})
        raise SystemExit(docs_result.returncode)

    lifecycle["docsStatus"] = "completed"
    lifecycle["phase"] = PHASE_DOCS_READY
    save_lifecycle(lifecycle)
    set_issue_state(issue, "docs_updated")
    save_issues(issues)

    if issue.get("requiresCodeChanges"):
        lifecycle["phase"] = PHASE_BUILDING
        lifecycle["buildStatus"] = STATUS_RUNNING
        save_lifecycle(lifecycle)
        set_issue_state(issue, PHASE_BUILDING)
        save_issues(issues)

        build_result = run_build_step(issue_id)
        if build_result.returncode != 0:
            lifecycle["buildStatus"] = "failed"
            lifecycle["phase"] = "issue_failed"
            save_lifecycle(lifecycle)
            set_issue_state(issue, "failed")
            save_issues(issues)
            update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})
            raise SystemExit(build_result.returncode)

        lifecycle["buildStatus"] = "completed"
        lifecycle["phase"] = PHASE_READY
        save_lifecycle(lifecycle)
        set_issue_state(issue, "completed")
        issue["buildStatus"] = "completed"
        save_issues(issues)
    else:
        lifecycle["buildStatus"] = "not_required"
        lifecycle["phase"] = PHASE_READY
        save_lifecycle(lifecycle)
        set_issue_state(issue, "completed")
        issue["buildStatus"] = "not_required"
        save_issues(issues)

    update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})


if __name__ == "__main__":
    main()
