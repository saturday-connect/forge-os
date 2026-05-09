import os
from pprint import pformat

FORGE_VERSION = "0.2.0"

# Agents mapped to their definition blocks
AGENTS = {
    "product-strategist": """# Agent: Product Strategist

## Responsibility
Analyze raw, unstructured product visions and ideas to formulate structured business context. Define the foundational business model, target users and personas, constraints, competitive landscape, and product positioning.

## Inputs
- raw-input.md

## Outputs
- 00-context/product-vision.md
- 00-context/business-model.md
- 00-context/constraints.md
- 00-context/users-and-personas.md
- 00-context/competitive-analysis.md
- 00-context/positioning.md

## Rules
- Distill the raw input into a clear, cohesive product vision document.
- Distill the raw input into structured, concrete statements for the other context files.
- Ensure the business model clearly defines the value proposition and target market.
- Develop realistic personas based on the implied audience of the product vision.
- If constraints are not specified, infer reasonable default constraints for an MVP.

## Review Checklist
- Is the business model realistic and clearly aligned with the product vision?
- Are the personas specific, with clear goals and pain points?
- Are assumptions explicitly marked?
- Does the positioning statement clearly differentiate the product?
""",

    "product-manager": """# Agent: Product Manager

## Responsibility
Translate business context and product vision into actionable product requirements. Author the Business Requirements Document (BRD), Product Requirements Document (PRD), Non-Functional Requirements, and define clear success metrics.

## Inputs
- 00-context/*

## Outputs
- 01-requirements/brd.md
- 01-requirements/prd.md
- 01-requirements/non-functional-requirements.md
- 01-requirements/open-questions.md
- 01-requirements/success-metrics.md

## Rules
- BRD must map directly to the business-model.md and positioning.md.
- PRD must detail the functional capabilities needed to support the user journeys.
- Non-functional requirements MUST establish realistic baselines for scale, latency, and reliability based on constraints.
- Explicitly log unknown variables into open-questions.md.
- Success metrics must be quantifiable and measurable (e.g. Daily Active Users, Conversion Rate).

## Review Checklist
- Are the functional requirements clear, unambiguous, and testable?
- Are non-functional requirements quantified (e.g. "99.9% uptime" instead of "highly available")?
- Do the success metrics accurately reflect the business goals?
""",

    "business-analyst": """# Agent: Business Analyst

## Responsibility
Map requirements into structured domains and user journeys. Define the domain model, analyze dependencies, and document process flows and risks.

## Inputs
- 01-requirements/*

## Outputs
- 03-analysis/domain-model.md
- 03-analysis/user-journeys.md
- 03-analysis/risks-and-assumptions.md
- 03-analysis/process-flows.md

## Rules
- The domain model must outline the core entities, attributes, and their relationships.
- User journeys must trace the end-to-end path of personas achieving their goals.
- Highlight specific business rules and validations within process flows.
- Map out all logical dependencies required to execute the user journeys.

## Review Checklist
- Does the domain model cover all entities implied by the PRD?
- Are the user journeys step-by-step and chronological?
- Are the risks actionable with mitigation strategies?
""",

    "product-designer": """# Agent: Product Designer

## Responsibility
Translate requirements into an experience and visual design specification. Define the design system, UX principles, screen specifications, and accessibility guidelines.

## Inputs
- 00-context/*
- 01-requirements/*

## Outputs
- 02-design/design-brief.md
- 02-design/design-system.md
- 02-design/ux-principles.md
- 02-design/user-flows.md
- 02-design/accessibility-guidelines.md

## Rules
- Design system must define core typography, color palettes, and standard components.
- UX principles must align with the target audience expectations (e.g. enterprise vs consumer).
- User flows must represent screen-to-screen navigation logic.
- Accessibility guidelines must conform to WCAG 2.1 AA standards at minimum.

## Review Checklist
- Is the component map comprehensive enough for developers?
- Are responsive behaviors (mobile/tablet/desktop) accounted for?
- Are interaction states (hover, focus, error) defined?
""",

    "architect": """# Agent: Software Architect

## Responsibility
Design the high-level technical architecture, API contracts, data schema, security posture, and deployment topology to fulfill the product requirements.

## Inputs
- 01-requirements/*
- 02-design/*
- 03-analysis/*

## Outputs
- 04-architecture/system-architecture.md
- 04-architecture/api-design.md
- 04-architecture/data-model.md
- 04-architecture/security-design.md
- 04-architecture/deployment-architecture.md

## Rules
- System architecture must identify major services, components, and their integrations.
- API design must follow RESTful or GraphQL best practices, outlining key endpoints and payloads.
- Data model must be normalized (or explicitly denormalized for performance), specifying relationships and keys.
- Security design must cover authentication, authorization, data-in-transit, and data-at-rest.

## Review Checklist
- Can the proposed architecture meet the non-functional requirements?
- Are the API contracts explicitly defined with methods and paths?
- Is the deployment topology scalable and resilient?
""",

    "backend-engineer": """# Agent: Backend Engineer

## Responsibility
Write the detailed backend implementation specifications, translating architecture into actionable code guidelines and implementation plans.

## Inputs
- 04-architecture/*
- 02-design/*

## Outputs
- 06-engineering/backend-spec.md
- 06-engineering/frontend-spec.md
- 06-engineering/implementation-plan.md

## Rules
- Detail specific libraries, frameworks, and patterns to be used.
- Outline data access strategies, caching mechanisms, and background processing.
- The implementation plan should break the work into ordered, actionable technical phases.

## Review Checklist
- Is the technology stack completely specified?
- Are the edge cases and failure modes addressed?
- Is the implementation sequence logically ordered by dependency?
""",

    "qa-engineer": """# Agent: QA Engineer

## Responsibility
Define the testing strategy and acceptance criteria to ensure the product meets all requirements and design specifications.

## Inputs
- 01-requirements/*
- 06-engineering/*

## Outputs
- 07-quality/test-strategy.md
- 07-quality/acceptance-tests.md

## Rules
- Test strategy must cover unit, integration, E2E, and performance testing methodologies.
- Acceptance tests must use Given-When-Then (BDD) format mapped directly to user stories/PRD.
- Include failure scenarios, boundary conditions, and edge cases.

## Review Checklist
- Are all critical user journeys covered by acceptance tests?
- Is the strategy realistic for the current team size and CI/CD capability?
""",

    "devops-engineer": """# Agent: DevOps Engineer

## Responsibility
Design the operational infrastructure, monitoring strategies, incident response plans, and runbooks.

## Inputs
- 04-architecture/*
- 06-engineering/*

## Outputs
- 08-operations/monitoring.md
- 08-operations/runbook.md
- 08-operations/incident-response.md

## Rules
- Define key metrics to monitor (Golden Signals: Latency, Traffic, Errors, Saturation).
- The runbook must contain actionable, step-by-step resolution paths for common alerts.
- Incident response must define severity levels and escalation paths.

## Review Checklist
- Are the alerts actionable and non-noisy?
- Does the runbook provide exact commands or dashboard links?
""",

    "release-manager": """# Agent: Release Manager

## Responsibility
Coordinate the release process, ensuring production readiness, defining rollout strategies, and documenting release notes.

## Inputs
- 05-delivery/*
- 07-quality/*

## Outputs
- 09-release/release-notes.md
- 09-release/production-readiness-review.md
- 09-release/rollout-strategy.md

## Rules
- Rollout strategy must detail feature flagging, canary releases, or blue/green deployments.
- Production readiness review must explicitly check off security, scaling, and operational requirements.
- Release notes must be user-facing, summarizing value delivered.

## Review Checklist
- Is the rollback plan clearly defined if the rollout fails?
- Are the release notes free of internal engineering jargon?
""",

    "marketing-strategist": """# Agent: Marketing Strategist

## Responsibility
Develop the go-to-market strategy, product positioning, and target audience definition.

## Inputs
- 00-context/*
- 05-delivery/*

## Outputs
- 10-marketing/marketing-strategy.md
- 10-marketing/product-positioning.md
- 10-marketing/target-audience.md

## Rules
- Define clear buyer personas and decision-makers (if B2B) or user segments (if B2C).
- Develop a messaging framework that highlights the unique value proposition.
- Outline key marketing channels and campaign tactics for launch.

## Review Checklist
- Does the positioning clearly stand out from the competitive analysis?
- Are the marketing channels realistic for the target audience?
"""
}

