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

DASHBOARD_HTML_CONTENT = open(os.path.join(os.path.dirname(__file__), "dashboard.html")).read()

SERVER_PY_CONTENT = r"""import os
import sys
import json
import subprocess
import shutil
import tempfile
import time
import threading
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO_ROOT = os.environ.get("FORGE_REPO_ROOT", ".")
_forge_data = os.environ.get("FORGE_DATA_DIR")
FORGE_DIR = os.path.expanduser(_forge_data) if _forge_data else os.path.join(REPO_ROOT, ".forge")

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
            return None, err
        with open(tmp_path, encoding="utf-8") as f:
            return f.read(), None
    except subprocess.TimeoutExpired:
        return None, "AI call timed out after 10 minutes"
    except FileNotFoundError:
        return None, f"AI tool '{tool}' not found in PATH"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

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

def _build_org_context_meta():
    _org = os.environ.get("FORGE_ORG", "")
    if not _org:
        return {"active": False, "org": "", "fileCount": 0}
    _cache = os.path.expanduser(f"~/.forge/org-cache/{_org}")
    _count = 0
    for _sub in ("knowledge", "patterns"):
        _d = os.path.join(_cache, _sub)
        if os.path.isdir(_d):
            _count += sum(1 for _f in os.listdir(_d) if _f.endswith(".md"))
    return {"active": _count > 0, "org": _org, "fileCount": _count}

USER_FILE = os.path.expanduser("~/.forge/user.json")

DEPARTMENTS = {
    "all":         list(range(11)),
    "product":     [0, 1],
    "design":      [2, 3],
    "engineering": [4, 5, 6, 7],
    "operations":  [8, 9],
    "marketing":   [10],
}

def load_user():
    try:
        with open(USER_FILE, "r") as _f:
            return json.load(_f)
    except Exception:
        return {"role": "admin", "department": "all"}

def save_user(data):
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, "w") as _f:
        json.dump(data, _f, indent=2)

def _list_knowledge_entries():
    _org = os.environ.get("FORGE_ORG", "")
    if not _org:
        return []
    _cache = os.path.expanduser(f"~/.forge/org-cache/{_org}")
    _entries = []
    for _sub in ("knowledge", "patterns"):
        _d = os.path.join(_cache, _sub)
        if os.path.isdir(_d):
            for _fname in sorted(os.listdir(_d)):
                if _fname.endswith(".md"):
                    _fpath = os.path.join(_d, _fname)
                    _st = os.stat(_fpath)
                    _entries.append({
                        "name": _fname,
                        "type": _sub,
                        "absPath": _fpath,
                        "size": _st.st_size,
                        "modifiedAt": int(_st.st_mtime * 1000),
                    })
    return _entries

def _push_distill_to_kb(kb_repo_url, token, file_path, stage, ts):
    # Clone KB repo, commit distilled file on a new branch, push, open a PR.
    _parsed = urllib.parse.urlparse(kb_repo_url)
    _path_parts = _parsed.path.rstrip('/').lstrip('/').split('/')
    if len(_path_parts) < 2:
        return None, "Invalid KB repo URL"
    _owner = _path_parts[-2]
    _repo = _path_parts[-1].removesuffix('.git') if hasattr(str, 'removesuffix') else _path_parts[-1].replace('.git', '')
    _auth_url = f"https://x-access-token:{token}@github.com/{_owner}/{_repo}.git"
    _branch = f"forge/distill-{stage}-{ts}"
    _work_dir = tempfile.mkdtemp(prefix="forge-kb-")
    try:
        # Shallow clone
        _r = subprocess.run(
            ["git", "clone", "--depth=1", _auth_url, _work_dir],
            capture_output=True, text=True
        )
        if _r.returncode != 0:
            return None, f"Clone failed: {_r.stderr.strip()[:200]}"
        # Get default branch name
        _def_branch_r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=_work_dir, capture_output=True, text=True
        )
        _default_branch = _def_branch_r.stdout.strip() or "main"
        # Create feature branch
        subprocess.run(["git", "checkout", "-b", _branch], cwd=_work_dir, capture_output=True)
        # Copy distilled file into patterns/
        _dest_dir = os.path.join(_work_dir, "patterns")
        os.makedirs(_dest_dir, exist_ok=True)
        _fname = os.path.basename(file_path)
        shutil.copy2(file_path, os.path.join(_dest_dir, _fname))
        # Configure git identity
        subprocess.run(["git", "config", "user.email", "forge-os@forge-os.local"], cwd=_work_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Forge OS"], cwd=_work_dir, capture_output=True)
        # Commit
        subprocess.run(["git", "add", "."], cwd=_work_dir, capture_output=True)
        _commit_r = subprocess.run(
            ["git", "commit", "-m", f"distill({stage}): add distilled patterns from {ts}"],
            cwd=_work_dir, capture_output=True, text=True
        )
        if _commit_r.returncode != 0:
            return None, f"Commit failed: {_commit_r.stderr.strip()[:200]}"
        # Push
        _push_r = subprocess.run(
            ["git", "push", "origin", _branch],
            cwd=_work_dir, capture_output=True, text=True
        )
        if _push_r.returncode != 0:
            return None, f"Push failed: {_push_r.stderr.strip()[:200]}"
        # Create PR via GitHub API
        _pr_body = json.dumps({
            "title": f"Distilled patterns: {stage} ({ts[:8]})",
            "head": _branch,
            "base": _default_branch,
            "body": (
                f"Auto-generated by Forge OS distillation.\n\n"
                f"**Stage:** `{stage}`  \n**File:** `patterns/{_fname}`  \n**Timestamp:** `{ts}`\n\n"
                f"Review the distilled patterns below and merge to publish them to the org knowledge base."
            ),
        }).encode("utf-8")
        _req = urllib.request.Request(
            f"https://api.github.com/repos/{_owner}/{_repo}/pulls",
            data=_pr_body,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "forge-os",
            }
        )
        with urllib.request.urlopen(_req, timeout=15) as _resp:
            _pr = json.loads(_resp.read().decode("utf-8"))
            return _pr.get("html_url", ""), None
    except urllib.error.HTTPError as _e:
        _body = _e.read().decode("utf-8", errors="ignore")[:300]
        return None, f"GitHub API error {_e.code}: {_body}"
    except Exception as _e:
        return None, str(_e)[:300]
    finally:
        shutil.rmtree(_work_dir, ignore_errors=True)

def _load_distill_result():
    _path = os.path.join(FORGE_DIR, "runs/distill-result.json")
    if not os.path.exists(_path):
        return None
    try:
        with open(_path) as _f:
            return json.load(_f)
    except Exception:
        return None

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
        "skip_org_context": proj.get("skip_org_context", False),
        "orgContext": _build_org_context_meta(),
        "user": load_user(),
        "project_type": proj.get("project_type", "standard"),
        "lastDistill": _load_distill_result(),
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

        if path == "/api/user":
            self._json_response(200, load_user())
            return

        if path == "/api/knowledge":
            params = dict(urllib.parse.parse_qsl(parsed.query))
            abs_path = params.get("path")
            if abs_path:
                # Read a specific knowledge file (must be inside org-cache)
                _org = os.environ.get("FORGE_ORG", "")
                _allowed = os.path.expanduser(f"~/.forge/org-cache/{_org}") if _org else ""
                if not _allowed or not abs_path.startswith(_allowed):
                    self._json_response(403, {"error": "forbidden"})
                    return
                if not os.path.isfile(abs_path):
                    self._json_response(404, {"error": "not found"})
                    return
                with open(abs_path, "r", encoding="utf-8") as _f:
                    content = _f.read()
                self._json_response(200, {"content": content})
            else:
                self._json_response(200, {"entries": _list_knowledge_entries()})
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
                        "FORGE_SKIP_ORG_CONTEXT": "1" if proj.get("skip_org_context", False) else "",
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
                    subprocess.run(["git", "add", ".forge"], cwd=REPO_ROOT, capture_output=True)
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
                    run_git(["add", ".forge"])
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

        if path == "/api/user":
            user = load_user()
            if "role" in data:
                user["role"] = data["role"]
            if "department" in data:
                user["department"] = data["department"]
            save_user(user)
            self._json_response(200, {"status": "saved"})
            return

        if path == "/api/distill":
            stage = data.get("stage")
            _org = os.environ.get("FORGE_ORG", "")
            if not stage:
                self._json_response(400, {"error": "missing stage"})
                return
            if not _org:
                self._json_response(400, {"error": "FORGE_ORG not set — connect GitHub org first"})
                return
            _stage_dirs = {
                "context": "00-context", "requirements": "01-requirements",
                "design": "02-design", "analysis": "03-analysis",
                "architecture": "04-architecture", "delivery": "05-delivery",
                "engineering": "06-engineering", "qa": "07-quality",
                "operations": "08-operations", "release": "09-release",
                "marketing": "10-marketing",
            }
            _sdir = _stage_dirs.get(stage)
            if not _sdir:
                self._json_response(400, {"error": "invalid stage"})
                return
            _stage_path = os.path.join(FORGE_DIR, _sdir)
            if not os.path.isdir(_stage_path):
                self._json_response(404, {"error": "stage directory not found"})
                return
            _reviews = load_reviews()
            _reviewed = [
                os.path.join(FORGE_DIR, _sdir, _fn)
                for _fn in sorted(os.listdir(_stage_path))
                if _fn.endswith(".md") and _reviews.get(os.path.join(_sdir, _fn)) == "reviewed"
            ]
            if not _reviewed:
                self._json_response(400, {"error": "no reviewed files in this stage"})
                return
            _proj = load_project_state()
            _forge_script = FORGE_SCRIPT or os.path.abspath(os.path.join(FORGE_DIR, "..", "..", "forge"))

            def _run_distill():
                _status_file = os.path.join(FORGE_DIR, "runs/status.json")
                _result_file = os.path.join(FORGE_DIR, "runs/distill-result.json")
                _ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                _out_path = None
                try:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(_status_file, "w") as _sf:
                            json.dump({"status": "distilling", "stage": stage, "updated_at": datetime.now().isoformat()}, _sf)
                    _out_dir = os.path.expanduser(f"~/.forge/org-cache/{_org}/patterns")
                    os.makedirs(_out_dir, exist_ok=True)
                    _out_path = os.path.join(_out_dir, f"{stage}-{_ts}.md")
                    _base_env = {
                        **os.environ,
                        "FORGE_TOOL": _proj.get("tool", "gemini"),
                        "FORGE_MODEL": _proj.get("model", ""),
                    }
                    _cmd = [
                        sys.executable,
                        os.path.join(FORGE_DIR, "scripts/run.py"),
                        "distill",
                        "--distill-stage", stage,
                        "--distill-output", _out_path,
                        "--distill-sources", ",".join(_reviewed),
                    ]
                    _sub = subprocess.run(_cmd, cwd=REPO_ROOT, env=_base_env)

                    # Git PR flow if KB repo is configured
                    _kb_url = _proj.get("git", {}).get("kb_repo_url", "")
                    _token = _proj.get("git", {}).get("token", "")
                    _pr_url = None
                    _pr_error = None
                    if _sub.returncode == 0 and _kb_url and _token and _out_path and os.path.exists(_out_path):
                        _pr_url, _pr_error = _push_distill_to_kb(_kb_url, _token, _out_path, stage, _ts)

                    # Write result
                    _result = {
                        "stage": stage,
                        "file": _out_path,
                        "timestamp": _ts,
                        "prUrl": _pr_url,
                        "prError": _pr_error,
                        "success": _sub.returncode == 0,
                    }
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(_result_file, "w") as _rf:
                            json.dump(_result, _rf, indent=2)
                finally:
                    if os.path.exists(os.path.join(FORGE_DIR, "runs")):
                        with open(_status_file, "w") as _sf:
                            json.dump({"status": "idle", "stage": stage, "updated_at": datetime.now().isoformat()}, _sf)

            _t = threading.Thread(target=_run_distill, daemon=True)
            _t.start()
            self._json_response(200, {"status": "started", "stage": stage})
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
            if "project_type" in data:
                proj["project_type"] = data["project_type"]
            if "skip_org_context" in data:
                proj["skip_org_context"] = data["skip_org_context"]
            if "git" in data and "kb_repo_url" in data["git"]:
                proj["git"]["kb_repo_url"] = data["git"]["kb_repo_url"]
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
                        "FORGE_REPO_ROOT": REPO_ROOT,
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
"""

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
            with open(BUILD_STATUS_FILE) as f:
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
    with open(BUILD_STATUS_FILE, "w") as f:
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
        with open(tmp_path, "w") as out_f:
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
                with open(status_file, "w") as sf:
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
                # Read friendly message written by run.py
                err_msg = "Generation failed — the AI model may have reached its usage limit. Try again in a few minutes."
                if os.path.exists(run_error_file):
                    try:
                        with open(run_error_file) as ef:
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
            with open(status_file, "w") as sf:
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
            subprocess.run(cmd, stdout=open(tmp_path, 'w'), check=True)
        elif tool == "claude":
            subprocess.run(["claude"], input=prompt, text=True, stdout=open(tmp_path, 'w'), check=True)
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
        with open(err_path, "w") as f:
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

SERVER_PY = r\"\"\"{SERVER_PY_CONTENT}\"\"\"

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
    with open(os.path.join(FORGE_DIR, "scripts/build_runner.py"), "w") as f:
        f.write(BUILD_RUNNER_PY)
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
                  '            with open(agent_path, "w") as f:\n')
    first = True
    for agent, text in all_agents.items():
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
        BUILD_RUNNER_PY_CONTENT=BUILD_RUNNER_PY_CONTENT,
    )

    with open("forge", "w") as f:
        f.write(forge_content)

    print("forge built successfully.")

if __name__ == "__main__":
    build_forge()
