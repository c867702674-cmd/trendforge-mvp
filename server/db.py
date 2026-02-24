import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Any, Dict, List

DB_PATH = Path(__file__).resolve().parent / "trendforge.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]  # (cid, name, type, notnull, dflt_value, pk)
    return col in cols


def init_db():
    """
    V1 Schema:
    - 原字段：date/term/country/category/growth/payload_json/created_at
    - 新字段：hit_score/action_level/risk_level/reason
    """
    conn = get_conn()
    cur = conn.cursor()

    # 先创建基础表（含新字段）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        term TEXT NOT NULL,
        country TEXT,
        category TEXT,
        growth REAL,

        hit_score INTEGER,
        action_level TEXT,
        risk_level TEXT,
        reason TEXT,

        payload_json TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # 如果你之前已经创建过旧表，这里做“增量加字段”，避免你必须删库
    # （SQLite 不支持 IF NOT EXISTS ADD COLUMN，所以需要先检测）
    for col_def in [
        ("hit_score", "INTEGER"),
        ("action_level", "TEXT"),
        ("risk_level", "TEXT"),
        ("reason", "TEXT"),
    ]:
        col, typ = col_def
        if not _column_exists(conn, "trends", col):
            cur.execute(f"ALTER TABLE trends ADD COLUMN {col} {typ}")

    conn.commit()
    conn.close()


def insert_trend(
    date: str,
    term: str,
    country: Optional[str] = None,
    category: Optional[str] = None,
    growth: Optional[float] = None,

    hit_score: Optional[int] = None,
    action_level: Optional[str] = None,
    risk_level: Optional[str] = None,
    reason: Optional[str] = None,

    payload_json: Optional[str] = None,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO trends (
        date, term, country, category, growth,
        hit_score, action_level, risk_level, reason,
        payload_json, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date, term, country, category, growth,
        hit_score, action_level, risk_level, reason,
        payload_json, datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


# 兼容你之前叫 upsert_trend 的写法（当前逻辑仍然是 insert）
def upsert_trend(
    date, term,
    country=None, category=None, growth=None,
    hit_score=None, action_level=None, risk_level=None, reason=None,
    payload_json=None
):
    insert_trend(
        date=date, term=term,
        country=country, category=category, growth=growth,
        hit_score=hit_score, action_level=action_level, risk_level=risk_level, reason=reason,
        payload_json=payload_json
    )


def list_trends(limit: int = 200) -> List[Dict[str, Any]]:
    """
    默认按 hit_score desc，其次 growth desc，再按 id desc
    （NULL score 会排在后面）
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM trends
    ORDER BY
      CASE WHEN hit_score IS NULL THEN 1 ELSE 0 END ASC,
      hit_score DESC,
      CASE WHEN growth IS NULL THEN 1 ELSE 0 END ASC,
      growth DESC,
      id DESC
    LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]