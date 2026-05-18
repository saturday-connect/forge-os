import os
from pprint import pformat

FORGE_VERSION = "0.3.4"

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
""",

    "frontend-engineer": """# Agent: Frontend Engineer

## Responsibility
Author detailed frontend engineering specifications — component architecture, state management patterns, routing, API integration strategy, and accessibility requirements.

## Inputs
- 02-design/*
- 01-requirements/prd.md
- 04-architecture/api-design.md

## Outputs
- 06-engineering/frontend-spec.md

## Rules
- Specify the component hierarchy and which components are shared vs page-specific.
- Define the state management approach (global vs local, store structure).
- Map each design screen to a route and component.
- Document all API calls the frontend makes and their expected shapes.
- Flag any design gaps or infeasible interactions.

## Review Checklist
- Does the component tree match the design screens?
- Are loading, error, and empty states specified for every data-fetching component?
- Is the API integration strategy consistent with the backend spec?
""",

    "ux-designer": """# Agent: UX Designer

## Responsibility
Define user experience flows, interaction patterns, information architecture, and usability guidelines. Produce wireframe-level specifications that bridge business requirements and visual design.

## Inputs
- 00-context/users-and-personas.md
- 01-requirements/prd.md
- 03-analysis/user-journeys.md

## Outputs
- 02-design/user-flows.md
- 02-design/information-architecture.md
- 02-design/ux-principles.md
- 02-design/page-inventory.md

## Rules
- Ground every flow in a specific persona and goal from the persona document.
- Identify friction points and document how each is resolved.
- The information architecture must reflect the navigation structure of the final product.

## Review Checklist
- Does every user journey from the analysis stage have a corresponding UX flow?
- Are error states and edge cases covered?
""",

    "design-system-reviewer": """# Agent: Design System Reviewer

## Responsibility
Audit the design system and component specifications for internal consistency, accessibility compliance, and alignment with brand guidelines. Produce a gap analysis and actionable recommendations.

## Inputs
- 02-design/design-system.md
- 02-design/design-tokens.md
- 02-design/component-map.md
- 02-design/accessibility-guidelines.md

## Outputs
- 02-design/design-review.md
- 02-design/design-gap-analysis.md

## Rules
- Check every component for WCAG 2.1 AA compliance (contrast ratios, focus states, keyboard nav).
- Flag any tokens or components that are referenced but not defined.
- Rate each gap as: critical (blocks launch), major (degrades UX), or minor (cosmetic).

## Review Checklist
- Are all colour tokens contrast-compliant?
- Is there a focus indicator for every interactive element?
- Are mobile breakpoints specified for every component?
""",

    "security-reviewer": """# Agent: Security Reviewer

## Responsibility
Identify security risks in the architecture and engineering design. Review authentication, authorisation, data handling, API surface, and deployment configuration against OWASP Top 10 and relevant compliance requirements.

## Inputs
- 04-architecture/security-design.md
- 04-architecture/api-design.md
- 04-architecture/data-model.md
- 06-engineering/backend-spec.md

## Outputs
- 07-quality/security-tests.md

## Rules
- Map every finding to an OWASP category.
- Classify each risk: Critical / High / Medium / Low.
- For every risk, provide a concrete remediation action.
- Flag any PII handling that requires compliance review (GDPR, SOC 2, HIPAA).

## Review Checklist
- Is authentication stateless and token-expiry enforced?
- Are all external inputs validated and sanitised?
- Are secrets stored in environment variables, not in code?
""",

    "brand-strategist": """# Agent: Brand Strategist

## Responsibility
Define brand identity, voice, visual language, and messaging guidelines that differentiate the product and resonate with the target audience.

## Inputs
- 00-context/product-vision.md
- 00-context/competitive-analysis.md
- 10-marketing/target-audience.md

## Outputs
- 10-marketing/brand-guidelines.md
- 10-marketing/messaging-framework.md

## Rules
- The brand voice must be consistent across all output documents.
- Messaging pillars must each map to a distinct audience pain point.
- Include do/don't examples for tone of voice.

## Review Checklist
- Is the brand voice distinct from the top 3 competitors?
- Does the messaging framework address each persona's primary pain point?
""",

    "content-writer": """# Agent: Content Writer

## Responsibility
Produce marketing copy — website pages, landing pages, blog posts, email campaigns, and social content — that converts the target audience.

## Inputs
- 10-marketing/messaging-framework.md
- 10-marketing/brand-guidelines.md
- 10-marketing/target-audience.md
- 00-context/positioning.md

## Outputs
- 10-marketing/website-copy.md
- 10-marketing/landing-page-copy.md
- 10-marketing/blog-content-plan.md
- 10-marketing/email-campaigns.md

## Rules
- Every piece of copy must have a clear CTA.
- Headlines must be benefit-led, not feature-led.
- Blog post plan must include title, angle, target keyword, and outline for each post.

## Review Checklist
- Does every CTA have a clear value proposition?
- Is the tone consistent with brand guidelines?
""",

    "seo-specialist": """# Agent: SEO Specialist

## Responsibility
Develop the SEO strategy including keyword research, on-page optimisation recommendations, content structure, and link-building priorities.

## Inputs
- 10-marketing/target-audience.md
- 10-marketing/blog-content-plan.md
- 00-context/competitive-analysis.md

## Outputs
- 10-marketing/seo-strategy.md

## Rules
- Cluster keywords by intent: informational, navigational, transactional.
- Map each cluster to a page or blog post.
- Prioritise keywords by search volume and difficulty for an early-stage product.

## Review Checklist
- Are the primary keywords achievable for a new domain?
- Is there a clear internal linking strategy?
""",

    "growth-marketer": """# Agent: Growth Marketer

## Responsibility
Design growth loops, acquisition channels, activation funnels, and retention tactics. Define experiments and success metrics for each growth lever.

## Inputs
- 00-context/users-and-personas.md
- 10-marketing/marketing-strategy.md
- 01-requirements/success-metrics.md

## Outputs
- 10-marketing/analytics-kpis.md
- 10-marketing/campaign-performance.md
- 10-marketing/social-media-plan.md
- 10-marketing/content-calendar.md

## Rules
- Every channel must have a hypothesis, target metric, and experiment definition.
- Prioritise channels by effort vs expected impact for an early-stage product.
- Retention tactics must address the first 30 / 60 / 90 day lifecycle.

## Review Checklist
- Is there a measurable success metric for each campaign?
- Are the acquisition channels realistic for the budget stage?
""",

    "product-analyst": """# Agent: Product Analyst

## Responsibility
Define the product analytics framework: what to measure, how to instrument it, and how to interpret results. Produce the KPI hierarchy and instrumentation plan.

## Inputs
- 01-requirements/success-metrics.md
- 00-context/users-and-personas.md
- 05-delivery/roadmap.md

## Outputs
- 10-marketing/analytics-kpis.md
- 10-marketing/customer-feedback-insights.md

## Rules
- KPIs must be tied to business outcomes, not just activity metrics.
- Every KPI must have: definition, formula, data source, owner, target, and review cadence.
- Instrument every critical user action defined in the user journeys.

## Review Checklist
- Is there a north-star metric with supporting metrics beneath it?
- Does the instrumentation plan cover all key user actions?
"""
}

# Code-generation agents (used by Build System)
CODE_AGENTS = {
    "code-architect": """# Agent: Code Architect

## Responsibility
Generate complete, production-ready backend code from architecture and engineering specifications.

## Output Format
For each file you generate, use this exact delimiter on its own line:
=== path/to/filename.ext ===
Then the file content, then the next delimiter for the next file.

## Generation Order
1. README.md (setup, env, run instructions, API summary)
2. Configuration files (env.example, docker-compose.yml, Makefile)
3. Data models / schema
4. Repository / data access layer
5. Service / business logic layer
6. API handlers / routes
7. Main entry point

## Rules
- Infer the tech stack from the architecture doc; default to Python (FastAPI) + PostgreSQL if unspecified
- Every function must be implemented — no stubs, no TODOs in logic
- Include proper error handling, type hints, logging
- Keep files focused: one concern per file
- Use environment variables for all secrets and config
""",

    "frontend-coder": """# Agent: Frontend Engineer (Coder)

## Responsibility
Generate complete frontend UI code from design and engineering specifications.

## Output Format
For each file you generate, use this exact delimiter on its own line:
=== path/to/filename.ext ===
Then the file content.

## Generation Order
1. README.md (setup, env, run, build instructions)
2. package.json + tsconfig.json (or equivalent)
3. Design tokens / CSS variables / theme file
4. Shared UI components
5. Page components (one per major screen in the design)
6. Routing / navigation
7. API client / data fetching layer
8. Main entry point (index.html, main.tsx, etc.)

## Rules
- Infer the tech stack from the frontend spec; default to React + TypeScript + Tailwind CSS if unspecified
- Match the design system: use the colors, spacing, and component names from the design docs
- Every component must be complete and renderable
- Include loading states, error states, and empty states
""",

    "integration-engineer": """# Agent: Integration Engineer

## Responsibility
Generate the integration layer code: API client, third-party service adapters, webhook handlers.

## Output Format
For each file, use this exact delimiter on its own line:
=== path/to/filename.ext ===
Then the file content.

## Rules
- Generate a typed API client that wraps every endpoint in the API design doc
- Include retry logic, timeout handling, and error normalization
- Generate adapters for each third-party service mentioned in the integration spec
- Include a README.md explaining each integration and required env vars
""",

    "qa-coder": """# Agent: QA Engineer (Coder)

## Responsibility
Generate a complete test suite from the quality specifications and acceptance criteria.

## Output Format
For each file, use this exact delimiter on its own line:
=== path/to/filename.ext ===
Then the file content.

## Generation Order
1. README.md (how to run tests, coverage targets)
2. Test configuration (jest.config, pytest.ini, etc.)
3. Unit tests for core business logic
4. Integration tests for API endpoints
5. E2E tests for critical user journeys from acceptance criteria
6. Test fixtures and factories

## Rules
- Infer the test framework from the engineering specs; default to pytest (backend) + Playwright (e2e)
- Every acceptance criterion in the quality docs must have at least one test
- Tests must be runnable — no placeholder test bodies
- Include a CI configuration snippet (GitHub Actions)
""",

    "devops-coder": """# Agent: DevOps Engineer (Coder)

## Responsibility
Generate infrastructure-as-code, CI/CD pipelines, and operational configuration from deployment and operations specs.

## Output Format
For each file, use this exact delimiter on its own line:
=== path/to/filename.ext ===
Then the file content.

## Generation Order
1. README.md (infrastructure overview, deployment guide)
2. Dockerfile + docker-compose.yml
3. CI/CD pipeline (GitHub Actions or specified tool)
4. Infrastructure-as-code (Terraform, Pulumi, or cloud-specific)
5. Monitoring config (Prometheus, Grafana dashboards, alerts)
6. Environment configuration templates

## Rules
- Infer the cloud provider and tooling from the deployment architecture doc; default to Docker + GitHub Actions if unspecified
- Every runbook action in the operations docs must have a corresponding script or make target
- Include health check endpoints, readiness probes
- Secrets must use environment variables or a secrets manager — never hardcoded
""",
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
with open(os.path.join(_HERE, 'runtime', 'server.py'), 'r', encoding='utf-8') as _f:
    SERVER_PY_CONTENT = _f.read()

BUILD_RUNNER_PY_CONTENT = r"""#!/usr/bin/env python3
'''Build system runner - generates production-grade code from reviewed spec documents.
Two-pass strategy: backend generates API contract first, then frontend/integration consume it.
Usage: python3 scripts/build_runner.py <step>
'''
import os, sys, json, subprocess, tempfile
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get("FORGE_REPO_ROOT", os.path.dirname(os.path.dirname(SCRIPT_DIR)))
_forge_data = os.environ.get("FORGE_DATA_DIR")
FORGE_DIR = os.path.expanduser(_forge_data) if _forge_data else os.path.dirname(SCRIPT_DIR)
BUILD_STATUS_FILE = os.path.join(FORGE_DIR, "runs", "build-system.json")
API_CONTRACT_FILE = os.path.join(FORGE_DIR, "15-build", "api-contract.md")

# Build order matters: backend must run before frontend/integration/tests
STEPS = {
    "backend": {
        "label": "Backend & API",
        "agent": "code-architect",
        "source_dirs": ["01-requirements", "03-analysis", "04-architecture", "06-engineering"],
        "source_files": [],
        "output_dir": "15-build/backend",
    },
    "frontend": {
        "label": "Frontend UI",
        "agent": "frontend-coder",
        "source_dirs": ["02-design", "01-requirements"],
        "source_files": ["06-engineering/frontend-spec.md", "04-architecture/system-architecture.md"],
        "output_dir": "15-build/frontend",
    },
    "integration": {
        "label": "Integration Layer",
        "agent": "integration-engineer",
        "source_dirs": ["06-engineering"],
        "source_files": ["04-architecture/api-design.md"],
        "output_dir": "15-build/integration",
    },
    "tests": {
        "label": "Test Suite",
        "agent": "qa-coder",
        "source_dirs": ["07-quality"],
        "source_files": ["06-engineering/backend-spec.md", "06-engineering/frontend-spec.md"],
        "output_dir": "15-build/tests",
    },
    "infra": {
        "label": "Infrastructure",
        "agent": "devops-coder",
        "source_dirs": ["04-architecture", "06-engineering", "07-quality", "08-operations"],
        "source_files": ["01-requirements/prd.md"],
        "output_dir": "15-build/infra",
    },
}

BUILD_ORDER = ["backend", "frontend", "integration", "tests", "infra"]

def load_build_status():
    if os.path.exists(BUILD_STATUS_FILE):
        try:
            with open(BUILD_STATUS_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_step_status(step, status_val, files=None, error=None):
    status = load_build_status()
    existing = status.get(step, {})
    status[step] = {
        "status": status_val,
        "files": files if files is not None else existing.get("files", []),
        "generated_at": datetime.now().isoformat() if status_val == "complete" else existing.get("generated_at", ""),
        "error": error,
    }
    with open(BUILD_STATUS_FILE, "w", encoding='utf-8') as f:
        json.dump(status, f, indent=2)

def collect_docs(meta):
    docs = []
    for dir_name in meta.get("source_dirs", []):
        dir_path = os.path.join(FORGE_DIR, dir_name)
        if os.path.isdir(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.endswith(".md"):
                    fpath = os.path.join(dir_path, fname)
                    if os.path.getsize(fpath) > 0:
                        with open(fpath, encoding="utf-8") as f:
                            content = f.read()
                        docs.append("=== SOURCE: " + dir_name + "/" + fname + " ===\n" + content)
    for rel_file in meta.get("source_files", []):
        fpath = os.path.join(FORGE_DIR, rel_file)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            docs.append("=== SOURCE: " + rel_file + " ===\n" + content)
    return "\n\n".join(docs)

def load_api_contract():
    if os.path.exists(API_CONTRACT_FILE) and os.path.getsize(API_CONTRACT_FILE) > 0:
        with open(API_CONTRACT_FILE, encoding="utf-8") as f:
            return f.read()
    return ""

def load_agent(agent_name):
    path = os.path.join(FORGE_DIR, "11-agents", agent_name + ".md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return "# Agent: " + agent_name + "\nGenerate code based on the provided specifications."

def invoke_ai(prompt, tool, model_id):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as tmp:
        tmp_path = tmp.name
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
        with open(tmp_path, "w", encoding='utf-8') as out_f:
            result = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE, timeout=600)
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace") if result.stderr else "AI call failed"
            return None, err
        with open(tmp_path, encoding="utf-8") as f:
            return f.read(), None
    except subprocess.TimeoutExpired:
        return None, "AI call timed out after 10 minutes"
    except FileNotFoundError:
        return None, "AI tool '" + tool + "' not found in PATH"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def sanitize_path(candidate):
    p = candidate.strip()
    if " (" in p or p.endswith(")"):
        return None
    parts = p.replace("\\", "/").split("/")
    if parts and parts[0] == "15-build":
        parts = parts[2:]
    if parts and parts[0] == ".forge":
        parts = parts[1:]
    parts = [p2 for p2 in parts if p2 and p2 != ".."]
    if not parts:
        return None
    return "/".join(parts)

def parse_files(output_text):
    files = {}
    current_path = None
    current_lines = []
    for line in output_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("=== ") and stripped.endswith(" ==="):
            if current_path and not current_path.startswith("SOURCE:"):
                files[current_path] = "\n".join(current_lines).strip()
            candidate = stripped[4:-4].strip()
            if candidate.startswith("SOURCE:"):
                current_path = None
                current_lines = []
            else:
                clean = sanitize_path(candidate)
                current_path = clean
                current_lines = []
        elif current_path:
            current_lines.append(line)
    if current_path and not current_path.startswith("SOURCE:"):
        files[current_path] = "\n".join(current_lines).strip()
    return files

# -----------------------------------------------------------------------
# Spec-enforcing prompt builders — one per step
# -----------------------------------------------------------------------

COMMON_FORMAT_RULE = (
    "OUTPUT FORMAT — MANDATORY:\n"
    "Output ONLY file blocks in this exact format, no prose before or after:\n"
    "=== path/to/file.ext ===\n"
    "<complete file content>\n\n"
    "Every file must be complete and immediately runnable. "
    "No truncation, no '# ... rest of file', no TODO stubs.\n"
)

def build_backend_prompt(persona, docs):
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
        (
            "1. TECH STACK: Read the architecture documents below. Identify every technology, "
            "framework, database, and service named. Use EXACTLY those — no substitutions.\n"
            "   - If the spec says Supabase: use the supabase-py client, NOT SQLAlchemy ORM.\n"
            "   - If the spec says PostgreSQL via Supabase: use Supabase's database client.\n"
            "   - If the spec says FastAPI: use FastAPI with async handlers.\n"
            "   - If the spec says JWT auth: implement it exactly as described.\n"
            "   Never default to SQLite, in-memory stores, or generic ORMs when the spec names something specific.\n\n"
            "2. COMPLETENESS: Every endpoint listed in the engineering spec must be implemented in full. "
            "No stubs. No placeholder return values. Real business logic, real DB calls, real error handling.\n\n"
            "3. FIRST FILE IS api-contract.md — REQUIRED:\n"
            "   Your very first output block must be:\n"
            "   === api-contract.md ===\n"
            "   This file documents every endpoint so the frontend agent can connect to it. Include:\n"
            "   - Base URL (e.g. http://localhost:8000/api/v1)\n"
            "   - Auth mechanism (Supabase JWT Bearer, session cookie, etc.)\n"
            "   - Every endpoint: METHOD, path, auth required (yes/no), request body schema, response schema\n"
            "   - Supabase table names and Row Level Security policies if applicable\n"
            "   - All environment variables (name, description, example value)\n\n"
            "4. ENVIRONMENT VARIABLES: All credentials and config must come from env vars. "
            "Generate .env.example with every variable the app needs.\n\n"
            "5. SUPABASE SPECIFICS (if spec uses Supabase):\n"
            "   - Use supabase-py for all DB operations\n"
            "   - Implement Row Level Security policies in a migration file\n"
            "   - Use Supabase Auth for authentication (verify JWTs using Supabase's JWKS)\n"
            "   - Generate supabase/migrations/ SQL files for schema\n\n"
            "6. PRODUCTION QUALITY: Include proper error handling, input validation (Pydantic models), "
            "logging, CORS config, health check endpoint, and graceful startup/shutdown."
        ),
        "=" * 60,
        COMMON_FORMAT_RULE,
        "=" * 60,
        "SPECIFICATION DOCUMENTS (your source of truth — follow these exactly)",
        "=" * 60,
        docs,
    ])

def build_frontend_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "BACKEND API CONTRACT — CONNECT TO THESE EXACT ENDPOINTS\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else
        "WARNING: Backend API contract not yet generated. "
        "Infer endpoints from the engineering spec documents.\n"
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
        (
            "1. TECH STACK: Read the design and architecture documents below. Use EXACTLY the "
            "framework, component library, and styling system named — no substitutions.\n"
            "   - If spec says React + TypeScript: use React with strict TypeScript, no JS files.\n"
            "   - If spec says Next.js: use Next.js App Router or Pages as specified.\n"
            "   - If spec says Tailwind CSS: use Tailwind utility classes, not custom CSS.\n"
            "   - If spec says Supabase Auth: use @supabase/supabase-js for auth on the frontend.\n\n"
            "2. REAL API INTEGRATION — MANDATORY:\n"
            "   Every data fetch, mutation, and auth call MUST use the actual backend endpoints "
            "from the API contract above. NO mock data. NO hardcoded arrays. NO placeholder fetch calls.\n"
            "   - Create a typed API client (e.g. src/lib/api.ts) that wraps all endpoint calls.\n"
            "   - Use the exact request/response shapes from the contract.\n"
            "   - Handle loading, error, and empty states for every async operation.\n\n"
            "3. AUTH WIRING: If the backend uses Supabase Auth, implement the full auth flow:\n"
            "   - Sign in / sign up / sign out using @supabase/supabase-js\n"
            "   - Protected routes that redirect unauthenticated users\n"
            "   - Pass the Supabase session JWT as Bearer token to backend API calls\n\n"
            "4. ENVIRONMENT VARIABLES: Use the correct prefix for your framework:\n"
            "   - Vite: VITE_API_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY\n"
            "   - Next.js: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, etc.\n"
            "   Generate .env.example with all required variables.\n\n"
            "5. EVERY SCREEN FROM THE DESIGN SPEC must be implemented — no missing pages.\n\n"
            "6. PRODUCTION QUALITY: TypeScript strict mode, proper error boundaries, "
            "loading skeletons, form validation, accessible markup (ARIA where needed)."
        ),
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS",
        "=" * 60,
        docs,
    ])

def build_integration_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "BACKEND API CONTRACT\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else ""
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
        (
            "1. TECH STACK: Use ONLY the third-party services and SDKs named in the integration spec.\n\n"
            "2. FULL IMPLEMENTATION: Every integration (Stripe, Slack, email, webhooks, etc.) must be "
            "completely implemented using real SDK calls — no stubs, no TODO comments.\n\n"
            "3. ERROR HANDLING: Every external call must have retry logic, timeout handling, "
            "and structured error logging.\n\n"
            "4. CREDENTIALS: All API keys and secrets must come from environment variables. "
            "Generate .env.example entries for every third-party credential.\n\n"
            "5. WEBHOOK SECURITY: Implement signature verification for all inbound webhooks.\n\n"
            "6. PRODUCTION QUALITY: Idempotency keys for payment operations, "
            "dead-letter handling for async jobs, rate limit awareness."
        ),
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS",
        "=" * 60,
        docs,
    ])

def build_tests_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "BACKEND API CONTRACT — TEST THESE EXACT ENDPOINTS\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else ""
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "SPEC COMPLIANCE RULES — NON-NEGOTIABLE",
        "=" * 60,
        (
            "1. TEST FRAMEWORK: Use ONLY the frameworks named in the quality spec "
            "(e.g. pytest for backend, Playwright or Vitest for frontend).\n\n"
            "2. REAL ENDPOINT TESTING: Backend tests must call the actual API endpoints from the "
            "contract above — no mocking the HTTP layer. Use httpx.AsyncClient or similar.\n\n"
            "3. COVERAGE: Every endpoint in the API contract needs:\n"
            "   - Happy path test (valid input, expect 200/201)\n"
            "   - Auth failure test (missing/invalid token, expect 401)\n"
            "   - Validation failure test (bad input, expect 422)\n"
            "   - At least one edge case (empty list, duplicate, not found)\n\n"
            "4. FIXTURES: Generate reusable pytest fixtures or test factories for "
            "creating test users, workspaces, and data.\n\n"
            "5. E2E TESTS: If Playwright is specified, implement full user journey tests "
            "that exercise the real frontend against a real backend.\n\n"
            "6. CI READY: Tests must pass with `pytest` or `npm test` from the repo root. "
            "Include a conftest.py with DB setup/teardown."
        ),
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS",
        "=" * 60,
        docs,
    ])

def build_infra_prompt(persona, docs, api_contract):
    contract_block = (
        "=" * 60 + "\n"
        "API CONTRACT (use to derive all required env vars and service dependencies)\n"
        "=" * 60 + "\n"
        + api_contract + "\n"
        if api_contract else ""
    )
    return "\n\n".join([
        persona,
        "=" * 60,
        "YOUR MISSION",
        "=" * 60,
        (
            "Read EVERY specification document below. Identify:\n"
            "  - The deployment platform (Fly.io, Vercel, AWS, Railway, etc.)\n"
            "  - Every third-party service used (Supabase, Stripe, Slack, SendGrid, Redis, etc.)\n"
            "  - Every environment variable required by the backend and frontend\n"
            "  - The test framework and what a test run needs (DB, env vars, etc.)\n\n"
            "Then generate a complete, self-contained infrastructure that automates EVERYTHING "
            "except the initial one-time secret values a human must set in GitHub."
        ),
        "=" * 60,
        "MANDATORY OUTPUT FILES",
        "=" * 60,
        (
            "You MUST generate ALL of the following. Read the docs to fill in the specifics.\n\n"

            "1. `.github/workflows/ci.yml` — Pull Request checks:\n"
            "   - Trigger: on pull_request to main\n"
            "   - Jobs: lint, backend-test, frontend-test, e2e\n"
            "   - backend-test: start Supabase local (supabase start), run migrations, run pytest\n"
            "   - frontend-test: npm ci, npm run type-check, npm test\n"
            "   - e2e: run Playwright against a Supabase branch DB (supabase db branch create)\n"
            "   - All secrets injected from GitHub Secrets — NEVER hardcoded\n\n"

            "2. `.github/workflows/deploy.yml` — Deploy pipeline:\n"
            "   - Trigger: on push to main (deploy staging), on release published (deploy production)\n"
            "   - Steps IN ORDER:\n"
            "     a. Run migrations: `supabase db push --project-ref ${{ secrets.SUPABASE_PROJECT_ID }}`\n"
            "     b. Register/update webhooks for each third-party service found in the docs "
            "(Stripe: `stripe listen --forward-to`, Slack: POST to Slack API to register endpoint, etc.)\n"
            "     c. Build and deploy backend to the deployment platform from the docs\n"
            "     d. Build and deploy frontend to the deployment platform from the docs\n"
            "     e. Run smoke tests against the deployed URL\n\n"

            "3. `secrets-required.md` — The ONLY manual step:\n"
            "   A table of every GitHub Secret that must be set manually by the developer, with:\n"
            "   - Secret name (exact GitHub secret key)\n"
            "   - Where to get the value (e.g. 'Supabase Dashboard → Settings → API')\n"
            "   - Which workflow uses it\n"
            "   - Whether it's required for CI, staging, production, or all\n"
            "   Derive this list from the docs — every service mentioned needs its secrets listed.\n\n"

            "4. `supabase/config.toml` — Supabase CLI project config for local dev and CI.\n\n"

            "5. `docker-compose.yml` — Local development stack:\n"
            "   - Every service the app needs (backend, frontend, redis, etc.)\n"
            "   - Healthchecks on every service\n"
            "   - Volumes for persistence\n"
            "   - .env.local loaded via env_file\n\n"

            "6. `Makefile` — Developer commands:\n"
            "   - `make dev` — start full local stack\n"
            "   - `make migrate` — run Supabase migrations locally\n"
            "   - `make test` — run all tests\n"
            "   - `make e2e` — run Playwright\n"
            "   - `make deploy-staging` — trigger staging deploy\n"
            "   - `make setup` — first-time setup (install deps, copy .env.example, supabase start)\n\n"

            "7. `README.md` — Getting started:\n"
            "   - Prerequisites (Node version, Python version, Supabase CLI, etc.)\n"
            "   - `make setup` to get running locally in < 5 minutes\n"
            "   - Link to secrets-required.md for GitHub configuration"
        ),
        "=" * 60,
        "SPEC COMPLIANCE RULES",
        "=" * 60,
        (
            "1. DEPLOYMENT PLATFORM: Use EXACTLY what the operations/architecture docs specify. "
            "If docs say Fly.io, generate fly.toml. If Vercel, generate vercel.json. "
            "If Railway, generate railway.toml. Never substitute.\n\n"
            "2. THIRD-PARTY SERVICES: Every service mentioned in ANY doc must appear in the CI/CD. "
            "If Stripe is in the integration spec, the deploy workflow must register the Stripe webhook. "
            "If Slack is mentioned, the workflow must configure the Slack app endpoint. "
            "If Supabase Storage is mentioned, the workflow must create the required buckets.\n\n"
            "3. SUPABASE MIGRATIONS: Use Supabase CLI (`supabase db push`) — NOT Alembic — for schema changes. "
            "The migration SQL files already exist in `supabase/migrations/`. Run them in CI.\n\n"
            "4. ENVIRONMENT VARIABLES: Every variable from the API contract and docs must appear "
            "in secrets-required.md AND in the workflow env: blocks. No variable may be missing.\n\n"
            "5. NO PLACEHOLDERS: Every workflow step must be complete and runnable. "
            "No `# TODO`, no `YOUR_VALUE_HERE`, no incomplete steps."
        ),
        "=" * 60,
        COMMON_FORMAT_RULE,
        contract_block,
        "=" * 60,
        "SPECIFICATION DOCUMENTS (read all of these to derive the infra)",
        "=" * 60,
        docs,
    ])

def build_prompt_for_step(step, persona, docs, api_contract):
    if step == "backend":
        return build_backend_prompt(persona, docs)
    elif step == "frontend":
        return build_frontend_prompt(persona, docs, api_contract)
    elif step == "integration":
        return build_integration_prompt(persona, docs, api_contract)
    elif step == "tests":
        return build_tests_prompt(persona, docs, api_contract)
    elif step == "infra":
        return build_infra_prompt(persona, docs, api_contract)
    return persona + "\n\n---\n\n## Specification Documents\n\n" + docs

# -----------------------------------------------------------------------
# Step runner
# -----------------------------------------------------------------------

def run_step(step):
    meta = STEPS.get(step)
    if not meta:
        print("[BUILD] Unknown step: " + step)
        sys.exit(1)

    print("[BUILD] Running: " + meta["label"])
    save_step_status(step, "running")

    docs = collect_docs(meta)
    if not docs.strip():
        msg = "No source documents found. Generate and review the spec docs first."
        save_step_status(step, "error", error=msg)
        print("[BUILD] " + msg)
        return False

    api_contract = load_api_contract()
    if step in ("frontend", "integration", "tests") and not api_contract:
        print("[BUILD] WARNING: api-contract.md not found — run backend step first for fully connected output.")

    persona = load_agent(meta["agent"])
    prompt = build_prompt_for_step(step, persona, docs, api_contract)

    tool = os.environ.get("FORGE_TOOL", "gemini")
    model_id = os.environ.get("FORGE_MODEL", "")
    print("[BUILD] Invoking AI (" + tool + " " + (model_id or "default") + ")...")

    output, error = invoke_ai(prompt, tool, model_id)
    if error or not output:
        msg = error or "AI returned empty output"
        save_step_status(step, "error", error=msg)
        print("[BUILD] Error: " + msg)
        return False

    parsed = parse_files(output)
    if not parsed:
        parsed = {"output.md": output}

    out_dir = os.path.join(FORGE_DIR, meta["output_dir"])
    os.makedirs(out_dir, exist_ok=True)

    file_list = []
    for rel_path, content in parsed.items():
        # Save api-contract.md to shared location so frontend/tests can read it
        if step == "backend" and rel_path == "api-contract.md":
            os.makedirs(os.path.dirname(API_CONTRACT_FILE), exist_ok=True)
            with open(API_CONTRACT_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print("[BUILD] API contract saved: " + API_CONTRACT_FILE)

        parts = rel_path.replace("\\", "/").split("/")
        full_path = os.path.join(out_dir, *parts)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        file_list.append(rel_path)
        print("[BUILD] Written: " + rel_path)

    save_step_status(step, "complete", files=file_list)
    print("[BUILD] Done. " + str(len(file_list)) + " files generated.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_runner.py <step>")
        sys.exit(1)
    success = run_step(sys.argv[1])
    sys.exit(0 if success else 1)
"""

TEMPLATE = '''#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from datetime import datetime

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

def invoke_model(prompt, output_path):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
        tmp_path = tmp.name

    try:
        tool = getattr(state, "tool", state.model)
        model_id = getattr(state, "model_id", "")
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

def cmd_dashboard(port=8080):
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
        port = int(args[1]) if len(args) > 1 else 8080
        cmd_dashboard(port)
    elif command == "dev":
        port = int(args[1]) if len(args) > 1 else 8080
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
    )

    forge_content = forge_content.replace("__FORGE_SERVER_PY__", SERVER_PY_CONTENT)
    with open("forge", "w", encoding='utf-8') as f:
        f.write(forge_content)

    # Hot-deploy dashboard.html to all existing .forge/scripts/ directories so
    # a rebuild immediately takes effect without requiring a manual upgrade run.
    import glob
    dashboard_src = os.path.join(os.path.dirname(__file__), "dashboard.html")
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    parent_dir = os.path.dirname(repo_root)
    targets = (
        glob.glob(os.path.join(repo_root, ".forge/scripts/dashboard.html"))
        + glob.glob(os.path.join(repo_root, ".projects/*/.forge/scripts/dashboard.html"))
        + glob.glob(os.path.join(repo_root, "test-projects/*/.forge/scripts/dashboard.html"))
        # Sibling projects in the same parent directory
        + glob.glob(os.path.join(parent_dir, "*/.forge/scripts/dashboard.html"))
    )
    copied = 0
    for dst in targets:
        dst = os.path.normpath(dst)
        if os.path.exists(os.path.dirname(dst)):
            try:
                import shutil
                shutil.copy2(dashboard_src, dst)
                copied += 1
            except Exception:
                pass
    if copied:
        print(f"Dashboard hot-deployed to {copied} runtime director{'y' if copied==1 else 'ies'}.")

    print("forge built successfully.")

if __name__ == "__main__":
    build_forge()