# Gates mapped to their definitions
GATES = {
    "context-gate": """# Gate: Context

## Status
PENDING

## Required Checks
- [ ] Product Vision is clear and concise.
- [ ] Business Model is viable and aligns with constraints.
- [ ] Target audience is well-defined.
- [ ] Competitive differentiation is identified.

## Reviewer Notes
- Please manually review the 00-context folder outputs. Once satisfied, change Status to PASSED.
""",

    "prd-gate": """# Gate: PRD

## Status
PENDING

## Required Checks
- [ ] Requirements cover all user journeys in the Context.
- [ ] Non-functional requirements are quantified.
- [ ] Success metrics are trackable.

## Reviewer Notes
- Please manually review 01-requirements. Once satisfied, change Status to PASSED.
""",

    "design-gate": """# Gate: Design

## Status
PENDING

## Required Checks
- [ ] Design system covers all necessary UI states.
- [ ] User flows match the PRD capabilities.
- [ ] Accessibility standards are met.

## Reviewer Notes
- Review 02-design. Change Status to PASSED to proceed to Architecture.
""",

    "architecture-gate": """# Gate: Architecture

## Status
PENDING

## Required Checks
- [ ] API contracts are fully specified.
- [ ] Data model is normalized.
- [ ] Security boundaries are verified.

## Reviewer Notes
- Review 04-architecture. Change Status to PASSED to proceed to Engineering.
""",

    "engineering-gate": """# Gate: Engineering

## Status
PENDING

## Required Checks
- [ ] Implementation plan is broken down logically.
- [ ] Tech stack aligns with architecture.

## Reviewer Notes
- Review 06-engineering. Change Status to PASSED.
""",

    "qa-gate": """# Gate: Quality Assurance

## Status
PENDING

## Required Checks
- [ ] Acceptance criteria covers all edge cases.
- [ ] Test strategy is CI-compatible.

## Reviewer Notes
- Review 07-quality. Change Status to PASSED.
""",

    "release-gate": """# Gate: Release

## Status
PENDING

## Required Checks
- [ ] Rollout strategy is safe.
- [ ] Rollback procedures are documented.
- [ ] Runbooks are actionable.

## Reviewer Notes
- Review 08-operations and 09-release. Change Status to PASSED.
""",

    "marketing-gate": """# Gate: Marketing

## Status
PENDING

## Required Checks
- [ ] Messaging aligns with Product Vision.
- [ ] Launch channels are identified.

## Reviewer Notes
- Review 10-marketing. Change Status to PASSED.
"""
}

