import os
from pprint import pformat

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

DASHBOARD_HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Forge Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #21262d;
  --bg-card: #1c2128;
  --border-color: #30363d;
  --border-accent: #3b82f6;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --accent-blue: #3b82f6;
  --accent-green: #22c55e;
  --accent-amber: #f59e0b;
  --accent-red: #ef4444;
  --accent-purple: #a855f7;
  --radius: 8px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --transition: all 0.2s ease;
  --browser-top-inset: 56px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: var(--browser-top-inset);
}

.app-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
}

.app-header h1 {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.runtime-panel {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-tertiary);
}

.runtime-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.runtime-field label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.runtime-panel select,
.runtime-panel input {
  min-width: 160px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12px;
  font-family: inherit;
}

.runtime-panel input::placeholder {
  color: var(--text-muted);
}

.runtime-panel select:focus,
.runtime-panel input:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.runtime-help {
  font-size: 11px;
  color: var(--text-muted);
  max-width: 320px;
}

.header-actions button {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 6px 14px;
  border-radius: var(--radius);
  font-size: 13px;
  cursor: pointer;
  transition: var(--transition);
  font-family: inherit;
}

.header-actions button:hover {
  background: var(--accent-blue);
  color: #fff;
  border-color: var(--accent-blue);
}

.app-layout {
  flex-grow: 1;
  display: grid;
  grid-template-columns: 280px 1fr;
  overflow: hidden;
}

.sidebar {
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  padding: 16px 0;
}

.sidebar-section {
  margin-bottom: 8px;
}

.sidebar-section-title {
  padding: 8px 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
}

.stage-item {
  padding: 8px 20px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: var(--transition);
  color: var(--text-secondary);
  border-left: 3px solid transparent;
}

.stage-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.stage-item.active {
  background: rgba(59,130,246,0.08);
  color: var(--accent-blue);
  border-left-color: var(--accent-blue);
}

.stage-item .indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.stage-item .indicator.populated { background: var(--accent-green); }
.stage-item .indicator.empty { background: var(--text-muted); }
.stage-item .indicator.partial { background: var(--accent-amber); }
.stage-item .indicator.needs_review {
  background: var(--accent-amber);
  box-shadow: 0 0 0 3px rgba(245,158,11,0.14);
}
.stage-item .indicator.reviewed {
  background: var(--accent-green);
  box-shadow: 0 0 0 3px rgba(34,197,94,0.14);
}
.stage-item .indicator.ready {
  background: var(--accent-green);
  box-shadow: 0 0 0 3px rgba(34,197,94,0.14);
}
.stage-item .indicator.updated {
  background: var(--accent-amber);
  box-shadow: 0 0 0 3px rgba(245,158,11,0.14);
}

.file-item {
  padding: 6px 20px 6px 44px;
  font-size: 12px;
  cursor: pointer;
  color: var(--text-muted);
  transition: var(--transition);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.file-item.active {
  color: var(--accent-blue);
  background: rgba(59,130,246,0.05);
}

.file-item.empty-file {
  opacity: 0.5;
}

.main-content {
  overflow-y: auto;
  padding: 24px 32px;
}

.gates-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.gate-chip {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 6px;
}

.gate-chip.passed {
  background: rgba(34,197,94,0.12);
  border-color: rgba(34,197,94,0.3);
  color: var(--accent-green);
}

.gate-chip.pending {
  background: rgba(245,158,11,0.12);
  border-color: rgba(245,158,11,0.3);
  color: var(--accent-amber);
}

.gate-chip:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.gate-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.gate-chip.passed .gate-dot { background: var(--accent-green); }
.gate-chip.pending .gate-dot { background: var(--accent-amber); }

.content-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
}

.content-header {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-secondary);
}

.content-header h2 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.content-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.content-body {
  padding: 28px 32px;
  font-size: 15px;
  line-height: 1.85;
  color: var(--text-secondary);
  min-height: 280px;
  max-height: 68vh;
  overflow-y: auto;
  background:
    radial-gradient(circle at top right, rgba(59,130,246,0.08), transparent 28%),
    linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0));
}

.content-body:empty::after {
  content: 'Select a file from the sidebar to view its contents.';
  color: var(--text-muted);
  font-style: italic;
  font-family: 'Inter', sans-serif;
}

.markdown-preview {
  max-width: 860px;
  margin: 0 auto;
}

.markdown-preview > *:first-child {
  margin-top: 0;
}

.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3,
.markdown-preview h4 {
  color: var(--text-primary);
  letter-spacing: -0.03em;
  line-height: 1.2;
  margin: 1.4em 0 0.65em;
}

