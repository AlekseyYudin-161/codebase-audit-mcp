# Test fixture: known markers — scan_todos must find exactly 6 items in this file.
# scan_todos must find exactly 6 items in this file.


def connect(host: str, port: int) -> None:
    # TODO: add retry logic with exponential backoff
    pass


def parse_config(path: str) -> dict:
    # FIXME: does not handle missing keys, raises KeyError
    return {}


def compute_hash(data: bytes) -> str:
    # HACK: md5 used for speed, not security — replace with sha256
    import hashlib

    return hashlib.md5(data).hexdigest()


def legacy_export(records: list) -> None:
    # XXX: this whole function should be rewritten using the new API
    pass


def get_timeout() -> int:
    # NOTE: timeout is in seconds, not milliseconds
    return 30


def old_auth(token: str) -> bool:
    # DEPRECATED: use new_auth() from auth_v2 module instead
    return token == "hardcoded"
