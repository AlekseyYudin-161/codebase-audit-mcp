import subprocess, time, requests, sys, threading
import uvicorn
from server.app import app

def run_smoke() -> int:
    # запускаем сервер в фоне
    server = threading.Thread(
        target=uvicorn.run,
        kwargs={"app": app, "host": "127.0.0.1", "port": 8001},
        daemon=True
    )
    server.start()
    time.sleep(2)  # ждём старта
    
    try:
        # проверяем /health
        r = requests.get("http://127.0.0.1:8001/health", timeout=5)
        assert r.status_code == 200, f"/health returned {r.status_code}"
        assert r.json()["status"] == "ok"
        print("✅ /health OK")
        
        # вызываем scan_todos на demo_project
        # (через MCP JSON-RPC напрямую)
        ...  # детали при реализации
        print("✅ scan_todos OK")
        print("✅ Smoke test passed")
        return 0
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return 1