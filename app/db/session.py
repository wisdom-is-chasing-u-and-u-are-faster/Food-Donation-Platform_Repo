import sqlite3
import os
import uuid
import time
from pathlib import Path
from contextlib import contextmanager

# Read database URL from environment with safe local SQLite fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./food_donation.db")


def get_db_path() -> str:
    """Extract SQLite database file path from URL or return default."""
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "")
    return "food_donation.db"


@contextmanager
def get_db_connection():
    """Provides a thread-safe connection to the SQLite database with dictionary row factory and busy timeout."""
    db_file = get_db_path()
    conn = sqlite3.connect(db_file, timeout=60.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query_db(query: str, args=(), one=False):
    """Executes a SQL query and returns list of dictionaries or single dictionary."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        r = cur.fetchall()
        cur.close()
        return (dict(r[0]) if r else None) if one else [dict(row) for row in r]


def execute_db(query: str, args=()):
    """Executes a SQL mutation query and commits the transaction."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id


def generate_unique_id(prefix: str) -> str:
    """Generates an collision-resistant unique ID."""
    return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
