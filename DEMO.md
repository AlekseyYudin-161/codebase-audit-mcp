# DEMO.md — сценарий проверки codebase-audit-mcp

## 1. Цель сценария

Продемонстрировать реальную пользу трёх инструментов MCP-сервера на тестовом проекте `demo_project`:
- `scan_todos` — находит технический долг в комментариях
- `find_code_smells` — обнаруживает захардкоженные секреты, опасный код, сложные функции
- `generate_report` — агрегирует результаты в единый отчёт о здоровье проекта

Время прохождения сценария: **3–5 минут**.

---

## 2. Предусловия

### Запустить сервер (в первом терминале)

```bash
docker compose build
docker compose up serve
```

Проверить что сервер готов (во втором терминале):

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{"status": "ok", "version": "0.1.0", "tools": ["scan_todos", "find_code_smells", "generate_report"]}
```

### Запустить MCP Inspector (также во втором терминале)

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

Обычно MCP Inspector сам запустится в браузере, но если этого не произошло -
Открыть URL из терминала в браузере. Параметры для подключения такие:
- **Transport Type:** `Streamable HTTP`
- **URL:** `http://localhost:8000/mcp`
- Нажать **Connect**

Во вкладках **Tools**, **Resources**, **Prompts** должны появиться зарегистрированные элементы.

---

## 3. Шаги проверки

### Шаг 1: Найти TODO-маркеры — `scan_todos`

В Inspector → вкладка **Tools** → выбрать `scan_todos`.

Передать аргумент:
```json
{"path": "/app/demo_project"}
```

Нажать **Run Tool**.

**Ожидаемый результат:** список маркеров из файлов `app/main.py`, `app/utils.py`, `app/database.py`.
Должны присутствовать теги: `TODO`, `FIXME`, `HACK`, `XXX`, `NOTE`, `DEPRECATED`.

Пример одного элемента из ответа:
```json
{
  "tag": "FIXME",
  "file": "app/database.py",
  "line": 9,
  "text": "connection string hardcoded — must come from environment",
  "context": "# FIXME: connection string hardcoded — must come from environment"
}
```

---

### Шаг 2: Найти code smells — `find_code_smells`

В Inspector → вкладка **Tools** → выбрать `find_code_smells`.

Передать аргумент:
```json
{"path": "/app/demo_project"}
```

Нажать **Run Tool**.

**Ожидаемый результат:** список проблем всех категорий.

Что должно быть найдено:

| Категория | Файл | Что именно |
|---|---|---|
| `secret` | `config/settings.py` | `DB_PASSWORD`, `STRIPE_API_KEY`, `AWS_ACCESS_KEY_ID` и др. |
| `secret` | `app/main.py` | `ADMIN_TOKEN` — захардкоженный JWT |
| `dangerous_call` | `app/database.py` | `eval()` в функции `run_raw_query` |
| `long_function` | `app/utils.py` | `validate_and_process_user_data` — 70+ строк |
| `high_complexity` | `app/utils.py` | `validate_and_process_user_data` — 10+ ветвлений |
| `commented_block` | `app/utils.py` | 5+ подряд идущих строк комментариев |

---

### Шаг 3: Сгенерировать отчёт — `generate_report`

В Inspector → вкладка **Tools** → выбрать `generate_report`.

Передать аргумент:
```json
{"path": "/app/demo_project"}
```

Нажать **Run Tool**.

**Ожидаемый результат:** полный `HealthReport` со сводкой:

```json
{
  "path": "/app/demo_project",
  "files_scanned": 6,
  "summary": {
    "high": 10,
    "medium": 1,
    "low": 1,
    "todos": 12
  }
}
```

Конкретные цифры могут незначительно отличаться, но структура и наличие всех полей обязательны.

---

### Шаг 4: Проверить ресурс `report://last`

В Inspector → вкладка **Resources** → выбрать `report://last` → нажать **Read Resource**.

**Ожидаемый результат:** тот же отчёт что вернул `generate_report` на шаге 3 — сервер сохранил его в памяти.

---

### Шаг 5: Проверить конфигурацию `config://audit-rules`

В Inspector → вкладка **Resources** → выбрать `config://audit-rules` → нажать **Read Resource**.

**Ожидаемый результат:**
```json
{
  "long_function_threshold": 50,
  "high_complexity_threshold": 10,
  "commented_block_threshold": 5,
  "max_file_size_bytes": 1048576,
  "default_tags": ["TODO", "FIXME", "HACK", "XXX", "NOTE", "DEPRECATED"]
}
```

---

## 4. Ожидаемый результат — признаки успешной работы

- ✅ `scan_todos` вернул 10+ маркеров из файлов `demo_project`
- ✅ `find_code_smells` обнаружил секреты в `config/settings.py` и `app/main.py`
- ✅ `find_code_smells` обнаружил `eval()` в `app/database.py`
- ✅ `find_code_smells` обнаружил длинную/сложную функцию в `app/utils.py`
- ✅ `generate_report` вернул `HealthReport` с заполненными `todos`, `smells`, `summary`
- ✅ `report://last` вернул тот же отчёт — in-memory хранилище работает
- ✅ `config://audit-rules` отображает актуальные пороги анализа

---

## 5. Типичные проблемы / troubleshooting

**Сервер не отвечает на `/health`:**
```bash
# Проверить запущен ли контейнер
docker ps

# Если не запущен — пересобрать и запустить
docker compose build
docker compose up serve
```

**Inspector не подключается:**
- Убедиться что сервер запущен: `curl http://localhost:8000/health`
- Проверить Transport Type: должен быть `Streamable HTTP`, не `stdio`
- Проверить URL: `http://localhost:8000/mcp` (не `https`, не другой порт)

**Tool возвращает ошибку "Path does not exist":**
- Убедиться что `path` = `/app/demo_project` (путь внутри контейнера, не на хост-машине)

**Smoke-тест падает:**
```bash
# Запустить с выводом логов
docker compose run --rm smoke

# Проверить что образ пересобран после изменений
docker compose build
```

**Хочу проверить свой проект:**
```bash
# Остановить сервер
docker compose down

# Запустить с монтированием своего проекта
PROJECT_PATH=/absolute/path/to/project docker compose up serve

# В Inspector указать path = /workspace
# и дальше по инструкции выше
```