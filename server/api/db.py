import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_DB_PATH = str(Path(__file__).resolve().parents[2] / "trendforge.db")


def get_db_path() -> str:
    # Allow override via environment
    return os.environ.get("TREND_DB_PATH", DEFAULT_DB_PATH)


def connect() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_json_loads(s: Any) -> Dict[str, Any]:
    if not s:
        return {}
    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except Exception:
        return {}


def _allowed_sort(sort: str) -> str:
    """
    Whitelist sortable columns to avoid SQL injection.
    """
    mapping = {
        "hit_score": "hit_score",
        "growth": "growth",
        "date": "date",
        "id": "id",
    }
    return mapping.get(sort, "hit_score")


def _allowed_order(order: str) -> str:
    return "ASC" if str(order).lower() == "asc" else "DESC"


def fetch_trends(
    status: Optional[str],
    country: Optional[str],
    category: Optional[str],
    limit: int,
    offset: int,
    sort: str,
    order: str,
) -> Tuple[int, List[Dict[str, Any]]]:
    where = []
    params: List[Any] = []

    if status:
        # action_level is your state (DO_NOW/DOING/WATCH)
        where.append("action_level = ?")
        params.append(status)

    if country:
        where.append("country = ?")
        params.append(country)

    if category:
        where.append("category = ?")
        params.append(category)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sort_col = _allowed_sort(sort)
    sort_order = _allowed_order(order)

    with connect() as conn:
        # total
        total_sql = f"SELECT COUNT(1) AS cnt FROM trends {where_sql}"
        total = conn.execute(total_sql, params).fetchone()["cnt"]

        # items
        items_sql = f"""
        SELECT
          id, date, country, category, term, growth, hit_score, action_level, payload_json
        FROM trends
        {where_sql}
        ORDER BY
          CASE
            WHEN {sort_col} IS NULL THEN 1 ELSE 0
          END,
          {sort_col} {sort_order},
          id DESC
        LIMIT ? OFFSET ?
        """
        rows = conn.execute(items_sql, params + [limit, offset]).fetchall()

    items: List[Dict[str, Any]] = []
    for r in rows:
        items.append(
            {
                "id": int(r["id"]),
                "date": r["date"],
                "country": r["country"],
                "category": r["category"],
                "term": r["term"],
                "growth": r["growth"],
                "hit_score": r["hit_score"],
                "action_level": r["action_level"],
                "payload_json": _safe_json_loads(r["payload_json"]),
            }
        )

    return int(total), items


def fetch_trend_by_id(trend_id: int) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT
              id, date, country, category, term, growth, hit_score, action_level, payload_json
            FROM trends
            WHERE id = ?
            """,
            [trend_id],
        ).fetchone()

    if not row:
        return None

    return {
        "id": int(row["id"]),
        "date": row["date"],
        "country": row["country"],
        "category": row["category"],
        "term": row["term"],
        "growth": row["growth"],
        "hit_score": row["hit_score"],
        "action_level": row["action_level"],
        "payload_json": _safe_json_loads(row["payload_json"]),
    }


def fetch_summary() -> Dict[str, Any]:
    with connect() as conn:
        total = conn.execute("SELECT COUNT(1) AS cnt FROM trends").fetchone()["cnt"]
        rows = conn.execute(
            """
            SELECT action_level, COUNT(1) AS cnt
            FROM trends
            GROUP BY action_level
            """
        ).fetchall()

    by_status: Dict[str, int] = {}
    for r in rows:
        key = r["action_level"] if r["action_level"] else "UNKNOWN"
        by_status[str(key)] = int(r["cnt"])

    return {"total": int(total), "by_status": by_status}