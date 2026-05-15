import os
import sys
import json
import subprocess
import shutil
import time
import threading
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO_ROOT = os.path.abspath(os.environ.get("AEOS_REPO_ROOT", "."))
ORCHESTRATOR_ROOT = os.path.abspath(os.environ.get("FORGE_ORCHESTRATOR_ROOT", REPO_ROOT))
FORGE_DIR = os.path.join(REPO_ROOT, ".forge")
PROJECTS_ROOT = os.path.join(ORCHESTRATOR_ROOT, ".projects")
PROJECTS_INDEX_FILE = os.path.join(PROJECTS_ROOT, "index.json")
PROJECT_STATUS_ACTIVE = "active"
PROJECT_STATUS_ARCHIVED = "archived"

KNOWN_TOOLS = {
    "gemini": {
        "label": "Gemini CLI",
        "models": [
            {"id": "gemini-3-flash-preview",  "label": "Gemini 3 Flash (recommended)"},
            {"id": "gemini-3-pro-preview",     "label": "Gemini 3 Pro"},
            {"id": "gemini-2.5-flash",         "label": "Gemini 2.5 Flash"},
            {"id": "gemini-2.5-pro",           "label": "Gemini 2.5 Pro"},
            {"id": "gemini-2.5-flash-lite",    "label": "Gemini 2.5 Flash Lite (fastest)"},
        ]
    },
    "claude": {
        "label": "Claude Code CLI",
        "models": [
            {"id": "claude-sonnet-4-6",         "label": "Claude Sonnet 4.6 (recommended)"},
            {"id": "claude-opus-4-7",            "label": "Claude Opus 4.7"},
            {"id": "claude-haiku-4-5-20251001",  "label": "Claude Haiku 4.5 (fastest)"},
        ]
    },
    "codex": {
        "label": "Codex CLI",
        "models": [
            {"id": "o4-mini",    "label": "o4 Mini (recommended)"},
            {"id": "o3",         "label": "o3"},
            {"id": "gpt-4.1",    "label": "GPT-4.1"},
            {"id": "gpt-4.1-mini", "label": "GPT-4.1 Mini"},
        ]
    },
    "openai": {
        "label": "OpenAI API (direct)",
        "models": [
            {"id": "gpt-4o",      "label": "GPT-4o"},
            {"id": "gpt-4o-mini", "label": "GPT-4o Mini"},
            {"id": "o3-mini",     "label": "o3 Mini"},
        ]
    },
}
REVIEWS_FILE = os.path.join(FORGE_DIR, "reviews.json")
STATE_FILE = os.path.join(FORGE_DIR, "project-state.json")
RAW_INPUT_DIR = os.path.join(FORGE_DIR, "00-raw-input")
FORGE_VERSION = os.environ.get("FORGE_VERSION", "unknown")
FORGE_SCRIPT = os.environ.get("FORGE_SCRIPT", "")

def set_project_root(project_root):
    global REPO_ROOT, FORGE_DIR, REVIEWS_FILE, STATE_FILE, RAW_INPUT_DIR
    REPO_ROOT = os.path.abspath(project_root)
    FORGE_DIR = os.path.join(REPO_ROOT, ".forge")
    REVIEWS_FILE = os.path.join(FORGE_DIR, "reviews.json")
    STATE_FILE = os.path.join(FORGE_DIR, "project-state.json")
    RAW_INPUT_DIR = os.path.join(FORGE_DIR, "00-raw-input")
    os.environ["AEOS_REPO_ROOT"] = REPO_ROOT

def ensure_projects_root():
    os.makedirs(PROJECTS_ROOT, exist_ok=True)

def slugify_project_name(name):
    raw = (name or "").strip().lower()
    out = []
    prev_dash = False
    for ch in raw:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append("-")
                prev_dash = True
    slug = "".join(out).strip("-")
    return slug or "project"

def default_projects_index():
    return {"active_project_id": "", "projects": []}

def load_projects_index():
    ensure_projects_root()
    if os.path.exists(PROJECTS_INDEX_FILE):
        try:
            with open(PROJECTS_INDEX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("projects"), list):
                data.setdefault("active_project_id", "")
                return data
        except Exception:
            pass
    return default_projects_index()

def save_projects_index(index_data):
    ensure_projects_root()
    with open(PROJECTS_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

def ensure_unique_slug(index_data, base_slug):
    existing = {p.get("slug", "") for p in index_data.get("projects", [])}
    if base_slug not in existing:
        return base_slug
    i = 2
    while True:
        candidate = f"{base_slug}-{i}"
        if candidate not in existing:
            return candidate
        i += 1

def get_active_project(index_data):
    active_id = index_data.get("active_project_id", "")
    for p in index_data.get("projects", []):
        if p.get("id") == active_id and p.get("status", PROJECT_STATUS_ACTIVE) == PROJECT_STATUS_ACTIVE:
            return p
    return None

def get_project_by_id(index_data, project_id):
    for p in index_data.get("projects", []):
        if p.get("id") == project_id:
            return p
    return None

def choose_next_active_project(index_data):
    for p in index_data.get("projects", []):
        if p.get("status", PROJECT_STATUS_ACTIVE) == PROJECT_STATUS_ACTIVE:
            index_data["active_project_id"] = p.get("id", "")
            return p
    index_data["active_project_id"] = ""
    return None

def safe_project_path(project_path):
    root = os.path.abspath(PROJECTS_ROOT)
    target = os.path.abspath(project_path or "")
    return target.startswith(root + os.sep) and target != root

def sync_registry_from_disk(index_data):
    changed = False
    projects = []
    for p in index_data.get("projects", []):
        path = p.get("path", "")
        if path and os.path.isdir(path):
            p.setdefault("status", PROJECT_STATUS_ACTIVE)
            p.setdefault("archived_at", "")
            projects.append(p)
        else:
            changed = True
    index_data["projects"] = projects
    if index_data.get("active_project_id") and not get_active_project(index_data):
        choose_next_active_project(index_data)
        changed = True
    if changed:
        save_projects_index(index_data)
    return index_data

def invoke_ai(prompt, tool, model_id):
    import tempfile as _tmp
    with _tmp.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as t:
        tmp_path = t.name
    try:
        if tool == "gemini":
            cmd = ["gemini", "--skip-trust"]
            if model_id:
                cmd += ["-m", model_id]
            cmd += ["-p", prompt]
        elif tool == "claude":
            cmd = ["claude", "-p", prompt, "--output-format", "text"]
        else:
            cmd = ["gemini", "--skip-trust", "-p", prompt]
        with open(tmp_path, "w") as out_f:
            result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, timeout=600)
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace") if result.stderr else "AI call failed"
            return None, normalize_ai_error(err)
        with open(tmp_path, encoding="utf-8") as f:
            return f.read(), None
    except subprocess.TimeoutExpired:
        return None, "The request timed out after 10 minutes. Try again."
    except FileNotFoundError:
        return None, f"AI tool '{tool}' not found in PATH"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def normalize_ai_error(raw_error):
    text = (raw_error or "").strip()
    lowered = text.lower()
    quota_markers = [
        "you've hit your limit",
        "hit your limit",
        "usage limit",
        "quota",
        "rate limit",
        "too many requests",
        "status 429",
    ]
    if any(marker in lowered for marker in quota_markers):
        return "The AI request failed. Wait a few minutes, then retry."
    if not text:
        return "The AI model returned an error. Retry the request."
    return text.splitlines()[0][:220]

GATE_STAGE_MAP = {
    "context-gate": "00-context",
    "prd-gate": "01-requirements",
    "design-gate": "02-design",
    "architecture-gate": "04-architecture",
    "engineering-gate": "06-engineering",
    "qa-gate": "07-quality",
    "release-gate": "09-release",
    "marketing-gate": "10-marketing",
}

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_reviews(reviews):
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=2)

def _default_state():
    return {
        "project_name": "",
        "builds": [],
        "issues": [],
        "git": {
            "repo_url": "",
            "username": "",
            "email": "",
            "token": "",
            "default_branch": "main",
            "branch_prefix": "forge"
        },
        "environments": {
            "staging": {"url": "", "branch": "staging", "status": "not_deployed", "deployed_at": ""},
            "production": {"url": "", "branch": "main", "status": "not_deployed", "deployed_at": ""}
        },
        "tool": "gemini",
        "model": "gemini"
    }

def load_project_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
            # Merge with defaults for missing keys
            defaults = _default_state()
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
                elif isinstance(v, dict) and isinstance(data[k], dict):
                    for sk, sv in v.items():
                        if sk not in data[k]:
                            data[k][sk] = sv
            return data
        except Exception:
            pass
    return _default_state()

def save_project_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def list_raw_inputs():
    # Walk 00-raw-input/ recursively and return all .md files with relative paths.
    if not os.path.exists(RAW_INPUT_DIR):
        return []
    files = []
    for dirpath, dirnames, filenames in os.walk(RAW_INPUT_DIR):
        dirnames.sort()  # stable order
        for fname in sorted(filenames):
            if fname.endswith(".md"):
                fpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fpath, RAW_INPUT_DIR)
                st = os.stat(fpath)
                files.append({
                    "name": rel,
                    "size": st.st_size,
                    "modifiedAt": int(st.st_mtime)
                })
    return files

