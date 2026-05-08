import os
import re

FORGE_PATH = "forge"

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

STAGE_MULTI_OUTPUTS = """STAGE_MULTI_OUTPUTS = {
    "context": [
        "00-context/product-vision.md",
        "00-context/business-model.md",
        "00-context/constraints.md",
        "00-context/users-and-personas.md",
        "00-context/competitive-analysis.md",
        "00-context/positioning.md"
    ],
    "requirements": [
        "01-requirements/brd.md",
        "01-requirements/prd.md",
        "01-requirements/non-functional-requirements.md",
        "01-requirements/open-questions.md",
        "01-requirements/success-metrics.md"
    ],
    "design": [
        "02-design/design-brief.md",
        "02-design/design-system.md",
        "02-design/ux-principles.md",
        "02-design/user-flows.md",
        "02-design/accessibility-guidelines.md"
    ],
    "analysis": [
        "03-analysis/domain-model.md",
        "03-analysis/user-journeys.md",
        "03-analysis/risks-and-assumptions.md",
        "03-analysis/process-flows.md"
    ],
    "architecture": [
        "04-architecture/system-architecture.md",
        "04-architecture/api-design.md",
        "04-architecture/data-model.md",
        "04-architecture/security-design.md",
        "04-architecture/deployment-architecture.md"
    ],
    "delivery": [
        "05-delivery/roadmap.md",
        "05-delivery/epics.md",
        "05-delivery/user-stories.md",
        "05-delivery/sprint-plan.md"
    ],
    "engineering": [
        "06-engineering/backend-spec.md",
        "06-engineering/frontend-spec.md",
        "06-engineering/implementation-plan.md"
    ],
    "qa": [
        "07-quality/test-strategy.md",
        "07-quality/acceptance-tests.md"
    ],
    "operations": [
        "08-operations/monitoring.md",
        "08-operations/runbook.md",
        "08-operations/incident-response.md"
    ],
    "release": [
        "09-release/release-notes.md",
        "09-release/production-readiness-review.md",
        "09-release/rollout-strategy.md"
    ],
    "marketing": [
        "10-marketing/marketing-strategy.md",
        "10-marketing/product-positioning.md",
        "10-marketing/target-audience.md"
    ]
}"""

def update_forge_executable():
    with open(FORGE_PATH, "r") as f:
        content = f.read()

    # Replace STAGE_MULTI_OUTPUTS in STAGE_RUNNER_PY
    pattern = r"STAGE_MULTI_OUTPUTS = \{\n.*?\n\}"
    content = re.sub(pattern, STAGE_MULTI_OUTPUTS, content, flags=re.DOTALL)

    # Rebuild the agent generation block in cmd_init
    # Find the agent_template loop
    agent_loop_pattern = r'for agent in agents:\n\s+agent_path = os\.path\.join\(FORGE_DIR, f"11-agents/\{agent\}\.md"\)\n\s+if not os\.path\.exists\(agent_path\):\n\s+with open\(agent_path, "w"\) as f:\n(?:\s+if agent == "product-strategist":\n.*?\n\s+else:\n\s+f\.write\(agent_template\.format\(agent=agent\)\)\n|\s+f\.write\(agent_template\.format\(agent=agent\)\)\n)'
    
    agent_code = 'for agent in agents:\n        agent_path = os.path.join(FORGE_DIR, f"11-agents/{agent}.md")\n        if not os.path.exists(agent_path):\n            with open(agent_path, "w") as f:\n'
    first = True
    for agent, text in AGENTS.items():
        if first:
            agent_code += f'                if agent == "{agent}":\n                    f.write("""{text}""")\n'
            first = False
        else:
            agent_code += f'                elif agent == "{agent}":\n                    f.write("""{text}""")\n'
    
    agent_code += '                else:\n                    f.write(agent_template.format(agent=agent))\n'

    content = re.sub(agent_loop_pattern, agent_code, content, flags=re.DOTALL)

    # Rebuild the gate generation block
    gate_loop_pattern = r'for gate in gates:\n\s+gate_path = os\.path\.join\(FORGE_DIR, f"12-gates/\{gate\}\.md"\)\n\s+if not os\.path\.exists\(gate_path\):\n\s+with open\(gate_path, "w"\) as f:\n\s+f\.write\(gate_template\.format\(gate=gate\)\)\n'

    gate_code = 'for gate in gates:\n        gate_path = os.path.join(FORGE_DIR, f"12-gates/{gate}.md")\n        if not os.path.exists(gate_path):\n            with open(gate_path, "w") as f:\n'
    first_gate = True
    for gate, text in GATES.items():
        if first_gate:
            gate_code += f'                if gate == "{gate}":\n                    f.write("""{text}""")\n'
            first_gate = False
        else:
            gate_code += f'                elif gate == "{gate}":\n                    f.write("""{text}""")\n'
    gate_code += '                else:\n                    f.write(gate_template.format(gate=gate))\n'

    content = re.sub(gate_loop_pattern, gate_code, content, flags=re.DOTALL)

    with open(FORGE_PATH, "w") as f:
        f.write(content)
        
    print("Forge executable updated.")

if __name__ == "__main__":
    update_forge_executable()
