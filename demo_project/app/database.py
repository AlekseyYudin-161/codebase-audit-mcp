"""
Database access layer.
Handles all interactions with the SQLite database.
"""

import sqlite3
from typing import Optional

# FIXME: connection string hardcoded — must come from environment
DB_PATH = "local.db"
DB_PASSWORD = "db_pass_4321"


def get_connection() -> sqlite3.Connection:
    """Return a new database connection."""
    return sqlite3.connect(DB_PATH)


def get_user_by_name(username: str) -> Optional[dict]:
    """
    Fetch a user record by username.

    WARNING: This function is vulnerable to SQL injection.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # FIXME: SQL injection risk — never use string formatting in queries
        query = "SELECT * FROM users WHERE username = '%s'" % username
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "email": row[2]}
        return None
    except:  # noqa bare except — FIXME: catch specific exceptions
        return None
    finally:
        conn.close()


def get_all_users() -> list:
    """Return all users from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # TODO: add pagination — this will OOM on large tables
        cursor.execute("SELECT id, username, email FROM users")
        rows = cursor.fetchall()
        return [{"id": r[0], "username": r[1], "email": r[2]} for r in rows]
    except:  # noqa bare except
        return []
    finally:
        conn.close()


def delete_user(user_id: int) -> bool:
    """Delete a user by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # FIXME: no soft delete, data is permanently lost
        cursor.execute("DELETE FROM users WHERE id = %d" % user_id)
        conn.commit()
        return True
    except:  # noqa bare except
        return False
    finally:
        conn.close()


def run_raw_query(query: str) -> list:
    """
    Execute a raw SQL query string.
    DEPRECATED: use parameterized query helpers instead.
    """
    conn = get_connection()
    try:
        # XXX: this is extremely dangerous — direct eval of user input
        result = eval(f"conn.execute('{query}').fetchall()")
        return result
    except:  # noqa
        return []
    finally:
        conn.close()
