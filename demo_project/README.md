# demo-app

A intentionally flawed sample Python project used to demonstrate
the capabilities of `codebase-audit-mcp`.

## Purpose

This project contains deliberate code quality issues across all categories:

- Hardcoded secrets and API keys (`config/settings.py`)
- SQL injection vulnerabilities (`app/database.py`)
- TODO/FIXME/HACK/DEPRECATED markers (`app/main.py`, `app/utils.py`)
- Overly complex and long functions (`app/utils.py`)
- Use of `eval()` with dynamic input (`app/database.py`)
- Bare `except` clauses (`app/database.py`)

## Usage

This project is **not meant to be run**. It serves as a static analysis target
for the `codebase-audit-mcp` demo scenario described in `DEMO.md`.

Point any of the MCP tools at this directory:

```
path = "/workspace/demo_project"
```