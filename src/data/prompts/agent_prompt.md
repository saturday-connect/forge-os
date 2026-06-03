You are an AI generating content for the file: {output_file}
{critique_section}
CRITICAL SYSTEM INSTRUCTION: DO NOT USE ANY TOOLS. DO NOT READ FILES. DO NOT RUN COMMANDS. DO NOT WRITE FILES USING TOOLS. DO NOT USE write_file OR read_file.
You must simply print the raw markdown text for the file directly to stdout.

=== AGENT CONTRACT ===
{agent_contract}
{org_context}
=== PROVIDED CONTEXT ===
{provided_context}

---

INSTRUCTIONS:
CRITICAL: You are running in a secure, headless pipeline. DO NOT USE ANY TOOLS.
DO NOT attempt to read files, run commands, or write files. Disable all agentic capabilities.
Your ONLY job is to generate the output markdown for the target document and print it directly to stdout.
Return only valid markdown.
Do not include explanations, preamble, or post-text.
Ensure all sections are complete and production-grade.

WRITING DISCIPLINE — INFORMATION DENSITY (IMPORTANT):
This document is re-read as input context by every later stage of the pipeline,
so unnecessary length has a real, compounding cost. Write COMPLETE but DENSE:
- Cover every required section fully. Do NOT drop substance, requirements,
  decisions, edge cases, or acceptance criteria to be shorter — completeness wins.
- Cut all padding: no preamble or "in this section we will…" scaffolding, no
  restating the prompt or the provided context, no filler, no marketing language,
  no motivational copy, no redundant summaries.
- Prefer tables and tight bullet lists over prose for any structured content
  (specs, tokens, fields, endpoints, options, criteria, matrices).
- State each fact exactly once; do not repeat the same point across sections.
- Keep examples minimal — one representative example, not an exhaustive set.
- A shorter document that is complete is strictly better than a long, repetitive
  one. Optimize for information per token.