.markdown-preview h1 {
  font-size: 34px;
  font-weight: 700;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.markdown-preview h2 {
  font-size: 24px;
  font-weight: 650;
}

.markdown-preview h3 {
  font-size: 18px;
  font-weight: 650;
}

.markdown-preview h4 {
  font-size: 15px;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--accent-blue);
}

.markdown-preview p,
.markdown-preview li {
  color: var(--text-secondary);
  font-size: 15px;
}

.markdown-preview p {
  margin: 0 0 1.1em;
}

.markdown-preview ul,
.markdown-preview ol {
  margin: 0 0 1.25em 1.25em;
  padding: 0;
}

.markdown-preview li + li {
  margin-top: 0.45em;
}

.markdown-preview strong {
  color: var(--text-primary);
  font-weight: 650;
}

.markdown-preview em {
  color: #c9d6e3;
}

.markdown-preview a {
  color: #7cc4ff;
  text-decoration: none;
  border-bottom: 1px solid rgba(124,196,255,0.35);
}

.markdown-preview a:hover {
  color: #a7dbff;
  border-bottom-color: rgba(167,219,255,0.75);
}

.markdown-preview hr {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
  margin: 2em 0;
}

.markdown-preview blockquote {
  margin: 1.4em 0;
  padding: 16px 18px;
  border-left: 3px solid var(--accent-blue);
  background: rgba(59,130,246,0.08);
  border-radius: 0 12px 12px 0;
  color: #c7d7ea;
}

.markdown-preview code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.92em;
}

.markdown-preview p code,
.markdown-preview li code,
.markdown-preview td code,
.markdown-preview blockquote code {
  padding: 0.18em 0.42em;
  border-radius: 6px;
  background: rgba(255,255,255,0.06);
  color: #f7d794;
}

.markdown-preview pre {
  margin: 1.25em 0;
  padding: 18px 20px;
  border-radius: 16px;
  overflow-x: auto;
  background: linear-gradient(180deg, rgba(8,15,28,0.92), rgba(17,24,39,0.94));
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}

.markdown-preview pre code {
  color: #dbeafe;
  display: block;
  line-height: 1.7;
}

.markdown-preview table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.4em 0 1.8em;
  overflow: hidden;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.025);
}

