import json
import os
import subprocess
import sys
from datetime import datetime, timezone

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIFECYCLE_FILE = os.path.join(FORGE_ROOT, "lifecycle.json")
STATUS_FILE = os.path.join(FORGE_ROOT, "runs", "status.json")
PHASE_BUILDING = "building_product"
PHASE_READY = "ready_for_execution"
PHASE_FAILED = "build_failed"
STATUS_IDLE = "idle"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


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


def load_lifecycle():
    default_state = {
        "phase": "initialized",
        "docsStatus": "pending",
        "buildStatus": STATUS_IDLE,
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


def main():
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python3 scripts/product_build_runner.py")

    lifecycle = load_lifecycle()
    lifecycle["phase"] = PHASE_BUILDING
    lifecycle["buildStatus"] = STATUS_RUNNING
    save_lifecycle(lifecycle)

    update_status(
        {
            "status": "building",
            "kind": "build",
            "updatedAt": now_iso(),
        }
    )

    command = [sys.executable, "scripts/build_product.py"]
    result = subprocess.run(command, cwd=FORGE_ROOT)

    if result.returncode != 0:
        lifecycle["phase"] = PHASE_FAILED
        lifecycle["buildStatus"] = STATUS_FAILED
        save_lifecycle(lifecycle)
        update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})
        raise SystemExit(result.returncode)

    lifecycle["phase"] = PHASE_READY
    lifecycle["buildStatus"] = STATUS_COMPLETED
    save_lifecycle(lifecycle)
    update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})


if __name__ == "__main__":
    main()
