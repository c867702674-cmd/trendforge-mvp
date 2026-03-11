#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge V6 - Build trends from raw_trends -> trends

Reads:
- raw_trends(date,country,term,score,source,created_at,meta_json...)

Writes:
- trends(date,country,category,term,hit_score,action_level,source,created_at,payload_json,feedback_boost_score...)

Env:
- DB_PATH
- COUNTRY (default US)
- CATEGORY (default POD)
- DO_NOW_THRESHOLD (default 500)
- WATCH_THRESHOLD (default 200)
- SOURCE_DIVERSITY_BONUS (default 30)
- LOG1P_WEIGHT (default 1.0)
- POD_FILTER_ON (default 1)
"""

from __future__ import annotations

import os
import json
import math
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

# your POD filter module (you said file name is trend_filter_pod.py)
try:
    from trend_filter_pod import filter_pod_trends
except Exception:
    filter_pod_trends = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except Exception:
        return default


def env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return float(v)
    except Exception:
        return default


def env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return default if v is None or v == "" else v


def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}", flush=True)


TRENDS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS trends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  country TEXT,
  category TEXT,
  term TEXT,
  hit_score REAL,
  action_level TEXT,
  source TEXT,
  created_at TEXT,
  payload_json TEXT,
  feedback_boost_score REAL DEFAULT 0,
  cooldown_until TEXT
);
"""


def ensure_trends_schema(conn: sqlite3.Connection) -> None:
    conn.execute(TRENDS_SCHEMA_SQL)
    conn.commit()

    cols = {r[1] for r in conn.execute("PRAGMA table_info(trends);").fetchall()}
    need = {
        "date": "TEXT",
        "country": "TEXT",
        "category": "TEXT",
        "term": "TEXT",
        "hit_score": "REAL",
        "action_level": "TEXT",
        "source": "TEXT",
        "created_at": "TEXT",
        "payload_json": "TEXT",
        "feedback_boost_score": "REAL",
        "cooldown_until": "TEXT",
    }
    for c, t in need.items():
        if c not in cols:
            conn.execute(f"ALTER TABLE trends ADD COLUMN {c} {t};")
    conn.commit()

    conn.execute("CREATE INDEX IF NOT EXISTS idx_trends_date ON trends(date);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trends_term ON trends(term);")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_trends_day_term ON trends(date,country,category,term);")
    conn.commit()


def build_one(conn: sqlite3.Connection, date: str, country: str, category: str) -> Tuple[int, int]:
    DO_NOW_TH = env_float("DO_NOW_THRESHOLD", 500.0)
    WATCH_TH = env_float("WATCH_THRESHOLD", 200.0)
    SOURCE_BONUS = env_float("SOURCE_DIVERSITY_BONUS", 30.0)
    LOG1P_WEIGHT = env_float("LOG1P_WEIGHT", 1.0)
    POD_FILTER_ON = env_bool("POD_FILTER_ON", True)

    rows = conn.execute(
        """
        SELECT term,
               MAX(COALESCE(score,0)) AS max_score,
               COUNT(DISTINCT source) AS src_cnt
        FROM raw_trends
        WHERE date=? AND country=?
        GROUP BY term
        ORDER BY max_score DESC
        """,
        (date, country),
    ).fetchall()

    raw_grouped = len(rows)

    # --- POD filter compatibility ---
    if POD_FILTER_ON and filter_pod_trends is not None:
        # filter expects (term, score) pairs (common)
        pairs = [(t, float(s or 0.0)) for (t, s, _c) in rows]
        keep_pairs = filter_pod_trends(pairs)
        keep_set = {t for (t, _s) in keep_pairs}
        rows = [r for r in rows if r[0] in keep_set]

    upserted = 0

    ensure_trends_schema(conn)

    for term, max_score, src_cnt in rows:
        term = (term or "").strip()
        if not term:
            continue
        max_score = float(max_score or 0.0)
        src_cnt = int(src_cnt or 0)

        # score formula: max_score + source diversity bonus + log1p
        hit = max_score
        if src_cnt > 1:
            hit += (src_cnt - 1) * SOURCE_BONUS
        hit += math.log1p(max_score) * LOG1P_WEIGHT

        if hit >= DO_NOW_TH:
            lvl = "DO_NOW"
        elif hit >= WATCH_TH:
            lvl = "WATCH"
        else:
            lvl = "IGNORE"

        payload = {
            "date": date,
            "country": country,
            "category": category,
            "max_score": max_score,
            "src_cnt": src_cnt,
            "formula": {"source_bonus": SOURCE_BONUS, "log1p_weight": LOG1P_WEIGHT},
        }

        conn.execute(
            """
            INSERT INTO trends(date,country,category,term,hit_score,action_level,source,created_at,payload_json)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(date,country,category,term) DO UPDATE SET
              hit_score=excluded.hit_score,
              action_level=excluded.action_level,
              source=excluded.source,
              payload_json=excluded.payload_json
            """,
            (
                date, country, category, term, hit, lvl,
                "raw_trends",
                utc_now_iso(),
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        upserted += 1

    conn.commit()
    return upserted, raw_grouped


def main() -> int:
    db_path = env_str("DB_PATH", os.path.join(os.path.dirname(__file__), "trendforge.db"))
    country = env_str("COUNTRY", "US").strip().upper()
    category = env_str("CATEGORY", "POD").strip().upper()
    date = os.getenv("DATE") or today_utc_date()

    log("INFO", f"db={db_path}")
    log("INFO", f"build_trends_from_raw date={date} country={country} category={category}")

    conn = sqlite3.connect(db_path)
    try:
        upserted, raw_grouped = build_one(conn, date=date, country=country, category=category)
        log("OK", f"build_trends_from_raw date={date} upserted={upserted} (from raw grouped={raw_grouped}) db={db_path}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())