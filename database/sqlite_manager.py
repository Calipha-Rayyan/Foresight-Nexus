"""SQLite-backed lightweight persistence for application state that should
survive across reruns within a session (e.g. saved settings snapshots).
Intentionally minimal — DuckDB (duckdb_manager.py) handles the analytical
querying workload. A future version could swap this for PostgreSQL without
changing the calling code (see repositories.py).
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "app_state.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            settings_json TEXT NOT NULL
        )
    """)
    return conn


def save_settings_snapshot(settings_dict: dict) -> None:
    conn = get_connection()
    conn.execute("INSERT INTO settings_snapshots (settings_json) VALUES (?)",
                 (json.dumps(settings_dict),))
    conn.commit()
    conn.close()


def latest_settings_snapshot() -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT settings_json FROM settings_snapshots ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return json.loads(row[0]) if row else None
