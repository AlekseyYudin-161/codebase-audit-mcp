"""Main app launcher: Starlette + FastMCP"""

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# stateless_http=True решает ошибку "Missing session ID" при первом подключении
# (клиент ещё не имеет session ID; без stateless_http сервер отклоняет такой запрос)
mcp = FastMCP("codebase-audit-mcp", stateless_http=True)

from server.tools.scan_todos import register_scan_todos
from server.tools.find_code_smells import register_find_code_smells
from server.tools.generate_report import register_generate_report
from server.resources.audit_rules import register_audit_rules
from server.resources.last_report import register_last_report
from server.prompts.templates import register_templates

register_scan_todos(mcp)
register_find_code_smells(mcp)
register_generate_report(mcp)
register_audit_rules(mcp)
register_last_report(mcp)
register_templates(mcp)

# Получаем приложение MCP
app = mcp.streamable_http_app()


# Добавляем health маршрут Starlette-методом
async def health(request):
    return JSONResponse(
        {
            "status": "ok",
            "version": "0.1.0",
            "tools": ["scan_todos", "find_code_smells", "generate_report"],
        }
    )


app.add_route("/health", health, methods=["GET"])

# CORS для MCP Inspector (браузер): без expose_headers=["mcp-session-id"]
# клиент не сможет прочитать session ID из ответа и отправить его в следующих запросах
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=[
        "mcp-protocol-version",
        "mcp-session-id",
        "Authorization",
        "Content-Type",
    ],
    expose_headers=["mcp-session-id"],
)




### app.get("/tools")(mcp.tools)
### app.get("/resources")(mcp.resources)
### app.get("/prompts")(mcp.prompts)
