# db.py
# TrendForge - SQLite connection + schema ensure (backward compatible)

import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

DEFAULT_DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "trendforge.db"))


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    )
    return cur.fetchone() is not None


def _get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]  # row[1] = column name


def _ensure_table(conn: sqlite3.Connection, ddl: str) -> None:
    conn.execute(ddl)


def _ensure_column(conn: sqlite3.Connection, table: str, col: str, col_ddl: str) -> None:
    cols = _get_columns(conn, table)
    if col not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_ddl}")


def ensure_schema(conn: sqlite3.Connection) -> None:
    """
    Creates missing tables and columns safely.
    Keeps backward compatibility with your existing DB.
    """
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    # --- existing tables (create only if missing) ---
    if not _table_exists(conn, "trends"):
        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS trends (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              source TEXT,
              keyword TEXT,
              hit_score REAL,
              growth REAL,
              action_level TEXT,
              payload_json TEXT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
        )

    if not _table_exists(conn, "actions"):
        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS actions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              trend_id INTEGER,
              action_type TEXT,
              status TEXT,
              note TEXT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
        )

    if not _table_exists(conn, "push_log"):
        _ensure_table(
            conn,
            """
            CREATE TABLE IF NOT EXISTS push_log (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              channel TEXT,
              webhook_token TEXT,
              message_hash TEXT,
              sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
        )

    # --- D2 fields on trends (safe to add if missing) ---
    # If you already added these, nothing happens.
    _ensure_column(conn, "trends", "core_keyword", "core_keyword TEXT")
    _ensure_column(conn, "trends", "expansion_keywords", "expansion_keywords TEXT")   # JSON string
    _ensure_column(conn, "trends", "variant_directions", "variant_directions TEXT")  # JSON string
    _ensure_column(conn, "trends", "suggested_volume", "suggested_volume INTEGER")
    _ensure_column(conn, "trends", "execution_hint", "execution_hint TEXT")

    # --- D2 field on actions (safe) ---
    _ensure_column(conn, "actions", "produced_count", "produced_count INTEGER DEFAULT 0")
        # ================================
    # Trend -> Task 固化层（新增）
    # ================================
    _ensure_table(
        conn,
        """
        CREATE TABLE IF NOT EXISTS trend_tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          trend_key TEXT NOT NULL UNIQUE,
          trend_id INTEGER,
          theme TEXT,
          core_keyword TEXT,
          task_status TEXT DEFAULT 'DOING',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          produced_count INTEGER DEFAULT 0,
          meta_json TEXT
        );
        """
    )
        # ================================
    # Trend -> Task 固化层（D2 debounce）
    # ================================
    _ensure_table(
        conn,
        """
        CREATE TABLE IF NOT EXISTS trend_tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          trend_key TEXT NOT NULL UNIQUE,
          trend_id INTEGER,
          theme TEXT,
          core_keyword TEXT,
          task_status TEXT DEFAULT 'DOING',     -- DOING / DONE / PAUSED
          task_level TEXT DEFAULT 'WATCH',      -- WATCH / DO_NOW
          seen_streak INTEGER DEFAULT 0,
          miss_streak INTEGER DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          last_hit_at DATETIME,
          produced_count INTEGER DEFAULT 0,
          meta_json TEXT
        );
        """
    )

    # Backward compatible columns (safe add if missing)
    _ensure_column(conn, "trend_tasks", "task_level", "task_level TEXT DEFAULT 'WATCH'")
    _ensure_column(conn, "trend_tasks", "seen_streak", "seen_streak INTEGER DEFAULT 0")
    _ensure_column(conn, "trend_tasks", "miss_streak", "miss_streak INTEGER DEFAULT 0")
    _ensure_column(conn, "trend_tasks", "last_hit_at", "last_hit_at DATETIME")   
    _ensure_column(conn, "trends", "source", "source TEXT DEFAULT 'etsy'")

        # ================================
    # Trend -> Task 固化层（新增）
    # ================================
  
         
     


@contextmanager
def get_conn(db_path: Optional[str] = None):
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_schema(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()