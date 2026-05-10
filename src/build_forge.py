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
import time
import threading
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", ".")
FORGE_DIR = os.path.join(REPO_ROOT, ".forge")

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
                import shutil
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
'''Build system runner - generates code from reviewed spec documents.
Usage: python3 scripts/build_runner.py <step>
'''
import os, sys, json, subprocess, tempfile
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FORGE_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", os.path.dirname(FORGE_DIR))
BUILD_STATUS_FILE = os.path.join(FORGE_DIR, "runs", "build-system.json")

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
        "source_dirs": ["02-design"],
        "source_files": ["01-requirements/prd.md", "06-engineering/frontend-spec.md"],
        "output_dir": "15-build/frontend",
    },
    "integration": {
        "label": "Integration Layer",
        "agent": "integration-engineer",
        "source_dirs": [],
        "source_files": [
            "04-architecture/api-design.md",
            "06-engineering/integration-spec.md",
            "06-engineering/backend-spec.md",
        ],
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
        "source_dirs": ["08-operations"],
        "source_files": ["04-architecture/deployment-architecture.md"],
        "output_dir": "15-build/infra",
    },
}

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
    '''Strip known bad prefixes the AI sometimes emits and reject invalid paths.'''
    p = candidate.strip()
    # Reject paths with spaces after the name (e.g. "file.json (update)")
    if " (" in p or p.endswith(")"):
        return None
    # Strip leading 15-build/<anything>/ prefix — AI sometimes outputs full project paths
    parts = p.replace("\\", "/").split("/")
    if parts and parts[0] == "15-build":
        parts = parts[2:]  # drop "15-build" and the step name
    # Strip leading .forge/ prefix
    if parts and parts[0] == ".forge":
        parts = parts[1:]
    # Reject empty or path-traversal attempts
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
                current_path = clean  # None = skip this block
                current_lines = []
        elif current_path:
            current_lines.append(line)
    if current_path and not current_path.startswith("SOURCE:"):
        files[current_path] = "\n".join(current_lines).strip()
    return files

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

    persona = load_agent(meta["agent"])
    prompt = (persona + "\n\n---\n\n## Your Task\n\n"
              "Based on the specification documents below, generate a complete, working "
              + meta["label"] + " implementation.\n\n"
              "Use the output format described in your agent definition:\n"
              "=== path/to/filename.ext ===\n"
              "<file content>\n\n"
              "Include every file needed. Start with README.md.\n\n"
              "---\n\n## Specification Documents\n\n" + docs)

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
REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", ".")
LOG_LEVEL = os.environ.get("AEOS_LOG_LEVEL", "info")
os.environ["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
AGENTS_DIR = os.path.join(REPO_ROOT, "11-agents")
VERSIONS_DIR = os.path.join(REPO_ROOT, "versions")
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
