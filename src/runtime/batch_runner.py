#!/usr/bin/env python3
'''Batch document generator — produces ALL of a stage's files in ONE AI call.

The per-file generator (run.py) re-sends the full upstream context for every
file in a stage. For the heavy mid-pipeline stages that context is large, so a
4-file stage pays for it 4x. This runner sends the shared context ONCE and asks
the model to emit every file in a single response (=== path === blocks), the
same pattern the code generator already uses.

Opt-in via FORGE_STAGE_BATCH=1. stage_runner calls this first and falls back to
the proven per-file path if it exits non-zero (incomplete or failed batch), so
it can never regress generation.

Usage: python3 scripts/batch_runner.py <stage> <file1> <file2> ... [--raw-input X]
Exit:  0 = all files written (or all cached); 2 = bad args; 3 = fall back to per-file
'''
import os
import sys
import json
import hashlib
from datetime import datetime

# Reuse the build generator's battle-tested AI invocation (robust --model,
# rate-limit-safe `claude -p -`, codex/gemini/openai/agy), its === path ===
# parser, the fence stripper, and the token estimator. No duplication.
import build_runner

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get("FORGE_REPO_ROOT", os.path.dirname(os.path.dirname(SCRIPT_DIR)))
_forge_data = os.environ.get("FORGE_DATA_DIR")
FORGE_DIR = os.path.expanduser(_forge_data) if _forge_data else os.path.dirname(SCRIPT_DIR)
AGENTS_DIR = os.path.join(FORGE_DIR, "11-agents")
GEN_CACHE = os.path.join(FORGE_DIR, "runs", "generate-cache.json")

# Injected at build time from src/data/stage_pipeline.json (same source run.py uses).
STAGE_INPUTS = {}  # __FORGE_STAGE_INPUTS__
STAGE_AGENTS = {}  # __FORGE_STAGE_AGENTS__

_LOG = "[BATCH-RUNNER]"


def log(msg):
    print(_LOG + " " + msg, flush=True)


def resolve_inputs(stage, raw_input):
    """The stage's upstream context files (same resolution as run.py)."""
    inputs = []
    if stage == "context":
        if raw_input and os.path.exists(raw_input):
            inputs.append(os.path.abspath(raw_input))
        elif os.path.exists(os.path.join(REPO_ROOT, "raw-input.md")):
            inputs.append(os.path.join(REPO_ROOT, "raw-input.md"))
        return inputs
    for d in STAGE_INPUTS.get(stage, []):
        dir_path = os.path.join(FORGE_DIR, d)
        if os.path.isdir(dir_path):
            for root, _dirs, files in os.walk(dir_path):
                for f in sorted(files):
                    if f.endswith(".md"):
                        inputs.append(os.path.join(root, f))
    return inputs


def load_agent_contract(stage):
    agent = STAGE_AGENTS.get(stage, "")
    path = os.path.join(AGENTS_DIR, agent + ".md")
    if agent and os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""


def build_batch_prompt(stage, output_files, inputs):
    """One prompt that produces every file in the stage. Context sent once."""
    agent_contract = load_agent_contract(stage)
    context = ""
    for fp in inputs:
        rel = os.path.relpath(fp, FORGE_DIR)
        with open(fp, encoding="utf-8", errors="replace") as f:
            context += ("\n--- START OF " + rel + " ---\n\n" + f.read()
                        + "\n--- END OF " + rel + " ---\n")
    file_list = "\n".join("- " + f for f in output_files)
    return (
        "You are generating MULTIPLE documents for this stage in a single pass.\n"
        "CRITICAL SYSTEM INSTRUCTION: DO NOT USE ANY TOOLS. DO NOT READ OR WRITE FILES. "
        "Print raw markdown directly to stdout.\n\n"
        "=== AGENT CONTRACT ===\n" + agent_contract + "\n\n"
        "=== PROVIDED CONTEXT ===\n" + context + "\n\n---\n\n"
        "INSTRUCTIONS:\n"
        "Produce the COMPLETE markdown for EACH of the files listed below. Immediately "
        "before each file, output a marker line on its own line of EXACTLY this form:\n"
        "=== relative/path/to/file.md ===\n"
        "then that file's full markdown content, then the marker for the next file, and "
        "so on. Use the exact relative paths given below.\n\n"
        "Files to produce (ALL are required, in this order):\n" + file_list + "\n\n"
        "WRITING DISCIPLINE — INFORMATION DENSITY: each document is re-read as context by "
        "later stages, so length has a real cost. Be COMPLETE but DENSE: never drop "
        "substance/requirements/decisions; cut all padding (no preamble, no restating the "
        "context, no filler/marketing); tables and tight bullets over prose; state each "
        "fact once; minimal examples.\n"
        "Output ONLY the marked file blocks. Nothing before the first marker or after the "
        "last block.\n"
    )


