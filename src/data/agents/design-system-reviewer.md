# Agent: Design System Reviewer

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
