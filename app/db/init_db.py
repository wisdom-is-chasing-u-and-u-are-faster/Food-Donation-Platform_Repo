import os
import sys
import sqlite3
from pathlib import Path

# Add project root to sys.path for standalone script execution
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.db.session import get_db_connection


def init_database(force_reseed: bool = False):
    """Initializes the database schema and loads seed data if needed."""
    schema_path = repo_root / "db" / "schema.sql"
    seed_path = repo_root / "db" / "seed.sql"

    if not schema_path.exists():
        schema_path = Path("db/schema.sql")
    if not seed_path.exists():
        seed_path = Path("db/seed.sql")

    with get_db_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        cursor = conn.cursor()
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
                cursor.executescript(schema_sql)

        # Check if organizations exist, if not run seed
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]

        if (org_count == 0 or force_reseed) and seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as f:
                seed_sql = f.read()
                cursor.executescript(seed_sql)

        conn.commit()


if __name__ == "__main__":
    init_database(force_reseed=True)
    print("Database initialized and seeded successfully.")