.markdown-preview th,
.markdown-preview td {
  text-align: left;
  padding: 12px 14px;
  vertical-align: top;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.markdown-preview th {
  background: rgba(59,130,246,0.1);
  color: var(--text-primary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.markdown-preview tr:last-child td {
  border-bottom: none;
}

.markdown-preview .empty-file {
  color: var(--text-muted);
  font-style: italic;
}

.review-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
}
.review-bar button {
  padding: 4px 14px;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  cursor: pointer;
  font-weight: 500;
}
.btn-reviewed { background: var(--accent-green); color: #fff; }
.btn-needs-review { background: var(--accent-amber); color: #fff; }
.review-status-label { font-size: 12px; }
.stage-progress { font-size: 10px; color: var(--text-muted); margin-left: 6px; }

.critique-panel {
  margin-top: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
}

.critique-panel h3 {
  padding: 14px 20px;
  font-size: 13px;
  font-weight: 600;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.critique-input-area {
  padding: 16px 20px;
  display: flex;
  gap: 12px;
}

.critique-input-area textarea {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  padding: 10px 14px;
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
  min-height: 60px;
  transition: var(--transition);
}

.critique-input-area textarea:focus {
  outline: none;
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
}

.critique-input-area textarea::placeholder {
  color: var(--text-muted);
}

.btn-send {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  font-family: inherit;
  align-self: flex-end;
  white-space: nowrap;
}

.btn-send:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(59,130,246,0.3);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.status-banner {
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  animation: fadeIn 0.3s ease;
}

.status-banner.success {
  background: rgba(34,197,94,0.12);
  color: var(--accent-green);
  border-top: 1px solid rgba(34,197,94,0.2);
}

.status-banner.error {
  background: rgba(239,68,68,0.12);
  color: var(--accent-red);
  border-top: 1px solid rgba(239,68,68,0.2);
}

.status-banner.loading {
  background: rgba(59,130,246,0.12);
  color: var(--accent-blue);
  border-top: 1px solid rgba(59,130,246,0.2);
}

.empty-state {
  text-align: center;
  padding: 80px 40px;
  color: var(--text-muted);
}

.empty-state h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.sidebar::-webkit-scrollbar,
.content-body::-webkit-scrollbar,
.main-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-thumb,
.content-body::-webkit-scrollbar-thumb,
.main-content::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover,
.content-body::-webkit-scrollbar-thumb:hover,
.main-content::-webkit-scrollbar-thumb:hover {
  background: var(--border-color);
}

.stage-item .indicator.generating { 
  background: var(--accent-blue); 
  animation: pulse 1.5s infinite;
  box-shadow: 0 0 8px var(--accent-blue);
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.processing-banner {
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.3);
  color: var(--accent-blue);
  padding: 10px 16px;
  border-radius: var(--radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(59,130,246,0.3);
  border-top-color: var(--accent-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
</head>
<body>

<header class="app-header">
  <h1>Forge Dashboard</h1>
  <div class="header-actions">
    <div class="runtime-panel">
      <div class="runtime-field">
        <label for="toolSelect">AI Tool</label>
        <select id="toolSelect"></select>
      </div>
      <div class="runtime-field">
        <label for="modelInput">Model</label>
        <input id="modelInput" type="text" placeholder="Optional model override">
      </div>
      <button id="saveRuntimeButton" onclick="saveRuntime()">Save Runtime</button>
    </div>
    <button onclick="loadState()">Refresh</button>
  </div>
</header>

<div class="app-layout">
  <nav class="sidebar" id="sidebar"></nav>
  <main class="main-content">
    <div class="gates-bar" id="gatesBar"></div>
    <div class="runtime-help" id="runtimeHelp"></div>
    <div id="liveProcessingBanner" style="display:none"></div>
    <div class="content-panel">
      <div class="review-bar" id="reviewBar" style="display:none">
        <button id="reviewToggleBtn" onclick="toggleReview()">Mark as Reviewed</button>
        <span class="review-status-label" id="reviewStatusLabel"></span>
      </div>
      <div class="content-header">
        <h2 id="contentTitle">Select a file</h2>
        <div class="content-meta" id="contentMeta"></div>
      </div>
      <div class="content-body" id="contentBody"></div>
      <div id="statusBanner"></div>
    </div>
    <div class="critique-panel" id="critiquePanel" style="display:none">
      <h3>AI Critique / Fix Request</h3>
      <div class="critique-input-area">
        <textarea id="critiqueInput" placeholder="Describe the issue or improvement you want the AI to make to this file..."></textarea>
        <button class="btn-send" id="btnSend" onclick="sendCritique()">Send to AI</button>
      </div>
    </div>
  </main>
</div>

<script>
var currentFile = null;
var stateData = null;
var runtimeOptions = [];

var STAGE_LABELS = {
  '00-context': 'Context',
  '01-requirements': 'Requirements',
  '02-design': 'Design',
  '03-analysis': 'Analysis',
  '04-architecture': 'Architecture',
  '05-delivery': 'Delivery',
  '06-engineering': 'Engineering',
  '07-quality': 'Quality',
  '08-operations': 'Operations',
  '09-release': 'Release',
  '10-marketing': 'Marketing'
};

var FILE_STATUS_COPY = {
  generating: { label: 'Generating', description: 'This file is being created right now.' },
  empty: { label: 'Empty', description: 'No content yet. Run ./forge generate to start.' },
  needs_review: { label: 'Needs Review', description: 'AI-generated. Review and approve before the gate passes.' },
  reviewed: { label: 'Reviewed', description: 'Approved. Gate auto-passes when all stage files are reviewed.' },
  updated: { label: 'Recently updated', description: 'This file has content and changed recently.' },
  ready: { label: 'Generated', description: 'This file has content and is not recently changed.' }
};

var runtimeInitialized = false;
var stageReviewSummary = {};
var currentFileStatus = 'empty';

function loadState(forceRenderRuntime) {
  fetch('/api/state')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      stateData = data;
      runtimeOptions = data.runtime ? data.runtime.options || [] : [];
      stageReviewSummary = data.stageReviewSummary || {};
      if (!runtimeInitialized || forceRenderRuntime) {
        renderRuntime(data.runtime);
        runtimeInitialized = true;
      }
      renderGates(data.gates);
      renderSidebar(data.tree, data.processing);
      renderProcessing(data.processing);
    })
    .catch(function(err) {
      console.error('Failed to load state:', err);
    });
}

function renderRuntime(runtime) {
  var toolSelect = document.getElementById('toolSelect');
  var modelInput = document.getElementById('modelInput');
  var runtimeHelp = document.getElementById('runtimeHelp');
  var current = runtime && runtime.current ? runtime.current : { tool: '', model: '' };
  var options = runtime && runtime.options ? runtime.options : [];

  toolSelect.innerHTML = '';
  for (var i = 0; i < options.length; i++) {
    var optionData = options[i];
    var option = document.createElement('option');
    option.value = optionData.id;
    option.textContent = optionData.label + (optionData.available ? '' : ' (unavailable)');
    option.disabled = !optionData.available || !optionData.supported;
    if (optionData.id === current.tool) {
      option.selected = true;
    }
    toolSelect.appendChild(option);
  }

  modelInput.value = current.model || '';
  updateRuntimeHelp();
}

function updateRuntimeHelp() {
  var toolSelect = document.getElementById('toolSelect');
  var runtimeHelp = document.getElementById('runtimeHelp');
  var selectedTool = toolSelect.value;
  for (var i = 0; i < runtimeOptions.length; i++) {
    if (runtimeOptions[i].id === selectedTool) {
      runtimeHelp.textContent = runtimeOptions[i].description;
      return;
    }
  }
  runtimeHelp.textContent = '';
}

function renderGates(gates) {
  var bar = document.getElementById('gatesBar');
  bar.innerHTML = '';
  var gateNames = Object.keys(gates).sort();
  for (var i = 0; i < gateNames.length; i++) {
    var name = gateNames[i];
    var status = gates[name];
    var isPassed = status === 'PASSED';
    var chip = document.createElement('div');
    chip.className = 'gate-chip ' + (isPassed ? 'passed' : 'pending');
    chip.setAttribute('data-gate', name);
    chip.innerHTML = '<span class="gate-dot"></span>' + name.replace('-gate', '').replace(/-/g, ' ');
    chip.onclick = (function(n, p) {
      return function() {
        if (!p) { toggleGate(n); }
      };
    })(name, isPassed);
    bar.appendChild(chip);
  }
}

function renderSidebar(tree, processing) {
  var sidebar = document.getElementById('sidebar');
  sidebar.innerHTML = '';
  var stages = Object.keys(tree).sort();
  for (var i = 0; i < stages.length; i++) {
    var stage = stages[i];
    var files = tree[stage].slice().sort(function(a, b) {
      var aName = typeof a === 'string' ? a : a.name;
      var bName = typeof b === 'string' ? b : b.name;
      return aName.localeCompare(bName);
    });
    var section = document.createElement('div');
    section.className = 'sidebar-section';
    var title = document.createElement('div');
    title.className = 'sidebar-section-title';
    var labelText = STAGE_LABELS[stage] || stage;
    var summary = stageReviewSummary[stage];
    if (summary && summary.total > 0) {
      var prog = document.createElement('span');
      prog.className = 'stage-progress';
      prog.textContent = '(' + summary.reviewed + '/' + summary.total + ')';
      title.textContent = labelText;
      title.appendChild(prog);
    } else {
      title.textContent = labelText;
    }
    section.appendChild(title);

    for (var j = 0; j < files.length; j++) {
      var fileEntry = files[j];
      var fileName = typeof fileEntry === 'string' ? fileEntry : fileEntry.name;
      var fileStatus = typeof fileEntry === 'string' ? 'empty' : fileEntry.status;
      var fPath = stage + '/' + fileName;
      var fileDiv = document.createElement('div');
      fileDiv.className = 'file-item stage-item';
      var statusMeta = FILE_STATUS_COPY[fileStatus] || FILE_STATUS_COPY.empty;
      
      var indicatorHTML = '';
      if (processing && processing.status === 'generating' && processing.file === fPath) {
        indicatorHTML = '<span class="indicator generating" style="display:inline-block; width:6px; height:6px; border-radius:50%; margin-right:8px;"></span>';
        fileDiv.classList.add('active');
        fileDiv.title = FILE_STATUS_COPY.generating.description;
      } else {
        indicatorHTML = '<span class="indicator ' + fileStatus + '" style="display:inline-block; width:6px; height:6px; border-radius:50%; margin-right:8px;"></span>';
        if (fileStatus === 'empty') {
          fileDiv.classList.add('empty-file');
        }
        fileDiv.title = statusMeta.description;
      }
      
      fileDiv.innerHTML = indicatorHTML + fileName.replace('.md', '');
      fileDiv.setAttribute('data-path', fPath);
      fileDiv.onclick = (function(p) {
        return function() { loadFile(p); };
      })(fPath);
      section.appendChild(fileDiv);
    }
    sidebar.appendChild(section);
  }
}

function renderProcessing(processing) {
  var banner = document.getElementById('liveProcessingBanner');
  if (processing && processing.status === 'generating') {
    banner.style.display = 'flex';
    banner.className = 'processing-banner';
    banner.innerHTML = '<div class="spinner"></div><span><b>Generating:</b> ' + processing.stage + ' &rarr; ' + processing.file + '</span>';
  } else {
    banner.style.display = 'none';
  }
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderInlineMarkdown(text) {
  var escaped = escapeHtml(text);
  escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
  escaped = escaped.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  escaped = escaped.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  escaped = escaped.replace(/(^|[^\*])\*([^*]+)\*(?!\*)/g, '$1<em>$2</em>');
  escaped = escaped.replace(/(^|[^_])_([^_]+)_(?!_)/g, '$1<em>$2</em>');
  return escaped;
}

function isTableSeparator(line) {
  return /^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$/.test(line);
}

function renderTable(lines, startIndex) {
  if (startIndex + 1 >= lines.length) {
    return null;
  }
  if (lines[startIndex].indexOf('|') === -1 || !isTableSeparator(lines[startIndex + 1])) {
    return null;
  }

  var rows = [];
  var index = startIndex;
  while (index < lines.length && lines[index].indexOf('|') !== -1 && lines[index].trim() !== '') {
    rows.push(lines[index]);
    index += 1;
  }

  if (rows.length < 2) {
    return null;
  }

  function splitRow(row) {
    return row
      .trim()
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map(function(cell) { return renderInlineMarkdown(cell.trim()); });
  }

  var headerCells = splitRow(rows[0]);
  var bodyRows = rows.slice(2).map(splitRow);
  var html = '<table><thead><tr>';
  for (var i = 0; i < headerCells.length; i++) {
    html += '<th>' + headerCells[i] + '</th>';
  }
  html += '</tr></thead><tbody>';
  for (var j = 0; j < bodyRows.length; j++) {
    html += '<tr>';
    for (var k = 0; k < bodyRows[j].length; k++) {
      html += '<td>' + bodyRows[j][k] + '</td>';
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  return { html: html, nextIndex: index };
}

function renderMarkdown(markdown) {
  if (!markdown || !markdown.trim()) {
    return '<div class="markdown-preview"><p class="empty-file">(empty file)</p></div>';
  }

  var normalized = markdown.replace(/\r\n/g, '\n');
  var lines = normalized.split('\n');
  var html = [];
  var paragraph = [];
  var listType = '';
  var listItems = [];
  var inCodeBlock = false;
  var codeBuffer = [];

  function flushParagraph() {
    if (!paragraph.length) {
      return;
    }
    html.push('<p>' + renderInlineMarkdown(paragraph.join(' ')) + '</p>');
    paragraph = [];
  }

  function flushList() {
    if (!listItems.length) {
      return;
    }
    var tag = listType === 'ol' ? 'ol' : 'ul';
    html.push('<' + tag + '><li>' + listItems.join('</li><li>') + '</li></' + tag + '>');
    listItems = [];
    listType = '';
  }

  function flushCodeBlock() {
    if (!inCodeBlock) {
      return;
    }
    html.push('<pre><code>' + escapeHtml(codeBuffer.join('\n')) + '</code></pre>');
    inCodeBlock = false;
    codeBuffer = [];
  }

  for (var index = 0; index < lines.length; index++) {
    var line = lines[index];
    var trimmed = line.trim();

    if (trimmed.indexOf('```') === 0) {
      flushParagraph();
      flushList();
      if (inCodeBlock) {
        flushCodeBlock();
      } else {
        inCodeBlock = true;
        codeBuffer = [];
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    var tableResult = renderTable(lines, index);
    if (tableResult) {
      flushParagraph();
      flushList();
      html.push(tableResult.html);
      index = tableResult.nextIndex - 1;
      continue;
    }

    if (/^---+$/.test(trimmed) || /^\*\*\*+$/.test(trimmed)) {
      flushParagraph();
      flushList();
      html.push('<hr>');
      continue;
    }

    var headingMatch = /^(#{1,4})\s+(.*)$/.exec(trimmed);
    if (headingMatch) {
      flushParagraph();
      flushList();
      var level = headingMatch[1].length;
      html.push('<h' + level + '>' + renderInlineMarkdown(headingMatch[2]) + '</h' + level + '>');
      continue;
    }

    if (trimmed.indexOf('>') === 0) {
      flushParagraph();
      flushList();
      html.push('<blockquote>' + renderInlineMarkdown(trimmed.replace(/^>\s?/, '')) + '</blockquote>');
      continue;
    }

    var unorderedMatch = /^[-*+]\s+(.*)$/.exec(trimmed);
    if (unorderedMatch) {
      flushParagraph();
      if (listType && listType !== 'ul') {
        flushList();
      }
      listType = 'ul';
      listItems.push(renderInlineMarkdown(unorderedMatch[1]));
      continue;
    }

    var orderedMatch = /^\d+\.\s+(.*)$/.exec(trimmed);
    if (orderedMatch) {
      flushParagraph();
      if (listType && listType !== 'ol') {
        flushList();
      }
      listType = 'ol';
      listItems.push(renderInlineMarkdown(orderedMatch[1]));
      continue;
    }

    paragraph.push(trimmed);
  }

  flushParagraph();
  flushList();
  flushCodeBlock();
  return '<div class="markdown-preview">' + html.join('') + '</div>';
}

function loadFile(path) {
  currentFile = path;
  currentFileStatus = 'empty';
  if (stateData && stateData.tree) {
    var parts = path.split('/');
    var stageKey = parts[0];
    var fname = parts[1];
    var stageFiles = stateData.tree[stageKey] || [];
    for (var si = 0; si < stageFiles.length; si++) {
      if (stageFiles[si].name === fname) {
        currentFileStatus = stageFiles[si].status || 'empty';
        break;
      }
    }
  }
  updateReviewBar();
  document.getElementById('contentTitle').textContent = path;
  document.getElementById('contentMeta').textContent = '';
  document.getElementById('critiquePanel').style.display = 'block';
  document.getElementById('critiqueInput').value = '';
  document.getElementById('statusBanner').innerHTML = '';

  if (stateData && stateData.tree) {
    var stage = path.split('/')[0];
    var fileName = path.split('/').slice(1).join('/');
    var stageFiles = stateData.tree[stage] || [];
    for (var i = 0; i < stageFiles.length; i++) {
      var fileEntry = stageFiles[i];
      if (fileEntry && fileEntry.name === fileName) {
        var statusMeta = FILE_STATUS_COPY[fileEntry.status] || FILE_STATUS_COPY.empty;
        document.getElementById('contentMeta').textContent = statusMeta.label + ' - ' + statusMeta.description;
        break;
      }
    }
  }

  var allFiles = document.querySelectorAll('.file-item');
  for (var i = 0; i < allFiles.length; i++) {
    allFiles[i].classList.remove('active');
    if (allFiles[i].getAttribute('data-path') === path) {
      allFiles[i].classList.add('active');
    }
  }

  fetch('/api/file?path=' + encodeURIComponent(path))
    .then(function(r) { return r.text(); })
    .then(function(text) {
      document.getElementById('contentBody').innerHTML = renderMarkdown(text);
    })
    .catch(function(err) {
      document.getElementById('contentBody').innerHTML = '<div class="markdown-preview"><p class="empty-file">Error loading file: ' + escapeHtml(String(err)) + '</p></div>';
    });
}

function toggleGate(gateName) {
  var nextStatus = 'PASSED';
  if (stateData && stateData.gates && stateData.gates[gateName] === 'PASSED') {
    nextStatus = 'PENDING';
  }
  fetch('/api/gate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gate: gateName, status: nextStatus })
  })
  .then(function(r) { return r.json(); })
  .then(function() { loadState(); })
  .catch(function(err) {
    console.error('Failed to toggle gate:', err);
  });
}

function saveRuntime() {
  var tool = document.getElementById('toolSelect').value;
  var model = document.getElementById('modelInput').value.trim();
  var saveButton = document.getElementById('saveRuntimeButton');

  saveButton.disabled = true;
  saveButton.textContent = 'Saving...';

  fetch('/api/runtime', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tool: tool, model: model })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    saveButton.disabled = false;
    saveButton.textContent = 'Save Runtime';
    if (data.status === 'success') {
      showBanner('success', 'Runtime settings updated.');
      loadState(true);
    } else {
      showBanner('error', 'Runtime update failed.');
    }
  })
  .catch(function(err) {
    saveButton.disabled = false;
    saveButton.textContent = 'Save Runtime';
    showBanner('error', 'Runtime update failed: ' + err);
  });
}

function updateReviewBar() {
  var bar = document.getElementById('reviewBar');
  var btn = document.getElementById('reviewToggleBtn');
  var label = document.getElementById('reviewStatusLabel');
  if (!currentFile || currentFileStatus === 'empty') {
    bar.style.display = 'none';
    return;
  }
  bar.style.display = 'flex';
  if (currentFileStatus === 'reviewed') {
    btn.textContent = 'Mark Needs Review';
    btn.className = 'btn-needs-review';
    label.textContent = 'Reviewed ✓';
    label.style.color = 'var(--accent-green)';
  } else {
    btn.textContent = 'Mark as Reviewed';
    btn.className = 'btn-reviewed';
    label.textContent = 'Needs Review';
    label.style.color = 'var(--accent-amber)';
  }
}

function toggleReview() {
  if (!currentFile) return;
  var newStatus = currentFileStatus === 'reviewed' ? 'needs_review' : 'reviewed';
  fetch('/api/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: currentFile, status: newStatus })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.status === 'success') {
      currentFileStatus = newStatus;
      updateReviewBar();
      loadState(false);
    }
  })
  .catch(function(err) { showBanner('error', 'Review update failed: ' + err); });
}

function sendCritique() {
  if (!currentFile) return;
  var critique = document.getElementById('critiqueInput').value.trim();
  if (!critique) return;

  var btn = document.getElementById('btnSend');
  btn.disabled = true;
  btn.textContent = 'Processing...';
  showBanner('loading', 'Sending critique to AI agent...');

  fetch('/api/fix', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: currentFile, critique: critique })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    btn.disabled = false;
    btn.textContent = 'Send to AI';
    if (data.status === 'success') {
      showBanner('success', 'File regenerated successfully.');
      loadFile(currentFile);
    } else {
      showBanner('error', 'AI generation failed. Check terminal logs.');
    }
  })
  .catch(function(err) {
    btn.disabled = false;
    btn.textContent = 'Send to AI';
    showBanner('error', 'Request failed: ' + err);
  });
}

function showBanner(type, message) {
  var banner = document.getElementById('statusBanner');
  banner.innerHTML = '<div class="status-banner ' + type + '">' + message + '</div>';
  if (type !== 'loading') {
    setTimeout(function() { banner.innerHTML = ''; }, 5000);
  }
}

loadState();
document.getElementById('toolSelect').addEventListener('change', updateRuntimeHelp);
setInterval(loadState, 3000);
</script>
</body>
</html>
"""

TEMPLATE = '''#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from datetime import datetime

FORGE_DIR = ".forge"

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
    print(f"[AEOS] {{msg}}")

def parse_args():
    parser = argparse.ArgumentParser(description="AEOS Pipeline Runner")
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

SERVER_PY = r"""import os
import sys
import json
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO_ROOT = os.environ.get("AEOS_REPO_ROOT", ".")
FORGE_DIR = os.path.join(REPO_ROOT, ".forge")
REVIEWS_FILE = os.path.join(FORGE_DIR, "reviews.json")

GATE_STAGE_MAP = {{
    "context-gate": "00-context",
    "prd-gate": "01-requirements",
    "design-gate": "02-design",
    "architecture-gate": "04-architecture",
    "engineering-gate": "06-engineering",
    "qa-gate": "07-quality",
    "release-gate": "09-release",
}}

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {{}}

def save_reviews(reviews):
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=2)

def build_file_entry(stage_dir, filename, reviews=None):
    file_path = os.path.join(stage_dir, filename)
    file_stats = os.stat(file_path)
    file_size = file_stats.st_size
    modified_at = int(file_stats.st_mtime)
    stage_name = os.path.basename(stage_dir)
    rel_path = f"{{stage_name}}/{{filename}}"
    if reviews is None:
        reviews = {{}}
    if file_size == 0:
        status = "empty"
    elif reviews.get(rel_path) == "reviewed":
        status = "reviewed"
    else:
        status = "needs_review"
    return {{
        "name": filename,
        "status": status,
        "size": file_size,
        "modifiedAt": modified_at,
    }}

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
        if reviews.get(f"{{stage_dir_name}}/{{fname}}") != "reviewed":
            return "PENDING"
    return "PASSED"

class ForgeHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open(os.path.join(FORGE_DIR, "scripts/dashboard.html"), "rb") as f:
                self.wfile.write(f.read())
            return
            
        if self.path == "/api/state":
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            gates = {{}}
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
                            gates[gate_name] = "PASSED" if "PASSED" in content or "APPROVED" in content else "PENDING"

            reviews = load_reviews()
            VALID_STAGE_PREFIXES = {{f"{{i:02d}}" for i in range(11)}}
            files_tree = {{}}
            stage_review_summary = {{}}
            for d in sorted(os.listdir(FORGE_DIR)):
                d_path = os.path.join(FORGE_DIR, d)
                if os.path.isdir(d_path) and d[:2] in VALID_STAGE_PREFIXES:
                    files_tree[d] = []
                    reviewed_count = 0
                    total_count = 0
                    for f in os.listdir(d_path):
                        if f.endswith(".md"):
                            entry = build_file_entry(d_path, f, reviews)
                            files_tree[d].append(entry)
                            total_count += 1
                            if entry["status"] == "reviewed":
                                reviewed_count += 1
                    stage_review_summary[d] = {{"reviewed": reviewed_count, "total": total_count}}
                            
            processing_status = {{"status": "idle"}}
            status_file = os.path.join(FORGE_DIR, "runs/status.json")
            if os.path.exists(status_file):
                try:
                    with open(status_file, "r") as sf:
                        processing_status = json.load(sf)
                except:
                    pass
                    
            all_reviewed = all(
                s["reviewed"] == s["total"] and s["total"] > 0
                for s in stage_review_summary.values()
            ) if stage_review_summary else False
            state = {{
                "gates": gates,
                "tree": files_tree,
                "processing": processing_status,
                "stageReviewSummary": stage_review_summary,
                "allReviewed": all_reviewed,
            }}
            self.wfile.write(json.dumps(state).encode())
            return

        if self.path.startswith("/api/file"):
            import urllib.parse
            parsed_path = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_path.query)
            file_path = params.get("path", [None])[0]
            
            if not file_path:
                self.send_response(400)
                self.end_headers()
                return
                
            abs_path = os.path.join(FORGE_DIR, file_path)
            if os.path.exists(abs_path):
                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                with open(abs_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if self.path == "/api/gate":
            gate_name = data.get("gate")
            gate_path = os.path.join(FORGE_DIR, f"12-gates/{{gate_name}}.md")
            if os.path.exists(gate_path):
                with open(gate_path, "r") as f:
                    content = f.read()
                content = content.replace("PENDING", "PASSED")
                with open(gate_path, "w") as f:
                    f.write(content)
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "success"}}).encode())
            else:
                self.send_response(404)
                self.end_headers()
            return
            
        if self.path == "/api/review":
            file_path = data.get("path")
            status = data.get("status")
            if not file_path or status not in ("reviewed", "needs_review"):
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()
                return
            reviews = load_reviews()
            if status == "reviewed":
                reviews[file_path] = "reviewed"
            else:
                reviews.pop(file_path, None)
            save_reviews(reviews)
            for gate_name in GATE_STAGE_MAP:
                gate_status = evaluate_gate(gate_name)
                gate_path = os.path.join(FORGE_DIR, f"12-gates/{{gate_name}}.md")
                if os.path.exists(gate_path):
                    with open(gate_path, "r") as gf:
                        content = gf.read()
                    new_content = content
                    if gate_status == "PASSED" and "PENDING" in content:
                        new_content = content.replace("PENDING", "PASSED")
                    elif gate_status == "PENDING" and "PASSED" in content:
                        new_content = content.replace("PASSED", "PENDING")
                    if new_content != content:
                        with open(gate_path, "w") as gf:
                            gf.write(new_content)
            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({{"status": "success"}}).encode())
            return

        if self.path == "/api/fix":
            file_path = data.get("path")
            critique = data.get("critique")
            
            if not file_path or not critique:
                self.send_response(400)
                self.end_headers()
                return
                
            stage = file_path.split("/")[0].split("-", 1)[1] if "-" in file_path.split("/")[0] else "context"
            
            cmd = [sys.executable, os.path.join(FORGE_DIR, "scripts/run.py"), stage, "--output", file_path, "--critique", critique]
            result = subprocess.run(cmd, cwd=REPO_ROOT)
            
            if result.returncode == 0:
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "success"}}).encode())
            else:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "failed"}}).encode())
            return
            
def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ForgeHandler)
    print(f"Forge Dashboard running at http://localhost:{{port}}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run_server()
"""

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
    result = subprocess.run([sys.executable, server_script], env={{**os.environ, "AEOS_REPO_ROOT": "."}})
    sys.exit(result.returncode)

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
        print("Usage: ./forge [--project <path>] <init|generate [stage] [input]|pipeline [input]|dashboard [port]|dev [port]>")
        sys.exit(1)

    command = args[0]

    if command == "init":
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
        print("Available commands: init, generate [stage], pipeline, dashboard, dev")
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
        DASHBOARD_HTML_CONTENT=DASHBOARD_HTML_CONTENT
    )

    with open("forge", "w") as f:
        f.write(forge_content)

    print("forge built successfully.")

if __name__ == "__main__":
    build_forge()
