
> Локальный MCP-сервер для статического анализа кодовой базы: находит TODO-/FIXME-/ прочие маркеры, захардкоженные секреты, code smells (уязвимости, переусложненные функции, слишком длинные функции) и генерирует отчёты о состоянии проекта. Работает полностью офлайн — без внешних API.

---

## Что делает этот MCP-сервер

**Какую боль решает:** разработчики тратят время на ручной поиск технического долга, забытых секретов и проблем качества кода, разбросанных по большой кодовой базе. Этот сервер автоматизирует этот процесс
и встраивается напрямую в IDE.

**Для кого:** разработчики, использующие Cursor, Claude Desktop или любой MCP-совместимый клиент, которые хотят мгновенно получать отчёт о здоровье кодовой базы не выходя из редактора.

**Реализованные инструменты:**

| Tool | Описание |
|---|---|
| `scan_todos` | Находит все маркеры TODO, FIXME, HACK, XXX, NOTE, DEPRECATED в комментариях |
| `find_code_smells` | Обнаруживает захардкоженные секреты, использование eval/exec, длинные функции, высокую сложность, большие блоки комментариев |
| `generate_report` | Запускает оба инструмента выше и возвращает агрегированный JSON-отчёт |

**Ресурсы:**

| Resource | Описание |
|---|---|
| `config://audit-rules` | Текущие правила и пороги анализа |
| `report://last` | Последний сгенерированный отчёт (in-memory) |

**Промпты:** `full_audit`, `quick_secrets_check`, `standup_prep`

---

## Быстрый старт

### Требования

- Docker + Docker Compose
- Node.js v18+ (для MCP Inspector)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/codebase-audit-mcp
cd codebase-audit-mcp
```

### 2. Собрать Docker-образ

```bash
docker compose build
```

### 3. Запустить сервер

```bash
docker compose up serve
```

### 4. Проверить `/health`

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{"status": "ok", "version": "0.1.0", "tools": ["scan_todos", "find_code_smells", "generate_report"]}
```

### 5. Запустить smoke-тест

```bash
docker compose run --rm smoke
```

Ожидаемый вывод:
```
✅ /health OK
✅ scan_todos OK
✅ find_code_smells OK
✅ generate_report OK
✅ Smoke test passed — all checks successful
```

### 6. Подключиться через MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

Открыть URL из терминала в браузере. В интерфейсе Inspector:
- **Transport Type:** `Streamable HTTP`
- **URL:** `http://localhost:8000/mcp`
- **Connection Type:** `Direct`
- Нажать **Connect**

---

## Как использовать

### Tool: `scan_todos`

Рекурсивно сканирует директорию на наличие маркеров в комментариях.

**Входные параметры:**
```json
{"path": "/app/demo_project"}
```

**Возвращает:** список маркеров с полями `tag`, `file`, `line`, `text`, `context`.

**Пропускает:** `__pycache__`, `.git`, `node_modules`, `.venv`, бинарные файлы, lock-файлы, файлы > 1 МБ.

---

### Tool: `find_code_smells`

Статический анализ потенциальных проблем с использованием regex и Python AST.

**Входные параметры:**
```json
{"path": "/app/demo_project"}
```

**Возвращает:** список проблем с полями `category`, `severity`, `file`, `line`, `description`, `snippet`.

**Категории:**

| Категория | Серьёзность | Что обнаруживает |
|---|---|---|
| `secret` | high | Захардкоженные пароли, API-ключи, токены, AWS-ключи |
| `dangerous_call` | high | Использование `eval()` / `exec()` |
| `high_complexity` | high | Цикломатическая сложность ≥ 10 |
| `long_function` | medium | Функции длиной ≥ 50 строк |
| `commented_block` | low | 5+ подряд идущих строк комментариев |

---

### Tool: `generate_report`

Запускает `scan_todos` + `find_code_smells` и возвращает агрегированный отчёт.

**Входные параметры:**
```json
{"path": "/app/demo_project"}
```

**Возвращает:** `HealthReport` с полями `path`, `timestamp`, `files_scanned`, `todos`, `smells`, `summary`.

---

### Промпты (в Cursor / Claude Desktop)

| Промпт | Что делает |
|---|---|
| `full_audit` | Полный аудит: вызывает все 3 инструмента, форматирует Markdown-отчёт по разделам |
| `quick_secrets_check` | Проверяет только захардкоженные секреты (HIGH severity) |
| `standup_prep` | Группирует TODO-маркеры по типу, предлагает задачи на день |

---

## Анализ проектов

### Анализ `demo_project` (включён в образ)

```bash
docker compose up serve
```

В Inspector указать `path`:
```
/app/demo_project
```

### Анализ стороннего проекта

```bash
PROJECT_PATH=/absolute/path/to/your/project docker compose up serve
```

В Inspector указать `path`:
```
/workspace
```

---

## Подключение к Cursor

Добавить в `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "codebase-audit": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Перезапустить Cursor. В чате:
> "Run full_audit on /app/demo_project"

---

## Подключение к Claude Desktop

Добавить в `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "codebase-audit": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## Конфигурация (опционально)

Дефолтные пороги работают из коробки. Для изменения скопировать `.env.example`:

```bash
cp .env.example .env
```

Отредактировать `.env`:
```bash
LONG_FUNCTION_THRESHOLD=30       # помечать функции длиннее 30 строк
HIGH_COMPLEXITY_THRESHOLD=8      # помечать сложность выше 8 ветвлений
COMMENTED_BLOCK_THRESHOLD=3      # помечать 3+ подряд идущих комментария
MAX_FILE_SIZE_BYTES=1048576      # пропускать файлы больше 1 МБ
```

Перезапустить сервер — пересборка образа не нужна:
```bash
docker compose up serve
```

Проверить применённые значения (запуск одного из tools).

---

## Ограничения

- AST-анализ (длинные функции, сложность) работает только для **Python-файлов**
- Поиск секретов и TODO-маркеров работает для **всех текстовых файлов**
- Файлы размером более 1 МБ пропускаются (настраивается через `MAX_FILE_SIZE_BYTES`)
- Lock-файлы (`.lock`, `poetry.lock`, `package-lock.json`) пропускаются намеренно
- Интернет-соединение не требуется — полностью локальный анализ
- Протестировано на: Python-проектах, смешанных Python/YAML-проектах

---

## Ресурсные лимиты

| Ресурс | Значение |
|---|---|
| Размер Docker-образа | 224 МБ (лимит: 500 МБ) |
| CPU | 2.0 (задан в docker-compose.yml) |
| RAM | 2048 МБ (задан в docker-compose.yml) |
| Порт | 8000 |