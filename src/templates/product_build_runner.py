import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from template_constants import (
    FILE_ENCODING,
    FILE_LIFECYCLE,
    FILE_STATUS,
    ISO_TIMESTAMP_FORMAT,
    PHASE_BUILDING_PRODUCT,
    PHASE_BUILD_FAILED,
    PHASE_INITIALIZED,
    PHASE_READY_FOR_EXECUTION,
    STATUS_BUILDING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IDLE,
    STATUS_KIND_BUILD,
    STATUS_PENDING,
    STATUS_RUNNING,
    LIFECYCLE_KEY_PHASE,
    LIFECYCLE_KEY_DOCS_STATUS,
    LIFECYCLE_KEY_BUILD_STATUS,
    LIFECYCLE_KEY_CURRENT_STAGE,
    LIFECYCLE_KEY_LAST_ISSUE_ID,
    LIFECYCLE_KEY_LAST_UPDATED_AT,
    USAGE_PRODUCT_BUILD_RUNNER,
)

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIFECYCLE_FILE = os.path.join(FORGE_ROOT, FILE_LIFECYCLE)
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


def main():
    if len(sys.argv) != 1:
        raise SystemExit(USAGE_PRODUCT_BUILD_RUNNER)

    lifecycle = load_lifecycle()
    lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_BUILDING_PRODUCT
    lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_RUNNING
    save_lifecycle(lifecycle)

    update_status(
        {
            "status": STATUS_BUILDING,
            "kind": STATUS_KIND_BUILD,
            "updatedAt": now_iso(),
        }
    )

    command = [sys.executable, "scripts/build_product.py"]
    result = subprocess.run(command, cwd=FORGE_ROOT)

    if result.returncode != 0:
        lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_BUILD_FAILED
        lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_FAILED
        save_lifecycle(lifecycle)
        update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})
        raise SystemExit(result.returncode)

    lifecycle[LIFECYCLE_KEY_PHASE] = PHASE_READY_FOR_EXECUTION
    lifecycle[LIFECYCLE_KEY_BUILD_STATUS] = STATUS_COMPLETED
    save_lifecycle(lifecycle)
    update_status({"status": STATUS_IDLE, "updatedAt": now_iso()})


if __name__ == "__main__":
    main()
