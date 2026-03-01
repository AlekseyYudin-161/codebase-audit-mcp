"""All the constants used in the application."""

DEFAULT_TAGS = ["TODO", "FIXME", "HACK", "XXX", "NOTE", "DEPRECATED"]

IGNORED_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}

IGNORED_EXTENSIONS = {
    ".lock",      # poetry.lock, package-lock.json
    ".sum",       # go.sum
    ".min.js",    # минифицированный JS
    ".min.css",   # минифицированный CSS
    ".map",       # source maps
}

BINARY_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".exe",
    ".jpg",
    ".png",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}

MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB - можно увеличить до 5 MB

SECRET_PATTERNS = [
    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}["\']', "Hardcoded password"),
    (r'(?i)(api_key|apikey|api-key)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded API key"),
    (r'(?i)(secret|token)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded secret/token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----", "Private key in code"),
    (r"(?i)bearer\s+[a-zA-Z0-9\-_]{20,}", "Bearer token in code"),
]

LONG_FUNCTION_THRESHOLD = 50  # строк
HIGH_COMPLEXITY_THRESHOLD = 10  # число ветвлений
COMMENTED_BLOCK_THRESHOLD = 5  # строк подряд
