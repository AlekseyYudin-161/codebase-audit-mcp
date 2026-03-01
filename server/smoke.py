"""
Smoke test for codebase-audit-mcp.

Runs as: python main.py smoke
Starts the server in a background thread, calls /health and all three
tools via MCP JSON-RPC, then exits with code 0 (pass) or 1 (fail).
"""

import json
import threading
import time
from pathlib import Path
import requests
import uvicorn

from server.logging_config import logger

# Path to demo_project — used as test input for all tools
DEMO_PROJECT = str(Path(__file__).parent.parent / "demo_project")

# Server settings for smoke test — different port to avoid conflicts
SMOKE_HOST = "127.0.0.1"
SMOKE_PORT = 8001
BASE_URL = f"http://{SMOKE_HOST}:{SMOKE_PORT}"
MCP_URL = f"{BASE_URL}/mcp"


def _start_server() -> None:
    """Start uvicorn in background thread."""
    from server.app import app

    uvicorn.run(app, host=SMOKE_HOST, port=SMOKE_PORT, log_level="error")


def _wait_for_server(timeout: int = 10) -> bool:
    """Poll /health until server is ready or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=1)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    return False


def _call_tool(tool_name: str, arguments: dict) -> dict:
    """
    Call an MCP tool via Streamable HTTP JSON-RPC.
    Returns parsed result or raises on error.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    r = requests.post(MCP_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()

    # Response may be JSON or SSE stream — handle both
    content_type = r.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        # Parse SSE: find the first "data: {...}" line
        for line in r.text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        raise ValueError("No data line found in SSE response")

    return r.json()


def run_smoke() -> int:
    """
    Main smoke test entrypoint.
    Returns 0 on success, 1 on failure.
    """
    logger.info("Starting smoke test...")

    # --- Start server in background ---
    thread = threading.Thread(target=_start_server, daemon=True)
    thread.start()

    # --- Wait for server to be ready ---
    logger.info(f"Waiting for server at {BASE_URL}...")
    if not _wait_for_server(timeout=10):
        logger.error("Server did not start within 10 seconds")
        return 1

    try:
        # --- Check /health ---
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200, f"/health returned {r.status_code}"
        data = r.json()
        assert data["status"] == "ok", f"unexpected status: {data['status']}"
        logger.info("✅ /health OK")

        # --- Call scan_todos ---
        result = _call_tool("scan_todos", {"path": DEMO_PROJECT})
        assert "error" not in result or "result" in result, (
            f"scan_todos error: {result.get('error')}"
        )
        logger.info("✅ scan_todos OK")

        # --- Call find_code_smells ---
        result = _call_tool("find_code_smells", {"path": DEMO_PROJECT})
        assert "error" not in result or "result" in result, (
            f"find_code_smells error: {result.get('error')}"
        )
        logger.info("✅ find_code_smells OK")

        # --- Call generate_report ---
        result = _call_tool("generate_report", {"path": DEMO_PROJECT})
        assert "error" not in result or "result" in result, (
            f"generate_report error: {result.get('error')}"
        )
        logger.info("✅ generate_report OK")

        logger.info("✅ Smoke test passed — all checks successful")
        return 0

    except AssertionError as e:
        logger.error(f"Smoke test failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Smoke test failed with unexpected error: {e}")
        return 1