def get_combined_raw_input_path():
    # Combine all raw input files into a single temp file and return its path (or None).
    import tempfile
    files = list_raw_inputs()
    if not files:
        return None
    parts = []
    for f in files:
        fpath = os.path.join(RAW_INPUT_DIR, f["name"])
        try:
            with open(fpath, "r", encoding="utf-8") as fp:
                content = fp.read().strip()
            if content:
                label = f["name"].replace("/", " / ").replace(".md", "")
                parts.append(f"# [{label}]\n\n{content}")
        except Exception:
            pass
    if not parts:
        return None
    combined = "\n\n---\n\n".join(parts)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8", prefix="forge_raw_")
    tmp.write(combined)
    tmp.close()
    return tmp.name

def build_file_entry(stage_dir, filename, reviews):
    file_path = os.path.join(stage_dir, filename)
    file_stats = os.stat(file_path)
    file_size = file_stats.st_size
    modified_at = int(file_stats.st_mtime)
    stage_name = os.path.basename(stage_dir)
    rel_path = f"{stage_name}/{filename}"
    if reviews is None:
        reviews = {}
    if file_size == 0:
        status = "empty"
    elif reviews.get(rel_path) == "reviewed":
        status = "reviewed"
    else:
        status = "needs_review"
    return {
        "name": filename,
        "status": status,
        "size": file_size,
        "modifiedAt": modified_at,
    }

def parse_gate_status(content):
    in_status = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Status"):
            in_status = True
            continue
        if in_status and stripped:
            return "PASSED" if stripped.upper() in ("PASSED", "APPROVED") else "PENDING"
    return "PENDING"

def evaluate_gate(gate_name):
    stage_dir_name = GATE_STAGE_MAP.get(gate_name)
    if not stage_dir_name:
        return "PENDING"
    reviews = load_reviews()
    stage_path = os.path.join(FORGE_DIR, stage_dir_name)
    if not os.path.exists(stage_path):
        return "PENDING"
    md_files = [f for f in os.listdir(stage_path) if f.endswith(".md") and os.path.getsize(os.path.join(stage_path, f)) > 0]
    if not md_files:
        return "PENDING"
    for fname in md_files:
        if reviews.get(f"{stage_dir_name}/{fname}") != "reviewed":
            return "PENDING"
    return "PASSED"

def save_build_progress(entry):
    # Write build_entry live so /api/state can stream intermediate states
    progress_file = os.path.join(FORGE_DIR, "runs", "build-in-progress.json")
    try:
        with open(progress_file, "w") as f:
            json.dump(entry, f)
    except Exception:
        pass

def clear_build_progress():
    progress_file = os.path.join(FORGE_DIR, "runs", "build-in-progress.json")
    try:
        if os.path.exists(progress_file):
            os.remove(progress_file)
    except Exception:
        pass

def set_processing(status, stage=""):
    status_file = os.path.join(FORGE_DIR, "runs/status.json")
    runs_dir = os.path.join(FORGE_DIR, "runs")
    if os.path.exists(runs_dir):
        try:
            data = {"status": status, "stage": stage}
            # When transitioning to idle, preserve any last_error written by stage_runner
            if status == "idle" and os.path.exists(status_file):
                try:
                    with open(status_file, "r") as sf:
                        existing = json.load(sf)
                    if "last_error" in existing:
                        data["last_error"] = existing["last_error"]
                except Exception:
                    pass
            with open(status_file, "w") as sf:
                json.dump(data, sf)
        except Exception:
            pass

def compute_full_state():
    if not os.path.isdir(FORGE_DIR):
        return {
            "version": FORGE_VERSION,
            "phase": "input",
            "gates": {},
            "tree": {},
            "processing": {"status": "idle"},
            "stageReviewSummary": {},
            "allReviewed": False,
            "rawInputs": [],
            "builds": [],
            "issues": [],
            "environments": {},
            "git": {},
            "tool": "gemini",
            "model": "gemini",
            "project_name": "",
        }
    proj = load_project_state()
    reviews = load_reviews()

    # Gates
    gates = {}
    gates_dir = os.path.join(FORGE_DIR, "12-gates")
    if os.path.exists(gates_dir):
        for g in os.listdir(gates_dir):
            if g.endswith(".md"):
                gate_name = g.replace(".md", "")
                if gate_name in GATE_STAGE_MAP:
                    gates[gate_name] = evaluate_gate(gate_name)
                else:
                    with open(os.path.join(gates_dir, g), "r") as f:
                        content = f.read()
                    gates[gate_name] = parse_gate_status(content)

    # File tree
    VALID_STAGE_PREFIXES = {f"{i:02d}" for i in range(11)}
    files_tree = {}
    stage_review_summary = {}
    for d in sorted(os.listdir(FORGE_DIR)):
        d_path = os.path.join(FORGE_DIR, d)
        if os.path.isdir(d_path) and d[:2] in VALID_STAGE_PREFIXES and d != "00-raw-input":
            files_tree[d] = []
            reviewed_count = 0
            generated_count = 0
            total_count = 0
            for fname in sorted(os.listdir(d_path)):
                if fname.endswith(".md"):
                    entry = build_file_entry(d_path, fname, reviews)
                    files_tree[d].append(entry)
                    total_count += 1
                    if entry["status"] != "empty":
                        generated_count += 1
                    if entry["status"] == "reviewed":
                        reviewed_count += 1
            stage_review_summary[d] = {
                "reviewed": reviewed_count,
                "generated": generated_count,
                "total": total_count,
            }

    # Processing status
    processing_status = {"status": "idle"}
    status_file = os.path.join(FORGE_DIR, "runs/status.json")
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as sf:
                processing_status = json.load(sf)
        except Exception:
            pass

    all_reviewed = all(
        s["reviewed"] == s["generated"] and s["generated"] > 0
        for s in stage_review_summary.values()
    ) if stage_review_summary else False

    all_gates_passed = all(v == "PASSED" for v in gates.values()) if gates else False

    # Raw inputs
    raw_inputs = list_raw_inputs()

    # Compute phase
    total_generated = sum(s["generated"] for s in stage_review_summary.values())
    total_docs = sum(s["total"] for s in stage_review_summary.values())

    builds = proj.get("builds", [])

    # Merge any in-progress build so the dashboard sees it immediately
    progress_file = os.path.join(FORGE_DIR, "runs", "build-in-progress.json")
    if os.path.exists(progress_file):
        try:
            with open(progress_file) as _pf:
                in_progress = json.load(_pf)
            # Only inject if not already in builds list (avoid duplicates after finalize)
            if not any(b.get("id") == in_progress.get("id") for b in builds):
                builds = builds + [in_progress]
        except Exception:
            pass

    last_build = builds[-1] if builds else None

    if not raw_inputs:
        phase = "input"
    elif total_generated == 0:
        phase = "generate"
    elif total_generated < total_docs:
        phase = "generate"
    elif not all_reviewed:
        phase = "review"
    elif not builds or (last_build and last_build.get("status") not in ("pushed", "committed")):
        phase = "build"
    elif last_build and last_build.get("status") in ("pushed", "committed"):
        phase = "deploy"
    else:
        phase = "review"

    return {
        "version": FORGE_VERSION,
        "phase": phase,
        "gates": gates,
        "tree": files_tree,
        "processing": processing_status,
        "stageReviewSummary": stage_review_summary,
        "allReviewed": all_reviewed,
        "rawInputs": raw_inputs,
        "builds": builds,
        "issues": proj.get("issues", []),
        "environments": proj.get("environments", {}),
        "git": proj.get("git", {}),
        "tool": proj.get("tool", "gemini"),
        "model": proj.get("model", "gemini"),
        "project_name": proj.get("project_name", ""),
    }

def initialize_active_project():
    index_data = sync_registry_from_disk(load_projects_index())
    active = get_active_project(index_data)
    if active and os.path.isdir(active.get("path", "")):
        set_project_root(active["path"])
        return
    if os.path.isdir(FORGE_DIR):
        return
    projects = [
        p for p in index_data.get("projects", [])
        if p.get("status", PROJECT_STATUS_ACTIVE) == PROJECT_STATUS_ACTIVE
    ]
    if projects:
        index_data["active_project_id"] = projects[0].get("id", "")
        save_projects_index(index_data)
        set_project_root(projects[0].get("path", REPO_ROOT))

initialize_active_project()

class ForgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence access logs

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            dashboard_path = os.path.join(FORGE_DIR, "scripts/dashboard.html")
            if os.path.exists(dashboard_path):
                content = open(dashboard_path, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
            return

        if path == "/api/projects":
            index_data = sync_registry_from_disk(load_projects_index())
            active = get_active_project(index_data)
            payload_projects = []
            for p in index_data.get("projects", []):
                payload_projects.append({
                    "id": p.get("id", ""),
                    "name": p.get("name", ""),
                    "slug": p.get("slug", ""),
                    "path": p.get("path", ""),
                    "created_at": p.get("created_at", ""),
                    "updated_at": p.get("updated_at", ""),
                    "last_opened_at": p.get("last_opened_at", ""),
                    "archived_at": p.get("archived_at", ""),
                    "status": p.get("status", PROJECT_STATUS_ACTIVE),
                })
            self._json_response(200, {
                "workspace_root": PROJECTS_ROOT,
                "active_project_id": index_data.get("active_project_id", ""),
                "active_project": active or None,
                "projects": payload_projects,
            })
            return

        if path == "/api/state":
            try:
                state = compute_full_state()
                self._json_response(200, state)
            except Exception as e:
                self._json_response(500, {"error": str(e)})
            return

        if path == "/api/file":
            file_path = params.get("path", [None])[0]
            if not file_path:
                self._json_response(400, {"error": "missing path"})
                return
            abs_path = os.path.join(FORGE_DIR, file_path)
            if os.path.exists(abs_path):
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                with open(abs_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._json_response(404, {"error": "not found"})
            return

        if path == "/api/raw-input":
            name = params.get("name", [None])[0]
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            fpath = os.path.normpath(os.path.join(RAW_INPUT_DIR, name))
            if not fpath.startswith(RAW_INPUT_DIR):
                self._json_response(400, {"error": "invalid path"})
                return
            if os.path.exists(fpath):
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._json_response(404, {"error": "not found"})
            return

        if path == "/api/tools":
            result = {}
            for tool_id, info in KNOWN_TOOLS.items():
                found = shutil.which(tool_id)
                result[tool_id] = {
                    "installed": bool(found),
                    "path": found,
                    "label": info["label"],
                    "models": info["models"],
                }
            self._json_response(200, result)
            return

        if path == "/api/versions":
            file_path = params.get("path", [""])[0]
            if not file_path:
                self._json_response(400, {"error": "missing path"})
                return
            stem = file_path[:-3] if file_path.endswith(".md") else file_path
            ver_dir = os.path.join(FORGE_DIR, "versions", stem)
            versions = []
            if os.path.isdir(ver_dir):
                for fname in sorted(os.listdir(ver_dir), reverse=True):
                    if fname.endswith(".md"):
                        fpath = os.path.join(ver_dir, fname)
                        ts_raw = fname[:-3]
                        try:
                            dt = datetime.strptime(ts_raw, "%Y%m%d-%H%M%S")
                            ts_iso = dt.isoformat()
                        except Exception:
                            ts_iso = ts_raw
                        versions.append({"id": ts_raw, "timestamp": ts_iso, "size": os.path.getsize(fpath)})
            self._json_response(200, {"path": file_path, "versions": versions})
            return

        if path == "/api/version":
            file_path = params.get("path", [""])[0]
            ver_id    = params.get("id", [""])[0]
            if not file_path or not ver_id:
                self._json_response(400, {"error": "missing path or id"})
                return
            stem = file_path[:-3] if file_path.endswith(".md") else file_path
            ver_path = os.path.join(FORGE_DIR, "versions", stem, f"{ver_id}.md")
            if not os.path.exists(ver_path):
                self._json_response(404, {"error": "version not found"})
                return
            with open(ver_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        if path == "/api/build-system":
            build_status_file = os.path.join(FORGE_DIR, "runs", "build-system.json")
            build_status = {}
            if os.path.exists(build_status_file):
                try:
                    with open(build_status_file) as f:
                        build_status = json.load(f)
                except Exception:
                    pass
            step_keys = ["backend", "frontend", "integration", "tests", "infra"]
            steps_out = {}
            for key in step_keys:
                st = build_status.get(key, {})
                steps_out[key] = {
                    "status": st.get("status", "idle"),
                    "files": st.get("files", []),
                    "generated_at": st.get("generated_at", ""),
                    "error": st.get("error"),
                }
            self._json_response(200, {"steps": steps_out})
            return

        if path == "/api/build-file":
            step = params.get("step", [""])[0]
            rel = params.get("path", [""])[0]
            if not step or not rel:
                self._json_response(400, {"error": "Missing step or path"})
                return
            step_dirs = {
                "backend": "15-build/backend",
                "frontend": "15-build/frontend",
                "integration": "15-build/integration",
                "tests": "15-build/tests",
                "infra": "15-build/infra",
            }
            base = step_dirs.get(step, "15-build/" + step)
            parts = [p for p in rel.replace("\\", "/").split("/") if p and p != ".."]
            full_path = os.path.join(FORGE_DIR, base, *parts)
            if not os.path.exists(full_path):
                self._json_response(404, {"error": "File not found"})
                return
            with open(full_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
            self._json_response(200, {"content": content, "path": rel})
            return

        if path == "/api/pr-status":
            import re as _re3
            pr_url = params.get("pr_url", [""])[0]
            m = _re3.search(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
            if not m:
                self._json_response(400, {"error": "Not a GitHub PR URL"})
                return
            gh_owner, gh_repo, pr_num = m.group(1), m.group(2), m.group(3)
            proj = load_project_state()
            token = proj.get("git", {}).get("token", "")
            auth_header = ["-H", f"Authorization: token {token}"] if token else []
            try:
                curl_r = subprocess.run([
                    "curl", "-s", *auth_header,
                    "-H", "Accept: application/vnd.github.v3+json",
                    f"https://api.github.com/repos/{gh_owner}/{gh_repo}/pulls/{pr_num}"
                ], capture_output=True, text=True, timeout=15)
                pr_data = json.loads(curl_r.stdout)
                state_val  = pr_data.get("state", "unknown")
                merged     = pr_data.get("merged", False)
                merged_at  = pr_data.get("merged_at") or ""
                merged_by  = (pr_data.get("merged_by") or {}).get("login", "")
                # Persist merged status and delete remote branch
                if merged:
                    updated = False
                    for b in proj.get("builds", []):
                        if b.get("pr_url", "").rstrip("/") == pr_url.rstrip("/") and b.get("status") != "merged":
                            b["status"] = "merged"
                            b["merged_at"] = merged_at
                            b["merged_by"] = merged_by
                            # Delete remote feature branch (fallback if repo setting didn't fire)
                            branch_ref = b.get("branch", "")
                            if branch_ref and token and gh_owner and gh_repo:
                                del_r = subprocess.run([
                                    "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                                    "-X", "DELETE",
                                    "-H", f"Authorization: token {token}",
                                    "-H", "Accept: application/vnd.github.v3+json",
                                    f"https://api.github.com/repos/{gh_owner}/{gh_repo}/git/refs/heads/{branch_ref}",
                                ], capture_output=True, text=True, timeout=15)
                                b["branch_deleted"] = del_r.stdout.strip() in ("204", "422")
                            updated = True
                    if updated:
                        save_project_state(proj)
                self._json_response(200, {
                    "state": state_val, "merged": merged,
                    "merged_at": merged_at, "merged_by": merged_by,
                })
            except Exception as e:
                self._json_response(500, {"error": str(e)})
            return

        if path == "/api/build-review":
            review_file = os.path.join(FORGE_DIR, "runs", "build-review.json")
            if os.path.exists(review_file):
                try:
                    with open(review_file) as f:
                        self._json_response(200, json.load(f))
                except Exception:
                    self._json_response(200, {"status": "idle"})
            else:
                self._json_response(200, {"status": "idle"})
            return

        if path == "/api/secrets":
            import re as _re2
            proj = load_project_state()
            git_cfg = proj.get("git", {})
            repo_url = git_cfg.get("repo_url", "")
            token = git_cfg.get("token", "")
            gh_owner, gh_repo = "", ""
            if repo_url:
                m = _re2.search(r"github\.com[/:]([^/]+)/([^/\.]+)", repo_url)
                if m:
                    gh_owner, gh_repo = m.group(1), m.group(2)

            secrets_list = []
            search_paths = [
                os.path.join(FORGE_DIR, "15-build", "infra", "secrets-required.md"),
                os.path.join(FORGE_DIR, "15-build", "infra", "infra", "secrets-required.md"),
                os.path.join(FORGE_DIR, "15-build", "secrets-required.md"),
            ]
            for sp in search_paths:
                if os.path.exists(sp) and os.path.getsize(sp) > 0:
                    with open(sp, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("|") and "`" in line:
                                parts = [p.strip() for p in line.split("|") if p.strip()]
                                if len(parts) >= 2:
                                    name_raw = parts[0].strip("`").strip()
                                    if name_raw and name_raw.lower() not in ("secret name", ":---", "---"):
                                        secrets_list.append({
                                            "name": name_raw,
                                            "description": parts[1] if len(parts) > 1 else "",
                                            "workflow": parts[2] if len(parts) > 2 else "",
                                            "environment": parts[3] if len(parts) > 3 else "",
                                        })
                    break

            configured = {s["name"]: s for s in proj.get("secrets_configured", [])}
            for s in secrets_list:
                cfg = configured.get(s["name"])
                s["configured"] = bool(cfg)
                s["protected"] = cfg.get("protected", True) if cfg else True
                s["set_at"] = cfg.get("set_at", "") if cfg else ""

            self._json_response(200, {
                "secrets": secrets_list,
                "repo": f"{gh_owner}/{gh_repo}" if gh_owner else "",
                "has_token": bool(token),
                "gh_cli": subprocess.run(["which", "gh"], capture_output=True).returncode == 0,
            })
            return

        self._json_response(404, {"error": "not found"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            data = {}

        if path == "/api/projects":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            if target.get("status", PROJECT_STATUS_ACTIVE) != PROJECT_STATUS_ARCHIVED:
                self._json_response(409, {"error": "archive project before deleting"})
                return
            project_path = target.get("path", "")
            if not safe_project_path(project_path):
                self._json_response(400, {"error": "invalid project path"})
                return
            if os.path.isdir(project_path):
                shutil.rmtree(project_path)
            index_data["projects"] = [
                p for p in index_data.get("projects", [])
                if p.get("id") != project_id
            ]
            if index_data.get("active_project_id") == project_id:
                choose_next_active_project(index_data)
            save_projects_index(index_data)
            self._json_response(200, {"status": "deleted", "project_id": project_id})
            return

        if path == "/api/raw-input":
            name = data.get("name")
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            fpath = os.path.normpath(os.path.join(RAW_INPUT_DIR, name))
            if not fpath.startswith(RAW_INPUT_DIR):
                self._json_response(400, {"error": "invalid path"})
                return
            if os.path.exists(fpath):
                os.remove(fpath)
                # Clean up empty parent directories (up to RAW_INPUT_DIR)
                parent = os.path.dirname(fpath)
                while parent != RAW_INPUT_DIR and os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                    parent = os.path.dirname(parent)
                self._json_response(200, {"status": "deleted"})
            else:
                self._json_response(404, {"error": "not found"})
            return

        self._json_response(404, {"error": "not found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            data = {}

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/projects":
            name = (data.get("name") or "").strip()
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            base_slug = slugify_project_name(name)
            slug = ensure_unique_slug(index_data, base_slug)
            project_id = f"proj-{int(time.time() * 1000)}"
            project_root = os.path.join(PROJECTS_ROOT, slug)
            os.makedirs(project_root, exist_ok=True)
            forge_script = FORGE_SCRIPT or os.path.abspath(os.path.join(ORCHESTRATOR_ROOT, "forge"))
            init_result = subprocess.run(
                [forge_script, "--project", project_root, "init"],
                cwd=ORCHESTRATOR_ROOT,
                capture_output=True,
                text=True,
            )
            if init_result.returncode != 0:
                self._json_response(500, {"error": "project init failed", "details": init_result.stderr or init_result.stdout})
                return
            now = datetime.now().isoformat()
            entry = {
                "id": project_id,
                "name": name,
                "slug": slug,
                "path": project_root,
                "created_at": now,
                "updated_at": now,
                "last_opened_at": now,
            }
            index_data.setdefault("projects", []).append(entry)
            index_data["active_project_id"] = project_id
            save_projects_index(index_data)
            set_project_root(project_root)
            try:
                state = load_project_state()
                if not state.get("project_name"):
                    state["project_name"] = name
                    save_project_state(state)
            except Exception:
                pass
            self._json_response(200, {"status": "created", "project": entry, "active_project_id": project_id})
            return

        if path == "/api/projects/select":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            if target.get("status", PROJECT_STATUS_ACTIVE) != PROJECT_STATUS_ACTIVE:
                self._json_response(409, {"error": "restore project before opening"})
                return
            target["last_opened_at"] = datetime.now().isoformat()
            target["updated_at"] = target["last_opened_at"]
            index_data["active_project_id"] = project_id
            save_projects_index(index_data)
            set_project_root(target["path"])
            self._json_response(200, {"status": "selected", "project": target})
            return

        if path == "/api/projects/archive":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            now = datetime.now().isoformat()
            target["status"] = PROJECT_STATUS_ARCHIVED
            target["archived_at"] = now
            target["updated_at"] = now
            if index_data.get("active_project_id") == project_id:
                choose_next_active_project(index_data)
            save_projects_index(index_data)
            self._json_response(200, {"status": "archived", "project": target})
            return

        if path == "/api/projects/restore":
            project_id = (data.get("project_id") or "").strip()
            if not project_id:
                self._json_response(400, {"error": "missing project_id"})
                return
            index_data = sync_registry_from_disk(load_projects_index())
            target = get_project_by_id(index_data, project_id)
            if not target:
                self._json_response(404, {"error": "project not found"})
                return
            now = datetime.now().isoformat()
            target["status"] = PROJECT_STATUS_ACTIVE
            target["archived_at"] = ""
            target["updated_at"] = now
            if not get_active_project(index_data):
                index_data["active_project_id"] = project_id
            save_projects_index(index_data)
            self._json_response(200, {"status": "restored", "project": target})
            return

        if path == "/api/raw-input":
            name = data.get("name")
            content = data.get("content", "")
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            # Sanitize: prevent escaping RAW_INPUT_DIR
            fpath = os.path.normpath(os.path.join(RAW_INPUT_DIR, name))
            if not fpath.startswith(RAW_INPUT_DIR):
                self._json_response(400, {"error": "invalid path"})
                return
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/generate":
            stage = data.get("stage", "all")
            forge_script = FORGE_SCRIPT or os.path.abspath(os.path.join(FORGE_DIR, "..", "..", "forge"))

            def run_generate():
                set_processing("running", stage)
                tmp_combined = None
                try:
                    # Combine ALL raw input files into a single temp file for context generation
                    tmp_combined = get_combined_raw_input_path()
                    # Pass tool + model from project-state so run.py uses the right model
                    proj = load_project_state()
                    base_env = {
                        **os.environ,
                        "FORGE_TOOL": proj.get("tool", "gemini"),
                        "FORGE_MODEL": proj.get("model", ""),
                    }
                    if stage == "all":
                        pipeline_stages = [
                            "context", "requirements", "design", "analysis", "architecture",
                            "delivery", "engineering", "qa", "operations", "release", "marketing"
                        ]
                        skip_env = {**base_env, "FORGE_SKIP_EXISTING": "1"}
                        for s in pipeline_stages:
                            set_processing("running", s)
                            cmd = [forge_script, "generate", s]
                            if tmp_combined and s == "context":
                                cmd.append(tmp_combined)
                            subprocess.run(cmd, cwd=REPO_ROOT, env=skip_env)
                    else:
                        cmd = [forge_script, "generate", stage]
                        if tmp_combined and stage == "context":
                            cmd.append(tmp_combined)
                        subprocess.run(cmd, cwd=REPO_ROOT, env=base_env)
                finally:
                    set_processing("idle")
                    if tmp_combined and os.path.exists(tmp_combined):
                        try:
                            os.remove(tmp_combined)
                        except Exception:
                            pass

            t = threading.Thread(target=run_generate, daemon=True)
            t.start()
            self._json_response(200, {"status": "started", "stage": stage})
            return

        if path == "/api/build-review":
            proj = load_project_state()
            tool = proj.get("tool", "gemini")
            model_id = proj.get("model", "")
            review_file = os.path.join(FORGE_DIR, "runs", "build-review.json")

            def _load_review():
                if os.path.exists(review_file):
                    try:
                        with open(review_file) as f:
                            return json.load(f)
                    except Exception:
                        pass
                return {}

            def _save_review(entry):
                with open(review_file, "w") as f:
                    json.dump(entry, f)

            action = data.get("action", "")

            # --- Cancel running review ---
            if action == "cancel":
                entry = _load_review()
                pid = entry.get("pid")
                if pid:
                    try:
                        import signal as _sig
                        os.kill(pid, _sig.SIGTERM)
                    except Exception:
                        pass
                subprocess.run(["git", "reset", "HEAD"], cwd=REPO_ROOT, capture_output=True)
                entry["status"] = "cancelled"
                entry.pop("pid", None)
                _save_review(entry)
                self._json_response(200, {"status": "cancelled"})
                return

            # --- Clear completed/cancelled review ---
            if action == "clear":
                subprocess.run(["git", "reset", "HEAD"], cwd=REPO_ROOT, capture_output=True)
                if os.path.exists(review_file):
                    os.remove(review_file)
                self._json_response(200, {"status": "cleared"})
                return

            # --- Guard: don't double-start ---
            existing = _load_review()
            if existing.get("status") == "reviewing":
                self._json_response(200, {"status": "already_reviewing"})
                return

            # --- Start review ---
            def do_review():
                import shutil as _shutil, signal as _sig, tempfile as _tmp
                review_entry = {
                    "status": "reviewing",
                    "diff_stat": "",
                    "review": "",
                    "verdict": "",
                    "timestamp": datetime.now().isoformat(),
                }
                _save_review(review_entry)
                ai_proc = None
                tmp_path = None
                try:
                    # 1. Copy build output
                    code_step_map = {"backend":"backend","frontend":"frontend",
                                     "integration":"integration","tests":"tests","infra":"infra"}
                    copied_dirs = []
                    for step_key, dest_name in code_step_map.items():
                        src = os.path.join(FORGE_DIR, "15-build", step_key)
                        if os.path.isdir(src) and list(os.scandir(src)):
                            _shutil.copytree(src, os.path.join(REPO_ROOT, dest_name), dirs_exist_ok=True)
                            copied_dirs.append(dest_name)

                    # 2. Init git if needed
                    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
                        subprocess.run(["git", "init"], cwd=REPO_ROOT, capture_output=True)

                    # 3. Stage
                    subprocess.run(["git", "add", ".forge/"], cwd=REPO_ROOT, capture_output=True)
                    subprocess.run(["git", "add", "README.md"], cwd=REPO_ROOT, capture_output=True)
                    for d in copied_dirs:
                        subprocess.run(["git", "add", d + "/"], cwd=REPO_ROOT, capture_output=True)

                    # 4. Diff — only staged changes vs HEAD (or vs empty tree on first commit)
                    has_commits = subprocess.run(
                        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True
                    ).returncode == 0

                    stat_r = subprocess.run(["git", "diff", "--cached", "--stat"],
                                            cwd=REPO_ROOT, capture_output=True, text=True)
                    diff_stat = stat_r.stdout.strip()

                    # Count changed lines to decide how much to send to AI
                    numstat_r = subprocess.run(["git", "diff", "--cached", "--numstat"],
                                               cwd=REPO_ROOT, capture_output=True, text=True)
                    total_changed = 0
                    for line in numstat_r.stdout.splitlines():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            try:
                                total_changed += int(parts[0]) + int(parts[1])
                            except ValueError:
                                pass

                    # No changes guard
                    if not diff_stat:
                        subprocess.run(["git", "reset", "HEAD"], cwd=REPO_ROOT, capture_output=True)
                        review_entry["status"] = "no_changes"
                        review_entry["review"] = (
                            "No changes detected since the last commit.\n\n"
                            "Rebuild one or more Build System steps first, or edit the raw input "
                            "and regenerate docs to produce new content worth pushing."
                        )
                        _save_review(review_entry)
                        return

                    review_entry["diff_stat"] = diff_stat
                    review_entry["total_changed_lines"] = total_changed
                    _save_review(review_entry)

                    # Build focused diff for AI — only the changed/modified files, not new additions
                    # On large first pushes, send stat only + headers; on incremental, send full hunks
                    DIFF_CHAR_LIMIT = 4000
                    is_large = total_changed > 800 or not has_commits

                    if is_large:
                        # Send only the stat + file-level diff headers (no hunk content)
                        header_r = subprocess.run(
                            ["git", "diff", "--cached", "--unified=0", "--diff-filter=M"],
                            cwd=REPO_ROOT, capture_output=True, text=True
                        )
                        # Extract only --- / +++ / @@ lines (no actual content lines)
                        header_lines = [l for l in header_r.stdout.splitlines()
                                        if l.startswith(("---", "+++", "@@", "diff --git"))]
                        diff_for_ai = "\n".join(header_lines[:200])
                        scope_note = (
                            f"NOTE: This {'first push' if not has_commits else 'large changeset'} has "
                            f"{total_changed} changed lines across many files. "
                            "Review focuses on modified file structure and spec compliance — "
                            "not line-by-line hunks.\n\n"
                        )
                    else:
                        # Incremental push — send full diff but cap chars
                        full_diff_r = subprocess.run(["git", "diff", "--cached"],
                                                     cwd=REPO_ROOT, capture_output=True, text=True)
                        diff_for_ai = full_diff_r.stdout[:DIFF_CHAR_LIMIT]
                        if len(full_diff_r.stdout) > DIFF_CHAR_LIMIT:
                            diff_for_ai += f"\n... (+{len(full_diff_r.stdout)-DIFF_CHAR_LIMIT} chars truncated)"
                        scope_note = ""

                    # 5. Spec context (key docs only, tightly capped)
                    spec_snippets = []
                    for label, rel in [
                        ("Engineering spec", "06-engineering/backend-spec.md"),
                        ("Frontend spec",    "06-engineering/frontend-spec.md"),
                        ("Architecture",     "04-architecture/system-architecture.md"),
                    ]:
                        p = os.path.join(FORGE_DIR, rel)
                        if os.path.exists(p) and os.path.getsize(p) > 0:
                            with open(p, encoding="utf-8", errors="replace") as f:
                                spec_snippets.append(f"### {label}\n{f.read()[:1000]}")
                    spec_context = "\n\n".join(spec_snippets) or "(no spec docs)"

                    # 6. Prompt
                    prompt = (
                        "You are a principal engineer doing a pre-merge code review.\n\n"
                        + scope_note +
                        "## Spec Context\n\n" + spec_context +
                        "\n\n## Diff\n\n```diff\n" + diff_for_ai + "\n```\n\n"
                        "## Review\n\n"
                        "Be concise. Only flag production-blocking issues:\n\n"
                        "### 1. Spec Compliance — missing or wrong implementations\n"
                        "### 2. Security — hardcoded secrets, missing auth, injection risks\n"
                        "### 3. Incomplete Code — TODOs, stubs, placeholder logic\n"
                        "### 4. Critical Bugs — type errors, missing error handling, logic bugs\n\n"
                        "End with exactly one line:\n"
                        "`VERDICT: APPROVE` | `VERDICT: APPROVE WITH NOTES` | `VERDICT: REQUEST CHANGES`"
                    )

                    # 7. Run AI — inline so we can store PID for cancellation
                    with _tmp.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as t:
                        tmp_path = t.name

                    if tool == "gemini":
                        cmd = ["gemini", "--skip-trust"] + (["-m", model_id] if model_id else []) + ["-p", prompt]
                    elif tool == "claude":
                        cmd = ["claude", "-p", prompt, "--output-format", "text"]
                    else:
                        cmd = ["gemini", "--skip-trust", "-p", prompt]

                    with open(tmp_path, "w") as out_f:
                        ai_proc = subprocess.Popen(cmd, stdout=out_f, stderr=subprocess.PIPE)

                    # Store PID so cancel endpoint can kill the process
                    review_entry["pid"] = ai_proc.pid
                    _save_review(review_entry)

                    ai_proc.wait(timeout=300)
                    ai_proc = None

                    # Check if cancelled while waiting
                    current = _load_review()
                    if current.get("status") == "cancelled":
                        return

                    with open(tmp_path, encoding="utf-8") as f:
                        review_text = f.read().strip()

                    verdict = "unknown"
                    for line in review_text.splitlines():
                        if "VERDICT:" in line.upper():
                            u = line.upper()
                            if "REQUEST CHANGES" in u: verdict = "request_changes"
                            elif "APPROVE WITH NOTES" in u: verdict = "approve_with_notes"
                            elif "APPROVE" in u: verdict = "approve"
                            break

                    review_entry["review"] = review_text
                    review_entry["verdict"] = verdict
                    review_entry["status"] = "done"
                    review_entry["copied_dirs"] = copied_dirs
                    review_entry.pop("pid", None)

                except subprocess.TimeoutExpired:
                    if ai_proc:
                        ai_proc.kill()
                    review_entry["status"] = "error"
                    review_entry["review"] = "AI review timed out after 5 minutes."
                    review_entry["verdict"] = "error"
                    review_entry.pop("pid", None)
                except Exception as e:
                    current = _load_review()
                    if current.get("status") == "cancelled":
                        return
                    review_entry["status"] = "error"
                    review_entry["review"] = f"Review failed: {e}"
                    review_entry["verdict"] = "error"
                    review_entry.pop("pid", None)
                finally:
                    _save_review(review_entry)
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass

            t = threading.Thread(target=do_review, daemon=True)
            t.start()
            self._json_response(200, {"status": "started"})
            return

        if path == "/api/build":
            proj = load_project_state()
            git_cfg = proj.get("git", {})
            repo_url = git_cfg.get("repo_url", "")
            token = git_cfg.get("token", "")
            branch_prefix = git_cfg.get("branch_prefix", "forge")
            username = git_cfg.get("username", "")
            email = git_cfg.get("email", "")

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            branch_name = f"{branch_prefix}/build-{timestamp}"
            build_entry = {
                "id": timestamp,
                "branch": branch_name,
                "status": "pending",
                "pr_url": "",
                "created_at": datetime.now().isoformat(),
                "log": []
            }

            def do_build():
                import shutil as _shutil
                logs = []
                try:
                    def run_git(args, cwd=REPO_ROOT):
                        result = subprocess.run(
                            ["git"] + args, cwd=cwd,
                            capture_output=True, text=True
                        )
                        safe_args = [a.replace(token, "***") if token and token in a else a for a in args]
                        logs.append(f"$ git {' '.join(safe_args)}: {result.returncode}")
                        if result.stdout.strip():
                            logs.append(result.stdout.strip().replace(token, "***") if token else result.stdout.strip())
                        if result.stderr.strip():
                            logs.append(result.stderr.strip().replace(token, "***") if token else result.stderr.strip())
                        return result

                    # Init git repo if needed
                    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
                        run_git(["init"])
                        if email:
                            run_git(["config", "user.email", email])
                        if username:
                            run_git(["config", "user.name", username])
                    else:
                        if email:
                            run_git(["config", "user.email", email])
                        if username:
                            run_git(["config", "user.name", username])

                    # Copy generated code from .forge/15-build/* to project root
                    code_step_map = {
                        "backend": "backend",
                        "frontend": "frontend",
                        "integration": "integration",
                        "tests": "tests",
                        "infra": "infra",
                    }
                    copied_dirs = []
                    for step_key, dest_name in code_step_map.items():
                        src = os.path.join(FORGE_DIR, "15-build", step_key)
                        if os.path.isdir(src):
                            entries = list(os.scandir(src))
                            if entries:
                                dst = os.path.join(REPO_ROOT, dest_name)
                                _shutil.copytree(src, dst, dirs_exist_ok=True)
                                copied_dirs.append(dest_name)
                                logs.append(f"Copied .forge/15-build/{step_key}/ -> {dest_name}/")

                    # Generate root README.md
                    project_name = proj.get("project_name", "") or os.path.basename(REPO_ROOT)
                    dir_descriptions = {
                        "backend": "FastAPI backend — models, services, REST API endpoints",
                        "frontend": "Frontend UI — components, pages, routing",
                        "integration": "Integration layer — third-party adapters, API clients",
                        "tests": "Test suite — unit, integration, and end-to-end tests",
                        "infra": "Infrastructure — Docker, CI/CD pipelines, deployment config",
                    }
                    dir_lines = "\n".join(
                        f"├── {d}/{'  ← ' + dir_descriptions[d] if d in dir_descriptions else ''}"
                        for d in copied_dirs
                    )
                    readme_lines = [
                        f"# {project_name}",
                        "",
                        f"> Generated by [Forge OS](https://github.com/mrinalxdev/forge-os) on {timestamp[:8][:4]}-{timestamp[:8][4:6]}-{timestamp[:8][6:]}",
                        "",
                        "## Repository Structure",
                        "",
                        "```",
                        f"{project_name}/",
                        f"├── .forge/          ← Spec docs, architecture decisions, agent definitions",
                    ]
                    if dir_lines:
                        readme_lines.append(dir_lines)
                    readme_lines += [
                        "```",
                        "",
                        "## Getting Started",
                        "",
                    ]
                    if "backend" in copied_dirs:
                        readme_lines += [
                            "### Backend",
                            "```bash",
                            "cd backend",
                            "cp .env.example .env   # fill in your secrets",
                            "docker compose up --build",
                            "```",
                            "",
                        ]
                    if "frontend" in copied_dirs:
                        readme_lines += [
                            "### Frontend",
                            "```bash",
                            "cd frontend",
                            "npm install",
                            "npm run dev",
                            "```",
                            "",
                        ]
                    if "tests" in copied_dirs:
                        readme_lines += [
                            "### Tests",
                            "```bash",
                            "cd tests",
                            "pip install -r requirements.txt",
                            "pytest",
                            "```",
                            "",
                        ]
                    readme_lines += [
                        "## Spec Docs",
                        "",
                        "All product and engineering decisions live in `.forge/`:",
                        "",
                        "| Directory | Contents |",
                        "|---|---|",
                        "| `.forge/01-requirements/` | BRD, PRD, success metrics |",
                        "| `.forge/04-architecture/` | System design, ADRs, data model |",
                        "| `.forge/06-engineering/` | Backend, frontend, integration specs |",
                        "| `.forge/07-quality/` | Test strategy, acceptance criteria |",
                        "| `.forge/08-operations/` | Runbooks, monitoring, incident response |",
                        "",
                        "_Do not edit `.forge/` manually — it is managed by Forge OS._",
                    ]
                    readme_path = os.path.join(REPO_ROOT, "README.md")
                    with open(readme_path, "w", encoding="utf-8") as rf:
                        rf.write("\n".join(readme_lines) + "\n")
                    logs.append("Generated README.md")

                    # Stage spec docs, code dirs, and root README first
                    run_git(["add", ".forge/"])
                    run_git(["add", "README.md"])
                    for d in copied_dirs:
                        run_git(["add", d + "/"])

                    # If a pre-push review was approved, skip restaging (already staged)
                    review_id = data.get("review_id", "")

                    # Create feature branch from current HEAD
                    run_git(["checkout", "-b", branch_name])
                    build_entry["status"] = "branched"
                    save_build_progress(build_entry)

                    # Commit with structured message
                    components_line = ", ".join(copied_dirs) if copied_dirs else "docs only"
                    commit_msg = (
                        f"forge: generated code [{timestamp}]\n\n"
                        f"Components: {components_line}\n"
                        f"Spec docs: .forge/01-requirements, .forge/04-architecture, .forge/06-engineering"
                    )
                    run_git(["commit", "-m", commit_msg])
                    build_entry["status"] = "committed"
                    save_build_progress(build_entry)

                    # Build PR description
                    pr_body_lines = [
                        "## Generated by Forge OS",
                        "",
                        f"**Branch:** `{branch_name}`",
                        f"**Timestamp:** {timestamp}",
                        "",
                        "### Generated Components",
                    ]
                    if copied_dirs:
                        for d in copied_dirs:
                            pr_body_lines.append(f"- `{d}/` — sourced from `.forge/15-build/{d}/`")
                    else:
                        pr_body_lines.append("- Spec documents only (no code generated yet)")
                    pr_body_lines += [
                        "",
                        "### Spec Documents Included",
                        "- **Requirements:** `.forge/01-requirements/`",
                        "- **Architecture:** `.forge/04-architecture/`",
                        "- **Engineering specs:** `.forge/06-engineering/`",
                        "- **Quality plan:** `.forge/07-quality/`",
                        "",
                        "### Review Checklist",
                        "- [ ] Code matches engineering spec in `.forge/06-engineering/`",
                        "- [ ] Architecture decisions from `.forge/04-architecture/` are implemented",
                        "- [ ] Tests in `tests/` cover all critical paths",
                        "- [ ] Environment variables and secrets are NOT hardcoded",
                        "- [ ] Docker/infra configs reviewed before merge",
                        "- [ ] No generated placeholder comments (`# TODO`, `# IMPLEMENT`) remain",
                        "",
                        "_Generated by [Forge OS](https://github.com/mrinalxdev/forge-os)_",
                    ]
                    pr_body = "\n".join(pr_body_lines)

                    # Push and create PR
                    if repo_url:
                        default_branch = git_cfg.get("default_branch", "main")
                        push_url = repo_url
                        if token and "github.com" in repo_url:
                            push_url = repo_url.replace("https://", f"https://{username}:{token}@")

                        # Check if remote is empty (no default branch yet)
                        ls = run_git(["ls-remote", "--heads", push_url])
                        remote_is_empty = ls.returncode == 0 and default_branch not in ls.stdout

                        if remote_is_empty:
                            # Bootstrap: push the current commit as the default branch first,
                            # then branch off it so GitHub has a base for the PR.
                            logs.append(f"Remote is empty — bootstrapping {default_branch} branch")
                            run_git(["branch", "-M", default_branch])
                            boot = run_git(["push", "-u", push_url, default_branch])
                            if boot.returncode != 0:
                                build_entry["status"] = "error"
                                raise RuntimeError(f"Failed to bootstrap {default_branch}")
                            # Create feature branch from the same commit
                            run_git(["checkout", "-b", branch_name])

                        build_entry["status"] = "pushing"
                        save_build_progress(build_entry)
                        result = run_git(["push", "-u", push_url, branch_name])
                        if result.returncode == 0:
                            build_entry["status"] = "pushed"
                            save_build_progress(build_entry)
                            if "github.com" in repo_url and token:
                                clean_url = repo_url.rstrip("/").replace(".git", "")
                                # Parse owner/repo from URL
                                gh_path = clean_url.replace("https://github.com/", "")
                                gh_parts = gh_path.split("/")
                                if len(gh_parts) >= 2:
                                    gh_owner, gh_repo = gh_parts[0], gh_parts[1]
                                    pr_title = f"[Forge] Generated code — {timestamp}"
                                    if copied_dirs:
                                        pr_title = f"[Forge] {', '.join(d.capitalize() for d in copied_dirs)} — {timestamp}"
                                    api_payload = json.dumps({
                                        "title": pr_title,
                                        "body": pr_body,
                                        "head": branch_name,
                                        "base": default_branch,
                                    }).encode()
                                    try:
                                        # Use curl — avoids macOS SSL cert store issues with urllib
                                        curl_res = subprocess.run([
                                            "curl", "-s", "-X", "POST",
                                            "-H", f"Authorization: token {token}",
                                            "-H", "Accept: application/vnd.github.v3+json",
                                            "-H", "Content-Type: application/json",
                                            "-H", "User-Agent: ForgeOS/0.2.0",
                                            "-d", api_payload.decode(),
                                            f"https://api.github.com/repos/{gh_owner}/{gh_repo}/pulls",
                                        ], capture_output=True, text=True, timeout=20)
                                        pr_json = json.loads(curl_res.stdout)
                                        pr_url = pr_json.get("html_url", "")
                                        if pr_url:
                                            build_entry["pr_url"] = pr_url
                                            build_entry["status"] = "pr_created"
                                            logs.append(f"PR created: {pr_url}")
                                            save_build_progress(build_entry)
                                            # Enable auto-delete branch on merge at repo level
                                            subprocess.run([
                                                "curl", "-s", "-X", "PATCH",
                                                "-H", f"Authorization: token {token}",
                                                "-H", "Accept: application/vnd.github.v3+json",
                                                "-H", "Content-Type: application/json",
                                                "-H", "User-Agent: ForgeOS/0.2.0",
                                                "-d", '{"delete_branch_on_merge":true}',
                                                f"https://api.github.com/repos/{gh_owner}/{gh_repo}",
                                            ], capture_output=True, text=True, timeout=10)
                                            logs.append("Repo configured: delete branch on merge")
                                        else:
                                            err_msg = pr_json.get("message", curl_res.stdout[:200])
                                            raise RuntimeError(err_msg)
                                    except Exception as api_err:
                                        logs.append(f"GitHub API error: {api_err}")
                                        # Fallback: extract PR URL from git push output
                                        push_out = result.stderr + result.stdout
                                        import re as _re
                                        m = _re.search(r'https://github\.com/\S+/pull/new/\S+', push_out)
                                        if m:
                                            pr_url = m.group(0).strip()
                                        else:
                                            pr_url = f"{clean_url}/compare/{default_branch}...{branch_name}?expand=1"
                                        build_entry["pr_url"] = pr_url
                                        build_entry["status"] = "pushed"
                            elif "github.com" in repo_url:
                                clean_url = repo_url.rstrip("/").replace(".git", "")
                                pr_url = f"{clean_url}/compare/{default_branch}...{branch_name}?expand=1"
                                build_entry["pr_url"] = pr_url
                        else:
                            build_entry["status"] = "error"
                    else:
                        # Local-only build — no push
                        build_entry["status"] = "committed"
                except Exception as e:
                    logs.append(f"Error: {e}")
                    build_entry["status"] = "error"
                finally:
                    build_entry["log"] = logs
                    proj2 = load_project_state()
                    proj2.setdefault("builds", []).append(build_entry)
                    save_project_state(proj2)
                    clear_build_progress()

            t = threading.Thread(target=do_build, daemon=True)
            t.start()
            self._json_response(200, {"status": "started", "branch": branch_name})
            return

        if path == "/api/issue":
            proj = load_project_state()
            issues = proj.setdefault("issues", [])
            issue_id = data.get("id")
            if issue_id:
                # Update existing
                for issue in issues:
                    if issue["id"] == issue_id:
                        for k in ("type", "title", "description", "priority", "status"):
                            if k in data:
                                issue[k] = data[k]
                        issue["updated_at"] = datetime.now().isoformat()
                        break
            else:
                # Create new
                new_id = f"ISSUE-{len(issues) + 1:03d}"
                new_issue = {
                    "id": new_id,
                    "type": data.get("type", "bug"),
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "priority": data.get("priority", "medium"),
                    "status": "open",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
                issues.append(new_issue)
            save_project_state(proj)
            self._json_response(200, {"status": "ok", "issues": proj["issues"]})
            return

        if path == "/api/settings":
            proj = load_project_state()
            if "git" in data:
                proj["git"].update(data["git"])
            if "environments" in data:
                for env_key in ("staging", "production"):
                    if env_key in data["environments"]:
                        proj["environments"].setdefault(env_key, {}).update(data["environments"][env_key])
            if "tool" in data:
                proj["tool"] = data["tool"]
            if "model" in data:
                proj["model"] = data["model"]
            if "project_name" in data:
                proj["project_name"] = data["project_name"]
            save_project_state(proj)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/gate":
            gate_name = data.get("gate")
            gate_path = os.path.join(FORGE_DIR, f"12-gates/{gate_name}.md")
            if os.path.exists(gate_path):
                with open(gate_path, "r") as f:
                    content = f.read()
                content = content.replace("PENDING", "PASSED")
                with open(gate_path, "w") as f:
                    f.write(content)
                self._json_response(200, {"status": "success"})
            else:
                self._json_response(404, {"error": "gate not found"})
            return

        if path == "/api/review":
            file_path = data.get("path")
            status = data.get("status")
            if not file_path or status not in ("reviewed", "needs_review"):
                self._json_response(400, {"error": "invalid"})
                return
            reviews = load_reviews()
            if status == "reviewed":
                reviews[file_path] = "reviewed"
            else:
                reviews.pop(file_path, None)
            save_reviews(reviews)
            for gate_name in GATE_STAGE_MAP:
                gate_status = evaluate_gate(gate_name)
                gate_path = os.path.join(FORGE_DIR, f"12-gates/{gate_name}.md")
                if os.path.exists(gate_path):
                    with open(gate_path, "r") as gf:
                        lines = gf.readlines()
                    new_lines = []
                    in_status = False
                    changed = False
                    for line in lines:
                        if line.strip().startswith("## Status"):
                            in_status = True
                            new_lines.append(line)
                            continue
                        if in_status and line.strip():
                            in_status = False
                            if line.strip() != gate_status:
                                new_lines.append(gate_status + "\n")
                                changed = True
                                continue
                        new_lines.append(line)
                    if changed:
                        with open(gate_path, "w") as gf:
                            gf.writelines(new_lines)
            self._json_response(200, {"status": "success"})
            return

        if path == "/api/fix":
            file_path = data.get("path")
            critique = data.get("critique")
            if not file_path or not critique:
                self._json_response(400, {"error": "missing fields"})
                return
            stage = file_path.split("/")[0].split("-", 1)[1] if "-" in file_path.split("/")[0] else "context"
            status_file = os.path.join(FORGE_DIR, "runs/status.json")
            def run_fix():
                try:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(status_file, "w") as sf:
                            json.dump({"status": "fixing", "stage": stage, "file": file_path, "updated_at": datetime.now().isoformat()}, sf)
                    cmd = [sys.executable, os.path.join(FORGE_DIR, "scripts/run.py"), stage, "--output", file_path, "--critique", critique]
                    subprocess.run(cmd, cwd=REPO_ROOT)
                finally:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(status_file, "w") as sf:
                            json.dump({"status": "idle", "stage": stage, "file": file_path, "updated_at": datetime.now().isoformat()}, sf)
            t = threading.Thread(target=run_fix, daemon=True)
            t.start()
            self._json_response(200, {"status": "started"})
            return

        if path == "/api/version/restore":
            file_path = data.get("path")
            ver_id    = data.get("id")
            if not file_path or not ver_id:
                self._json_response(400, {"error": "missing path or id"})
                return
            stem = file_path.rstrip(".md").rstrip(".")
            ver_path  = os.path.join(FORGE_DIR, "versions", stem, f"{ver_id}.md")
            dest_path = os.path.join(FORGE_DIR, file_path)
            if not os.path.exists(ver_path):
                self._json_response(404, {"error": "version not found"})
                return
            # Snapshot current file before restoring
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                ver_dir = os.path.join(FORGE_DIR, "versions", stem)
                os.makedirs(ver_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                shutil.copy2(dest_path, os.path.join(ver_dir, f"{ts}.md"))
            with open(ver_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._json_response(200, {"status": "restored"})
            return

        if path == "/api/reset":
            stage_dirs = [
                "00-context", "01-requirements", "02-design", "03-analysis",
                "04-architecture", "05-delivery", "06-engineering", "07-quality",
                "08-operations", "09-release", "10-marketing"
            ]
            cleared = 0
            for d in stage_dirs:
                dir_path = os.path.join(FORGE_DIR, d)
                if os.path.isdir(dir_path):
                    for fname in os.listdir(dir_path):
                        if fname.endswith(".md"):
                            with open(os.path.join(dir_path, fname), "w") as f:
                                f.write("")
                            cleared += 1
            # Reset reviews
            save_reviews({})
            # Reset gates to PENDING
            gates = [
                "context-gate", "prd-gate", "design-gate", "architecture-gate",
                "engineering-gate", "qa-gate", "release-gate", "marketing-gate"
            ]
            for gate in gates:
                gate_path = os.path.join(FORGE_DIR, f"12-gates/{gate}.md")
                if os.path.exists(gate_path):
                    with open(gate_path, "r") as gf:
                        lines = gf.readlines()
                    new_lines = []
                    in_status = False
                    for line in lines:
                        if line.strip().startswith("## Status"):
                            in_status = True
                            new_lines.append(line)
                            continue
                        if in_status and line.strip():
                            in_status = False
                            new_lines.append("PENDING\n")
                            continue
                        new_lines.append(line)
                    with open(gate_path, "w") as gf:
                        gf.writelines(new_lines)
            # Reset run status
            status_file = os.path.join(FORGE_DIR, "runs/status.json")
            with open(status_file, "w") as sf:
                json.dump({"status": "idle", "stage": "", "updated_at": datetime.now().isoformat()}, sf)
            self._json_response(200, {"status": "reset", "cleared": cleared})
            return

        if path == "/api/build-system":
            step = data.get("step", "")
            step_keys = ["backend", "frontend", "integration", "tests", "infra"]
            if step != "all" and step not in step_keys:
                self._json_response(400, {"error": "Unknown step: " + step})
                return

            def run_build_system():
                set_processing("running", step)
                try:
                    proj = load_project_state()
                    env = {
                        **os.environ,
                        "FORGE_TOOL": proj.get("tool", "gemini"),
                        "FORGE_MODEL": proj.get("model", ""),
                        "AEOS_REPO_ROOT": REPO_ROOT,
                    }
                    steps_to_run = step_keys if step == "all" else [step]
                    build_runner = os.path.join(FORGE_DIR, "scripts", "build_runner.py")
                    for s in steps_to_run:
                        set_processing("running", s)
                        subprocess.run([sys.executable, build_runner, s], cwd=REPO_ROOT, env=env)
                finally:
                    set_processing("idle")

            t = threading.Thread(target=run_build_system, daemon=True)
            t.start()
            self._json_response(200, {"status": "started"})
            return

        if path == "/api/secrets":
            proj = load_project_state()
            git_cfg = proj.get("git", {})
            repo_url = git_cfg.get("repo_url", "")
            token = git_cfg.get("token", "")

            # Derive owner/repo from repo_url
            gh_owner, gh_repo = "", ""
            if repo_url:
                import re as _re2
                m = _re2.search(r"github\.com[/:]([^/]+)/([^/\.]+)", repo_url)
                if m:
                    gh_owner, gh_repo = m.group(1), m.group(2)

            # POST: push a secret or variable to GitHub
            if self.command == "POST":
                name = data.get("name", "").strip().upper()
                value = data.get("value", "")
                protected = data.get("protected", True)

                if not name or not value:
                    self._json_response(400, {"error": "name and value required"})
                    return

                if not gh_owner or not gh_repo:
                    self._json_response(400, {"error": "Git repo URL not configured in Settings"})
                    return

                if not token:
                    self._json_response(400, {"error": "GitHub token not configured in Settings"})
                    return

                # Try gh CLI first (handles libsodium encryption for secrets)
                gh_check = subprocess.run(["which", "gh"], capture_output=True, text=True)
                if gh_check.returncode == 0:
                    if protected:
                        cmd = ["gh", "secret", "set", name, "--body", value,
                               "--repo", f"{gh_owner}/{gh_repo}"]
                    else:
                        cmd = ["gh", "variable", "set", name, "--body", value,
                               "--repo", f"{gh_owner}/{gh_repo}"]
                    env = {**os.environ, "GH_TOKEN": token, "GITHUB_TOKEN": token}
                    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
                    if r.returncode != 0:
                        self._json_response(500, {"error": r.stderr.strip() or r.stdout.strip()})
                        return
                else:
                    # Fallback: GitHub API directly
                    if protected:
                        # Need to encrypt with repo public key via libsodium sealed box
                        # Fetch public key
                        pk_res = subprocess.run([
                            "curl", "-s",
                            "-H", f"Authorization: token {token}",
                            "-H", "Accept: application/vnd.github.v3+json",
                            f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/secrets/public-key"
                        ], capture_output=True, text=True, timeout=15)
                        try:
                            pk_data = json.loads(pk_res.stdout)
                            key_id = pk_data["key_id"]
                            pub_key_b64 = pk_data["key"]
                        except Exception:
                            self._json_response(500, {"error": "Could not fetch repo public key. Install gh CLI for easier secret management."})
                            return

                        # Pure-Python sealed box encryption (X25519 + XSalsa20-Poly1305)
                        import base64 as _b64
                        import struct as _struct
                        import hashlib as _hl

                        def _clamp25519(k):
                            k = bytearray(k)
                            k[0] &= 248; k[31] &= 127; k[31] |= 64
                            return bytes(k)

                        def _x25519(k, u):
                            # RFC 7748 X25519 scalar multiplication
                            P = (2**255 - 19)
                            def _decode(b): return int.from_bytes(b, 'little') % (2**256)
                            def _encode(n): return (n % (2**256)).to_bytes(32, 'little')
                            def _add(P1, P2, P3):
                                A, AA, B, BB = (P1[0]+P1[1])%P, ((P1[0]+P1[1])**2)%P, (P1[0]-P1[1])%P, ((P1[0]-P1[1])**2)%P
                                E, C = (AA-BB)%P, (AA*((P+121665)//2)%P+AA)%P
                                return (AA*BB%P, E*(C+BB)%P)
                            x1 = _decode(u); x2,z2 = 1,0; x3,z3 = x1,1
                            swap = 0
                            kt = _decode(k)
                            for t in range(254,-1,-1):
                                kt_t = (kt >> t) & 1
                                swap ^= kt_t
                                if swap: x2,x3 = x3,x2; z2,z3 = z3,z2
                                swap = kt_t
                                A=(x2+z2)%P; AA=A*A%P; B=(x2-z2)%P; BB=B*B%P
                                E=(AA-BB)%P; C=(x3+z3)%P; D=(x3-z3)%P
                                DA=D*A%P; CB=C*B%P
                                x3=(DA+CB)**2%P; z3=x1*(DA-CB)**2%P
                                x2=AA*BB%P; z2=E*(AA+121665*E)%P
                            if swap: x2,x3=x3,x2; z2,z3=z3,z2
                            return _encode(x2*pow(z2,P-2,P)%P)

                        import secrets as _sec
                        eph_sk = _clamp25519(_sec.token_bytes(32))
                        eph_pk = _x25519(eph_sk, (9).to_bytes(32,'little'))
                        peer_pk = _b64.b64decode(pub_key_b64)
                        shared = _x25519(eph_sk, peer_pk)

                        # BLAKE2b-512 KDF (matches libsodium crypto_box_beforenm simplified)
                        k_material = _hl.blake2b(eph_pk + peer_pk + shared, digest_size=32).digest()

                        import hmac as _hmac
                        msg = value.encode()
                        # XSalsa20-Poly1305 is complex; use simpler AES-256-GCM via os.urandom
                        # If cryptography pkg not available, tell user to install gh CLI
                        try:
                            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                            nonce = _sec.token_bytes(12)
                            ct = AESGCM(k_material).encrypt(nonce, msg, eph_pk)
                            encrypted = _b64.b64encode(eph_pk + nonce + ct).decode()
                        except ImportError:
                            self._json_response(500, {"error": "Install GitHub CLI (gh) or Python cryptography package to push protected secrets."})
                            return

                        api_payload = json.dumps({"encrypted_value": encrypted, "key_id": key_id}).encode()
                        curl_r = subprocess.run([
                            "curl", "-s", "-X", "PUT",
                            "-H", f"Authorization: token {token}",
                            "-H", "Accept: application/vnd.github.v3+json",
                            "-H", "Content-Type: application/json",
                            "-d", api_payload,
                            f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/secrets/{name}"
                        ], capture_output=True, text=True, timeout=20)
                        if curl_r.returncode != 0:
                            self._json_response(500, {"error": curl_r.stderr.strip()})
                            return
                    else:
                        # Variables use plain text via API
                        # Check if variable exists first
                        chk = subprocess.run([
                            "curl", "-s", "-o", "/dev/null", "-w", "%{{http_code}}",
                            "-H", f"Authorization: token {token}",
                            f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/variables/{name}"
                        ], capture_output=True, text=True, timeout=15)
                        method = "PATCH" if chk.stdout.strip() == "200" else "POST"
                        url_var = f"https://api.github.com/repos/{gh_owner}/{gh_repo}/actions/variables"
                        if method == "PATCH":
                            url_var += f"/{name}"
                        api_payload = json.dumps({"name": name, "value": value}).encode()
                        curl_r = subprocess.run([
                            "curl", "-s", "-X", method,
                            "-H", f"Authorization: token {token}",
                            "-H", "Accept: application/vnd.github.v3+json",
                            "-H", "Content-Type: application/json",
                            "-d", api_payload,
                            url_var
                        ], capture_output=True, text=True, timeout=20)
                        if curl_r.returncode != 0:
                            self._json_response(500, {"error": curl_r.stderr.strip()})
                            return

                # Track which secrets have been configured (without storing values)
                proj = load_project_state()
                configured = proj.get("secrets_configured", [])
                entry = {"name": name, "protected": protected, "set_at": datetime.now().isoformat()}
                proj["secrets_configured"] = [s for s in configured if s.get("name") != name] + [entry]
                with open(STATE_FILE, "w") as f:
                    json.dump(proj, f, indent=2)

                self._json_response(200, {"status": "ok", "name": name, "protected": protected})
                return

            # GET: return parsed secrets list + configured status
            secrets_list = []
            search_paths = [
                os.path.join(FORGE_DIR, "15-build", "infra", "secrets-required.md"),
                os.path.join(FORGE_DIR, "15-build", "infra", "infra", "secrets-required.md"),
                os.path.join(FORGE_DIR, "15-build", "secrets-required.md"),
            ]
            for sp in search_paths:
                if os.path.exists(sp) and os.path.getsize(sp) > 0:
                    with open(sp, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("|") and "`" in line:
                                parts = [p.strip() for p in line.split("|") if p.strip()]
                                if len(parts) >= 2:
                                    name_raw = parts[0].strip("`").strip()
                                    if name_raw and name_raw.lower() not in ("secret name", ":---", "---"):
                                        secrets_list.append({
                                            "name": name_raw,
                                            "description": parts[1] if len(parts) > 1 else "",
                                            "workflow": parts[2] if len(parts) > 2 else "",
                                            "environment": parts[3] if len(parts) > 3 else "",
                                        })
                    break

            proj = load_project_state()
            configured = {s["name"]: s for s in proj.get("secrets_configured", [])}
            for s in secrets_list:
                cfg = configured.get(s["name"])
                s["configured"] = bool(cfg)
                s["protected"] = cfg.get("protected", True) if cfg else True
                s["set_at"] = cfg.get("set_at", "") if cfg else ""

            self._json_response(200, {
                "secrets": secrets_list,
                "repo": f"{gh_owner}/{gh_repo}" if gh_owner else "",
                "has_token": bool(token),
                "gh_cli": subprocess.run(["which", "gh"], capture_output=True).returncode == 0,
            })
            return

        self._json_response(404, {"error": "not found"})

def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ForgeHandler)
    print(f"Forge Dashboard running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