STAGE_OUTPUT_FILES = {
    "context": [
        "00-context/product-vision.md",
        "00-context/business-model.md",
        "00-context/constraints.md",
        "00-context/users-and-personas.md",
        "00-context/competitive-analysis.md",
        "00-context/positioning.md",
    ],
    "requirements": [
        "01-requirements/brd.md",
        "01-requirements/prd.md",
        "01-requirements/non-functional-requirements.md",
        "01-requirements/open-questions.md",
        "01-requirements/success-metrics.md",
    ],
    "design": [
        "02-design/design-brief.md",
        "02-design/design-system.md",
        "02-design/design-tokens.md",
        "02-design/ux-principles.md",
        "02-design/information-architecture.md",
        "02-design/user-flows.md",
        "02-design/page-inventory.md",
        "02-design/screen-specs.md",
        "02-design/component-map.md",
        "02-design/accessibility-guidelines.md",
        "02-design/responsive-behavior.md",
        "02-design/design-gap-analysis.md",
        "02-design/prototype-plan.md",
        "02-design/figma-integration.md",
        "02-design/design-review.md",
    ],
    "analysis": [
        "03-analysis/domain-model.md",
        "03-analysis/user-journeys.md",
        "03-analysis/risks-and-assumptions.md",
        "03-analysis/process-flows.md",
        "03-analysis/dependency-analysis.md",
    ],
    "architecture": [
        "04-architecture/system-architecture.md",
        "04-architecture/api-design.md",
        "04-architecture/data-model.md",
        "04-architecture/security-design.md",
        "04-architecture/deployment-architecture.md",
        "04-architecture/observability-architecture.md",
    ],
    "delivery": [
        "05-delivery/roadmap.md",
        "05-delivery/epics.md",
        "05-delivery/user-stories.md",
        "05-delivery/sprint-plan.md",
        "05-delivery/milestones.md",
        "05-delivery/release-roadmap.md",
    ],
    "engineering": [
        "06-engineering/backend-spec.md",
        "06-engineering/frontend-spec.md",
        "06-engineering/integration-spec.md",
        "06-engineering/observability.md",
        "06-engineering/error-handling.md",
        "06-engineering/coding-guidelines.md",
        "06-engineering/implementation-plan.md",
    ],
    "qa": [
        "07-quality/test-strategy.md",
        "07-quality/acceptance-tests.md",
        "07-quality/regression-suite.md",
        "07-quality/performance-tests.md",
        "07-quality/security-tests.md",
        "07-quality/accessibility-tests.md",
    ],
    "operations": [
        "08-operations/monitoring.md",
        "08-operations/runbook.md",
        "08-operations/rollback-plan.md",
        "08-operations/incident-response.md",
        "08-operations/backup-recovery.md",
        "08-operations/support-handbook.md",
    ],
    "release": [
        "09-release/release-notes.md",
        "09-release/production-readiness-review.md",
        "09-release/go-live-plan.md",
        "09-release/rollout-strategy.md",
        "09-release/post-release-checklist.md",
    ],
    "marketing": [
        "10-marketing/marketing-strategy.md",
        "10-marketing/product-positioning.md",
        "10-marketing/target-audience.md",
        "10-marketing/ideal-customer-profile.md",
        "10-marketing/messaging-framework.md",
        "10-marketing/brand-guidelines.md",
        "10-marketing/launch-plan.md",
        "10-marketing/go-to-market-plan.md",
        "10-marketing/pricing-strategy.md",
        "10-marketing/competitive-comparison.md",
        "10-marketing/website-copy.md",
        "10-marketing/landing-page-copy.md",
        "10-marketing/blog-content-plan.md",
        "10-marketing/social-media-plan.md",
        "10-marketing/email-campaigns.md",
        "10-marketing/seo-strategy.md",
        "10-marketing/content-calendar.md",
        "10-marketing/analytics-kpis.md",
        "10-marketing/campaign-performance.md",
        "10-marketing/customer-feedback-insights.md",
    ],
}

