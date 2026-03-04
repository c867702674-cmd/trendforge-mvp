# server/trend_tasks.py
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------
# Debounce rule (recommended)
# -----------------------------
PROMOTE_HITS = 2   # 连续命中>=2 -> 升级 DO_NOW
DEMOTE_MISSES = 2  # 连续未命中>=2 -> 降级 WATCH


def _now_sql() -> str:
    return "datetime('now')"


def normalize_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def make_trend_key(source: str, keyword: str) -> str:
    # stable identity: source + normalized keyword
    return f"{normalize_key(source)}:{normalize_key(keyword)}"


@dataclass
class TaskRow:
    trend_key: str
    task_level: str
    task_status: str
    seen_streak: int
    miss_streak: int


def ensure_task_defaults(conn: sqlite3.Connection) -> None:
    """
    Safety: If table exists but old rows miss new columns, we rely on db.ensure_schema() to add columns.
    This function just exists for future extension; currently no-op.
    """
    return


def upsert_hit(
    conn: sqlite3.Connection,
    *,
    trend_key: str,
    trend_id: Optional[int] = None,
    theme: Optional[str] = None,
    core_keyword: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Tuple[TaskRow, bool]:
    """
    Mark one trend_key as "hit" in this run.
    Returns: (task_row, promoted_today)
    """
    meta_json = json.dumps(meta, ensure_ascii=False) if meta else None

    # Insert if missing
    conn.execute(
        """
        INSERT OR IGNORE INTO trend_tasks (
            trend_key, trend_id, theme, core_keyword,
            task_level, task_status,
            seen_streak, miss_streak,
            created_at, last_seen_at, last_hit_at,
            produced_count, meta_json
        ) VALUES (
            ?, ?, ?, ?,
            'WATCH', 'DOING',
            0, 0,
            datetime('now'), datetime('now'), datetime('now'),
            0, ?
        )
        """,
        (trend_key, trend_id, theme, core_keyword, meta_json),
    )

    # Fetch current
    row = conn.execute(
        """
        SELECT trend_key, task_level, task_status,
               COALESCE(seen_streak,0), COALESCE(miss_streak,0)
        FROM trend_tasks
        WHERE trend_key = ?
        """,
        (trend_key,),
    ).fetchone()

    if not row:
        # Should not happen
        row = (trend_key, "WATCH", "DOING", 0, 0)

    task_level, task_status, seen_streak, miss_streak = row[1], row[2], int(row[3]), int(row[4])

    # If task is DONE/PAUSED, we still update last_seen/last_hit but we do NOT promote.
    new_seen = seen_streak + 1
    new_miss = 0

    promoted_today = False
    new_level = task_level

    if task_status == "DOING":
        if task_level != "DO_NOW" and new_seen >= PROMOTE_HITS:
            new_level = "DO_NOW"
            promoted_today = True

    # Update record
    conn.execute(
        """
        UPDATE trend_tasks
        SET trend_id = COALESCE(?, trend_id),
            theme = COALESCE(?, theme),
            core_keyword = COALESCE(?, core_keyword),
            meta_json = COALESCE(?, meta_json),
            seen_streak = ?,
            miss_streak = ?,
            task_level = ?,
            last_seen_at = datetime('now'),
            last_hit_at = datetime('now')
        WHERE trend_key = ?
        """,
        (trend_id, theme, core_keyword, meta_json, new_seen, new_miss, new_level, trend_key),
    )

    return (
        TaskRow(
            trend_key=trend_key,
            task_level=new_level,
            task_status=task_status,
            seen_streak=new_seen,
            miss_streak=new_miss,
        ),
        promoted_today,
    )


def apply_misses(
    conn: sqlite3.Connection,
    *,
    hit_keys: Iterable[str],
    horizon_days: int = 30,
) -> int:
    """
    For tasks not hit in this run, increment miss_streak and possibly demote DO_NOW -> WATCH.
    Only affects task_status='DOING'.
    We only touch tasks seen recently to avoid inflating old tasks forever.
    Returns number of rows updated.
    """
    hit_set = set(hit_keys)

    # Candidate tasks to mark missed: active + seen in last horizon_days
    rows = conn.execute(
        f"""
        SELECT trend_key, task_level,
               COALESCE(seen_streak,0), COALESCE(miss_streak,0)
        FROM trend_tasks
        WHERE task_status='DOING'
          AND last_seen_at >= datetime('now', '-{int(horizon_days)} day')
        """
    ).fetchall()

    updated = 0
    for r in rows:
        trend_key = r[0]
        if trend_key in hit_set:
            continue

        task_level = r[1] or "WATCH"
        seen_streak = int(r[2] or 0)
        miss_streak = int(r[3] or 0)

        new_seen = 0
        new_miss = miss_streak + 1
        new_level = task_level

        # Demote if DO_NOW missed enough times
        if task_level == "DO_NOW" and new_miss >= DEMOTE_MISSES:
            new_level = "WATCH"

        conn.execute(
            """
            UPDATE trend_tasks
            SET seen_streak = ?,
                miss_streak = ?,
                task_level = ?,
                last_seen_at = datetime('now')
            WHERE trend_key = ?
            """,
            (new_seen, new_miss, new_level, trend_key),
        )
        updated += 1

    return updated


def get_levels_for_keys(conn: sqlite3.Connection, keys: Iterable[str]) -> Dict[str, TaskRow]:
    keys = list(keys)
    if not keys:
        return {}

    placeholders = ",".join(["?"] * len(keys))
    rows = conn.execute(
        f"""
        SELECT trend_key, task_level, task_status,
               COALESCE(seen_streak,0), COALESCE(miss_streak,0)
        FROM trend_tasks
        WHERE trend_key IN ({placeholders})
        """,
        keys,
    ).fetchall()

    out: Dict[str, TaskRow] = {}
    for r in rows:
        out[r[0]] = TaskRow(
            trend_key=r[0],
            task_level=r[1] or "WATCH",
            task_status=r[2] or "DOING",
            seen_streak=int(r[3] or 0),
            miss_streak=int(r[4] or 0),
        )
    return out