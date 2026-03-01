import sys, uvicorn
from server.smoke import run_smoke
from server.logging_config import logger

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "serve":
        logger.info("Starting server...")
        uvicorn.run("server.app:app", host="0.0.0.0", port=8000)
    elif cmd == "smoke":
        sys.exit(run_smoke())
    else:
        logger.error(f"Unknown command: {cmd}. Use: serve | smoke")
        print(f"Unknown command: {cmd}. Use: serve | smoke")
        sys.exit(1)
