"""MCP prompts: ready-made instruction templates for codebase audit workflows."""

from mcp.server.fastmcp import FastMCP


def register_templates(mcp: FastMCP) -> None:
    """Register all prompt templates in FastMCP."""

    @mcp.prompt(
        name="full_audit",
        description=(
            "Full codebase audit: TODO markers, code smells, "
            "hardcoded secrets, complex functions. Returns a Markdown report."
        ),
    )
    def full_audit(path: str) -> str:
        """
        Runs a full audit of the project at the given path.

        Args:
            path: Path to the project root to analyze.
        """
        return (
            f"Perform a full codebase audit at path: {path}\n\n"
            "Execute the following steps in strict order:\n"
            f"1. Call tool `scan_todos` with path='{path}' — find all TODO, "
            "FIXME, HACK, XXX, NOTE, DEPRECATED markers.\n"
            f"2. Call tool `find_code_smells` with path='{path}' — find "
            "hardcoded secrets, eval/exec usage, long functions, high complexity, "
            "and large commented-out blocks.\n"
            f"3. Call tool `generate_report` with path='{path}' — get the "
            "aggregated health report.\n"
            "4. Based on the results:\n"
            "   - Explain each found issue in plain English.\n"
            "   - Prioritize: HIGH severity first, then MEDIUM, then LOW.\n"
            "   - For each HIGH severity issue, suggest a concrete fix with a code example.\n"
            "   - Compile a top-5 action list of the most critical things to address first.\n\n"
            "Format the final response in Markdown with sections: "
            "Summary, Critical Issues, Warnings, TODO Tracker, Recommendations."
        )

    @mcp.prompt(
        name="quick_secrets_check",
        description=(
            "Quick check for hardcoded secrets, tokens, "
            "passwords, and API keys. HIGH severity only."
        ),
    )
    def quick_secrets_check(path: str) -> str:
        """
        Checks the project only for hardcoded secrets and tokens.

        Args:
            path: Path to the project root to check.
        """
        return (
            f"Check the codebase at path: {path} for hardcoded secrets.\n\n"
            f"1. Call tool `find_code_smells` with path='{path}'.\n"
            "2. From the results, keep only entries with severity='high' "
            "and category='secret'.\n"
            "3. For each found secret:\n"
            "   - Report the file and line number.\n"
            "   - Explain why this is dangerous.\n"
            "   - Suggest how to fix it: move to .env, use environment "
            "variables, or a secrets manager.\n"
            "4. If no secrets are found — confirm the check passed cleanly.\n\n"
            "Do NOT output the actual secret values in the response — "
            "only report their presence and location."
        )

    @mcp.prompt(
        name="standup_prep",
        description=(
            "Standup preparation: find all TODO/FIXME markers, "
            "prioritize them, and suggest tasks for the day."
        ),
    )
    def standup_prep(path: str) -> str:
        """
        Analyzes TODO markers and suggests tasks for sprint planning.

        Args:
            path: Path to the project root.
        """
        return (
            f"Prepare a task list for standup based on the codebase at: {path}\n\n"
            f"1. Call tool `scan_todos` with path='{path}'.\n"
            "2. Group results by marker type: "
            "FIXME (bugs), TODO (features/improvements), "
            "HACK (technical debt), DEPRECATED (legacy code).\n"
            "3. For each group:\n"
            "   - Count the total number of items.\n"
            "   - Highlight the top 3 most important based on context.\n"
            "4. Format the output as:\n"
            "   🔴 Urgent (FIXME): ...\n"
            "   🟡 In progress (TODO): ...\n"
            "   🔵 Tech debt (HACK/DEPRECATED): ...\n"
            "5. Suggest 3 concrete tasks that can realistically be closed in one day."
        )