def main():
    if len(sys.argv) < 3:
        log("usage: batch_runner.py <stage> <file...> [--raw-input X]")
        sys.exit(2)
    stage = sys.argv[1]
    rest = sys.argv[2:]
    raw_input = None
    if "--raw-input" in rest:
        i = rest.index("--raw-input")
        raw_input = rest[i + 1] if i + 1 < len(rest) else None
        rest = rest[:i] + rest[i + 2:]
    output_files = [f for f in rest if f]
    if len(output_files) < 2:
        log("need 2+ files to batch — deferring to per-file")
        sys.exit(3)

    tool = os.environ.get("FORGE_TOOL", "claude")
    model = os.environ.get("FORGE_MODEL", "")
    inputs = resolve_inputs(stage, raw_input)
    prompt = build_batch_prompt(stage, output_files, inputs)

    input_hash = hashlib.sha256(
        (tool + "\0" + (model or "") + "\0" + prompt).encode("utf-8")).hexdigest()

    try:
        cache = json.load(open(GEN_CACHE)) if os.path.exists(GEN_CACHE) else {}
    except (OSError, json.JSONDecodeError):
        cache = {}

    def _fresh(f):
        full = os.path.join(FORGE_DIR, f)
        return (cache.get(f, {}).get("hash") == input_hash
                and os.path.exists(full) and os.path.getsize(full) > 0)

    if os.environ.get("FORGE_FORCE_REGEN", "") != "1" and all(_fresh(f) for f in output_files):
        log("all " + str(len(output_files)) + " files cached (inputs unchanged) — skipping")
        sys.exit(0)

    log("Generating " + str(len(output_files)) + " files in ONE call ("
        + tool + " " + (model or "default") + ", context sent once)...")
    output, err = build_runner.invoke_ai(prompt, tool, model)
    if err or not output:
        log("batch AI call failed (" + (err or "empty output") + ") — fall back to per-file")
        sys.exit(3)

    parsed = build_runner.parse_files(output) or {}
    got = {}
    for k, v in parsed.items():
        got[k.strip().lstrip("./").replace("\\", "/")] = v

    missing = [f for f in output_files if f not in got or not (got[f] or "").strip()]
    if missing:
        log("batch output missing " + str(len(missing)) + " of "
            + str(len(output_files)) + " file(s) — fall back to per-file: " + ", ".join(missing))
        sys.exit(3)

    # All present — write atomically (all-or-nothing already guaranteed above).
    tok_in = build_runner._est_tokens(prompt)
    tok_out_total = build_runner._est_tokens(output)
    n = len(output_files)
    reviews_path = os.path.join(FORGE_DIR, "reviews.json")
    try:
        reviews = json.load(open(reviews_path)) if os.path.exists(reviews_path) else {}
    except (OSError, json.JSONDecodeError):
        reviews = {}

    for f in output_files:
        content = build_runner._strip_wrapping_code_fence(got[f], f)
        full = os.path.join(FORGE_DIR, f)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as out:
            out.write(content)
        cache[f] = {
            "hash": input_hash,
            "tokens_in": tok_in // n,           # shared input amortized across files
            "tokens_out": tok_out_total // n,
            "stage": stage,
            "model": model or tool,
            "updated_at": datetime.now().isoformat(),
        }
        reviews.pop(f, None)                    # regenerated -> needs re-review
        log("Written: " + f)

    os.makedirs(os.path.dirname(GEN_CACHE), exist_ok=True)
    with open(GEN_CACHE, "w") as f:
        json.dump(cache, f, indent=2)
    with open(reviews_path, "w") as f:
        json.dump(reviews, f, indent=2)

    log("Batch complete: " + str(n) + " files, ~" + str(tok_in) + " in / ~"
        + str(tok_out_total) + " out tokens (vs ~" + str(tok_in * n) + " in for per-file)")
    sys.exit(0)


if __name__ == "__main__":
    main()