STAGE_MULTI_OUTPUTS = f"STAGE_MULTI_OUTPUTS = {pformat(STAGE_OUTPUT_FILES, width=100)}"
FILES_TO_TOUCH = pformat(
    [file_path for output_files in STAGE_OUTPUT_FILES.values() for file_path in output_files],
    width=100,
)

DASHBOARD_HTML_CONTENT = open(os.path.join(os.path.dirname(__file__), "dashboard.html")).read()

SERVER_PY_CONTENT = r"""import os
import sys
import json
import subprocess
import time
import threading
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", ".")
FORGE_DIR = os.path.join(REPO_ROOT, ".forge")
REVIEWS_FILE = os.path.join(FORGE_DIR, "reviews.json")
STATE_FILE = os.path.join(FORGE_DIR, "project-state.json")
RAW_INPUT_DIR = os.path.join(FORGE_DIR, "00-raw-input")
FORGE_VERSION = os.environ.get("FORGE_VERSION", "unknown")
FORGE_SCRIPT = os.environ.get("FORGE_SCRIPT", "")

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
    if not os.path.exists(RAW_INPUT_DIR):
        return []
    files = []
    for fname in sorted(os.listdir(RAW_INPUT_DIR)):
        if fname.endswith(".md"):
            fpath = os.path.join(RAW_INPUT_DIR, fname)
            st = os.stat(fpath)
            files.append({
                "name": fname,
                "size": st.st_size,
                "modifiedAt": int(st.st_mtime)
            })
    return files

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

def set_processing(status, stage=""):
    status_file = os.path.join(FORGE_DIR, "runs/status.json")
    runs_dir = os.path.join(FORGE_DIR, "runs")
    if os.path.exists(runs_dir):
        try:
            with open(status_file, "w") as sf:
                json.dump({"status": status, "stage": stage}, sf)
        except Exception:
            pass

def compute_full_state():
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
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(dashboard_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
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
            fpath = os.path.join(RAW_INPUT_DIR, name)
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

        self._json_response(404, {"error": "not found"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/raw-input":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8")) if post_data else {}
            except Exception:
                data = {}
            name = data.get("name")
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            fpath = os.path.join(RAW_INPUT_DIR, name)
            if os.path.exists(fpath):
                os.remove(fpath)
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

        if path == "/api/raw-input":
            name = data.get("name")
            content = data.get("content", "")
            if not name:
                self._json_response(400, {"error": "missing name"})
                return
            os.makedirs(RAW_INPUT_DIR, exist_ok=True)
            fpath = os.path.join(RAW_INPUT_DIR, name)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/generate":
            stage = data.get("stage", "all")
            forge_script = FORGE_SCRIPT or os.path.abspath(os.path.join(FORGE_DIR, "..", "..", "forge"))

            def run_generate():
                set_processing("running", stage)
                try:
                    if stage == "all":
                        # Find all raw input files
                        raw_inputs = list_raw_inputs()
                        raw_input_arg = None
                        if raw_inputs:
                            raw_input_arg = os.path.join(RAW_INPUT_DIR, raw_inputs[0]["name"])
                        pipeline_stages = [
                            "context", "requirements", "design", "analysis", "architecture",
                            "delivery", "engineering", "qa", "operations", "release", "marketing"
                        ]
                        for s in pipeline_stages:
                            set_processing("running", s)
                            cmd = [forge_script, "generate", s]
                            if raw_input_arg and s == "context":
                                cmd.append(raw_input_arg)
                            subprocess.run(cmd, cwd=REPO_ROOT)
                    else:
                        raw_inputs = list_raw_inputs()
                        raw_input_arg = None
                        if raw_inputs and stage == "context":
                            raw_input_arg = os.path.join(RAW_INPUT_DIR, raw_inputs[0]["name"])
                        cmd = [forge_script, "generate", stage]
                        if raw_input_arg:
                            cmd.append(raw_input_arg)
                        subprocess.run(cmd, cwd=REPO_ROOT)
                finally:
                    set_processing("idle")

            t = threading.Thread(target=run_generate, daemon=True)
            t.start()
            self._json_response(200, {"status": "started", "stage": stage})
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
                logs = []
                try:
                    def run_git(args, cwd=REPO_ROOT):
                        result = subprocess.run(
                            ["git"] + args, cwd=cwd,
                            capture_output=True, text=True
                        )
                        logs.append(f"$ git {' '.join(args)}: {result.returncode}")
                        if result.stdout.strip():
                            logs.append(result.stdout.strip())
                        if result.stderr.strip():
                            logs.append(result.stderr.strip())
                        return result

                    # Init if not a git repo
                    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
                        run_git(["init"])
                        if email:
                            run_git(["config", "user.email", email])
                        if username:
                            run_git(["config", "user.name", username])

                    # Create branch
                    run_git(["checkout", "-b", branch_name])
                    build_entry["status"] = "committed"

                    # Stage and commit forge docs
                    run_git(["add", ".forge/"])
                    run_git(["commit", "-m", f"forge: generated docs {timestamp}"])

                    # Push if repo_url is set
                    if repo_url:
                        push_url = repo_url
                        if token and "github.com" in repo_url:
                            # Inject token
                            push_url = repo_url.replace("https://", f"https://{username}:{token}@")
                        result = run_git(["push", "-u", push_url, branch_name])
                        if result.returncode == 0:
                            build_entry["status"] = "pushed"
                            # Construct PR URL for GitHub
                            if "github.com" in repo_url:
                                clean_url = repo_url.rstrip("/").replace(".git", "")
                                default_branch = git_cfg.get("default_branch", "main")
                                pr_url = f"{clean_url}/compare/{default_branch}...{branch_name}?expand=1"
                                build_entry["pr_url"] = pr_url
                        else:
                            build_entry["status"] = "error"
                except Exception as e:
                    logs.append(f"Error: {e}")
                    build_entry["status"] = "error"
                finally:
                    build_entry["log"] = logs
                    proj2 = load_project_state()
                    proj2.setdefault("builds", []).append(build_entry)
                    save_project_state(proj2)

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
            cmd = [sys.executable, os.path.join(FORGE_DIR, "scripts/run.py"), stage, "--output", file_path, "--critique", critique]
            result = subprocess.run(cmd, cwd=REPO_ROOT)
            if result.returncode == 0:
                self._json_response(200, {"status": "success"})
            else:
                self._json_response(500, {"status": "failed"})
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
"""

