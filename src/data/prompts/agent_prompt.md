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