TEMPLATE = '''#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from datetime import datetime

FORGE_DIR = ".forge"
FORGE_VERSION = "{FORGE_VERSION}"

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
        print(f"[STAGE-RUNNER] Documents to generate: {{len(outputs)}}")

        success_count = 0
        failed_count = 0

        for output_file in outputs:
            print(f"[STAGE-RUNNER] Generating: {{output_file}}")
            
            status_file = os.path.join("runs", "status.json")
            if os.path.exists("runs"):
                import json
                with open(status_file, "w") as sf:
                    json.dump({{"stage": stage, "file": output_file, "status": "generating"}}, sf)
            
            cmd = [sys.executable, "scripts/run.py", stage, "--output", output_file]
            if raw_input:
                cmd.extend(["--raw-input", raw_input])
                
            result = subprocess.run(cmd)

            if os.path.exists("runs"):
                import json
                with open(status_file, "w") as sf:
                    json.dump({{"status": "idle"}}, sf)

            if result.returncode == 0:
                success_count += 1
                try:
                    reviews_path = "reviews.json"
                    if os.path.exists(reviews_path):
                        with open(reviews_path) as rf:
                            _reviews = json.load(rf)
                    else:
                        _reviews = {{}}
                    _reviews.pop(output_file, None)
                    with open(reviews_path, "w") as rf:
                        json.dump(_reviews, rf, indent=2)
                except Exception:
                    pass
            else:
                failed_count += 1
                print(f"[ERROR] Failed to generate: {{output_file}}")

        print(f"[STAGE-RUNNER] Stage complete. Success: {{success_count}}, Failed: {{failed_count}}")
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
from datetime import datetime, timezone

# Configuration
REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", ".")
LOG_LEVEL = os.environ.get("AEOS_LOG_LEVEL", "info")
os.environ["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
AGENTS_DIR = os.path.join(REPO_ROOT, "11-agents")
GATES_DIR = os.path.join(REPO_ROOT, "12-gates")
RUNS_LOG = os.path.join(REPO_ROOT, "runs/run-log.md")

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

def invoke_model(prompt, output_path):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
        tmp_path = tmp.name

    try:
        if state.model == "gemini":
            subprocess.run(["gemini", "--skip-trust", "-p", prompt], stdout=open(tmp_path, 'w'), check=True)
        elif state.model == "claude":
            subprocess.run(["claude"], input=prompt, text=True, stdout=open(tmp_path, 'w'), check=True)
        elif state.model == "openai":
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
                with urllib.request.urlopen(req) as response:
                    res_body = response.read().decode('utf-8')
                    res_json = json.loads(res_body)
                    content = res_json['choices'][0]['message']['content']
                    with open(tmp_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            except urllib.error.URLError as e:
                log_error(f"OpenAI API request failed: {{e}}")
                sys.exit(1)
        else:
            log_error(f"Unsupported model: '{{state.model}}'. Supported: gemini, claude, openai")
            sys.exit(1)
            
        with open(tmp_path, 'r', encoding='utf-8') as f:
            result_content = f.read()

        if not result_content.strip():
            log_error(f"Model returned empty output for: {{output_path}}")
            sys.exit(1)
            
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
    
    prompt = build_prompt(agent_path, inputs, output_file, args.critique)
    
    log_info(f"Invoking model: {{state.model}}")
    invoke_model(prompt, output_path)
    
    log_run()
    log_info("Stage complete.")

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

SERVER_PY = r\"\"\"{SERVER_PY_CONTENT}\"\"\"

DASHBOARD_HTML = r\"\"\"{DASHBOARD_HTML_CONTENT}\"\"\"

# -------------------------------------------------------------------------
# Commands
# -------------------------------------------------------------------------

def cmd_init():
    print("Initializing Forge Environment...")

    if not os.path.exists(FORGE_DIR):
        os.makedirs(FORGE_DIR)

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
        "scripts"
    ]

    for d in directories:
        os.makedirs(os.path.join(FORGE_DIR, d), exist_ok=True)

    files_to_touch = {FILES_TO_TOUCH}

    for f in files_to_touch:
        with open(os.path.join(FORGE_DIR, f), 'a'):
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
        "product-analyst"
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

    with open(os.path.join(FORGE_DIR, "13-decisions/decision-log.md"), "w") as f:
        f.write("# Decision Log\\n\\n| Date | Decision | Context | Owner | Status |\\n|---|---|---|---|---|\\n")

    with open(os.path.join(FORGE_DIR, "13-decisions/change-log.md"), "w") as f:
        f.write("# Change Log\\n\\n| Date | Change | Reason | Owner |\\n|---|---|---|---|\\n")

    with open(os.path.join(FORGE_DIR, "13-decisions/adr-index.md"), "w") as f:
        f.write("# ADR Index\\n\\n| ADR | Title | Status | Date |\\n|---|---|---|---|\\n")

    current_date = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    with open(os.path.join(FORGE_DIR, "runs/run-log.md"), "w") as f:
        f.write(f"# Run Log\\n\\n| Date | Command | Status |\\n|---|---|---|\\n| {{current_date}} | init | SUCCESS |\\n")

    with open(os.path.join(FORGE_DIR, "runs/execution-history.md"), "w") as f:
        f.write("# Execution History\\n")

    with open(os.path.join(FORGE_DIR, "runs/failed-runs.md"), "w") as f:
        f.write("# Failed Runs\\n")

    # Seed Scripts
    with open(os.path.join(FORGE_DIR, "scripts/stage_runner.py"), "w") as f:
        f.write(STAGE_RUNNER_PY)
    with open(os.path.join(FORGE_DIR, "scripts/run.py"), "w") as f:
        f.write(RUN_PY)
    with open(os.path.join(FORGE_DIR, "scripts/validate_gates.py"), "w") as f:
        f.write(VALIDATE_GATES_PY)
    with open(os.path.join(FORGE_DIR, "scripts/server.py"), "w") as f:
        f.write(SERVER_PY)
    with open(os.path.join(FORGE_DIR, "scripts/dashboard.html"), "w") as f:
        f.write(DASHBOARD_HTML)
    print("Dashboard deployed to .forge/scripts/")

    reviews_path = os.path.join(FORGE_DIR, "reviews.json")
    if not os.path.exists(reviews_path):
        with open(reviews_path, "w") as f:
            json.dump({{}}, f)

    os.makedirs(os.path.join(FORGE_DIR, "00-raw-input"), exist_ok=True)

    state_path = os.path.join(FORGE_DIR, "project-state.json")
    if not os.path.exists(state_path):
        with open(state_path, "w") as f:
            json.dump({{}}, f)

    print("Forge OS environment initialized successfully in .forge/")

PIPELINE_STAGES = [
    "context", "requirements", "design", "analysis", "architecture",
    "delivery", "engineering", "qa", "operations", "release", "marketing"
]

def cmd_generate(stage, input_file=None):
    if not os.path.exists(FORGE_DIR):
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

    # run.py resolves paths relative to cwd (.forge/), so AEOS_REPO_ROOT must be "."
    env = {{**os.environ, "AEOS_REPO_ROOT": "."}}
    result = subprocess.run(cmd, cwd=FORGE_DIR, env=env)

    if result.returncode == 0:
        print(f"Forge {{stage}} generation completed successfully.")
    else:
        print(f"Forge {{stage}} generation failed.")
        sys.exit(1)

def cmd_pipeline(input_file=None):
    if not os.path.exists(FORGE_DIR):
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

    for stage in PIPELINE_STAGES:
        print(f"==> [{{stage}}]")
        cmd = [sys.executable, "scripts/stage_runner.py", stage, abs_raw]
        env = {{**os.environ, "AEOS_REPO_ROOT": "."}}
        result = subprocess.run(cmd, cwd=FORGE_DIR, env=env)
        if result.returncode != 0:
            print("")
            print(f"  Gate blocked at stage '{{stage}}'.")
            print(f"  Review docs in the dashboard, then run: ./forge generate {{stage}}")
            sys.exit(1)
        print(f"  Done. Review '{{stage}}' docs before the next gate.")

    print("==> All stages generated.")
    print("    Open dashboard, review and approve documents to pass gates.")

def cmd_dashboard(port=8080):
    if not os.path.exists(FORGE_DIR):
        print("Forge not initialized. Please run 'forge init' first.")
        sys.exit(1)

    server_script = os.path.join(FORGE_DIR, "scripts/server.py")
    if not os.path.exists(server_script):
        print("Dashboard scripts not found. Run 'forge init' to regenerate.")
        sys.exit(1)

    print(f"Starting Forge Dashboard on port {{port}}...")
    project_root = os.path.dirname(os.path.abspath(FORGE_DIR))
    forge_abs = os.path.abspath(sys.argv[0])
    result = subprocess.run([sys.executable, server_script, str(port)], env={{**os.environ, "AEOS_REPO_ROOT": project_root, "FORGE_VERSION": FORGE_VERSION, "FORGE_SCRIPT": forge_abs}})
    sys.exit(result.returncode)

def cmd_upgrade():
    print(f"Forge OS v{{FORGE_VERSION}} — upgrading runtime scripts...")
    if not os.path.exists(FORGE_DIR):
        print("Forge not initialized. Run './forge init' first.")
        sys.exit(1)
    cmd_init()
    print("Upgrade complete. Runtime scripts updated, project data preserved.")

def cmd_dev(port=8080):
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
    src_dash = os.path.join(os.path.dirname(forge_script), "src/dashboard.html")
    dst_dash = os.path.join(FORGE_DIR, "scripts/dashboard.html")
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
        os.environ["AEOS_REPO_ROOT"] = project_path
        FORGE_DIR = os.path.join(project_path, ".forge")
        args = args[2:]

    if not args:
        print(f"Forge OS v{{FORGE_VERSION}}")
        print("Usage: ./forge [--project <path>] <version|init|upgrade|generate [stage]|pipeline|dashboard [port]|dev [port]>")
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
        port = int(args[1]) if len(args) > 1 else 8080
        cmd_dashboard(port)
    elif command == "dev":
        port = int(args[1]) if len(args) > 1 else 8080
        cmd_dev(port)
    else:
        print(f"Unknown command: {{command}}")
        print("Available commands: version, init, upgrade, generate [stage], pipeline, dashboard [port], dev [port]")
        sys.exit(1)
'''

def build_forge():
    agent_code = '    for agent in agents:\n        agent_path = os.path.join(FORGE_DIR, f"11-agents/{agent}.md")\n        if not os.path.exists(agent_path):\n            with open(agent_path, "w") as f:\n'
    first = True
    for agent, text in AGENTS.items():
        if first:
            agent_code += f'                if agent == "{agent}":\n                    f.write("""{text}""")\n'
            first = False
        else:
            agent_code += f'                elif agent == "{agent}":\n                    f.write("""{text}""")\n'
    
    agent_code += '                else:\n                    f.write(agent_template.format(agent=agent))\n'
    
    gate_code = '    for gate in gates:\n        gate_path = os.path.join(FORGE_DIR, f"12-gates/{gate}.md")\n        if not os.path.exists(gate_path):\n            with open(gate_path, "w") as f:\n'
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
        SERVER_PY_CONTENT=SERVER_PY_CONTENT,
    )

    with open("forge", "w") as f:
        f.write(forge_content)

    print("forge built successfully.")

if __name__ == "__main__":
    build_forge()
