#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge V6.1 - build trends from raw_trends into trends

Run:
  export DB_PATH=/root/trendforge-mvp/server/trendforge.db
  python build_trends_from_raw.py --date 2026-03-05

Notes:
- Non-blocking: if raw_trends empty => upserted=0 but OK
- Creates tables/columns if missing
"""

import os
import json
import math
import argparse
import sqlite3
import datetime


def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc_date():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def log(msg):
    print(msg, flush=True)


def get_db_path():
    return os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "trendforge.db"))


def env_int(k, default):
    try:
        return int(os.getenv(k, str(default)))
    except Exception:
        return default


def env_float(k, default):
    try:
        return float(os.getenv(k, str(default)))
    except Exception:
        return default


def env_str(k, default):
    v = os.getenv(k)
    return v if v is not None and str(v).strip() != "" else default


def ensure_raw_tables(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS raw_trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        country TEXT NOT NULL,
        term TEXT NOT NULL,
        score REAL DEFAULT 0,
        source TEXT NOT NULL,
        payload_json TEXT DEFAULT '{}',
        created_at TEXT DEFAULT ''
    );
    """)
    conn.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_trends_uniq
    ON raw_trends(date, country, term, source);
    """)
    conn.commit()


def ensure_trends_table(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        country TEXT NOT NULL,
        category TEXT DEFAULT 'POD',
        term TEXT NOT NULL,
        growth REAL DEFAULT 0,
        hit_score REAL DEFAULT 0,
        action_level TEXT DEFAULT 'WATCH',
        payload_json TEXT DEFAULT '{}',
        feedback_boost_score REAL DEFAULT 0,
        updated_at TEXT DEFAULT ''
    );
    """)
    conn.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_trends_uniq
    ON trends(date, country, term);
    """)
    conn.commit()

    # add missing columns if older DB
    cols = {r[1] for r in conn.execute("PRAGMA table_info(trends)").fetchall()}
    if "feedback_boost_score" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN feedback_boost_score REAL DEFAULT 0;")
    if "payload_json" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN payload_json TEXT DEFAULT '{}';")
    if "action_level" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN action_level TEXT DEFAULT 'WATCH';")
    if "hit_score" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN hit_score REAL DEFAULT 0;")
    if "growth" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN growth REAL DEFAULT 0;")
    if "updated_at" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN updated_at TEXT DEFAULT '';")
    conn.commit()


def score_to_action(hit_score: float, do_now: float, watch: float) -> str:
    if hit_score >= do_now:
        return "DO_NOW"
    if hit_score >= watch:
        return "WATCH"
    return "IGNORE"


def build_one(conn: sqlite3.Connection, date: str, country: str, category: str):
    """
    Aggregate raw_trends -> trends
    Strategy:
      - group by term; use max(score) and source diversity bonus
      - apply optional feedback_boost_score (if exists)
    """
    ensure_raw_tables(conn)
    ensure_trends_table(conn)

    # thresholds
    DO_NOW_TH = env_float("DO_NOW_THRESHOLD", 500.0)
    WATCH_TH = env_float("WATCH_THRESHOLD", 200.0)
    SOURCE_BONUS = env_float("SOURCE_DIVERSITY_BONUS", 30.0)
    LOG1P_WEIGHT = env_float("LOG1P_WEIGHT", 1.0)

    now = utc_now_iso()

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
        (date, country)
    ).fetchall()

    upserted = 0

    for term, max_score, src_cnt in rows:
        term = (term or "").strip()
        if not term:
            continue

        base = float(max_score or 0)
        diversity = max(0, int(src_cnt or 0) - 1) * SOURCE_BONUS
        # mild log scaling to avoid super huge domination
        hit = (math.log1p(base) * 100.0 * LOG1P_WEIGHT) + diversity

        # try read existing feedback boost (so user actions can affect next pushes)
        fb = 0.0
        try:
            cur = conn.execute(
                "SELECT COALESCE(feedback_boost_score,0) FROM trends WHERE date=? AND country=? AND term=?",
                (date, country, term)
            ).fetchone()
            fb = float((cur[0] if cur else 0) or 0)
        except Exception:
            fb = 0.0
        hit = hit + fb

        action = score_to_action(hit, DO_NOW_TH, WATCH_TH)
        payload = {
            "term": term,
            "raw_max_score": base,
            "src_cnt": int(src_cnt or 0),
            "diversity_bonus": diversity,
            "hit_score": hit,
            "rule": {
                "do_now_th": DO_NOW_TH,
                "watch_th": WATCH_TH,
                "source_bonus": SOURCE_BONUS,
                "log1p_weight": LOG1P_WEIGHT
            },
            "built_at": now,
            "sources": [],
        }

        # keep a few sample sources
        src_rows = conn.execute(
            """
            SELECT source, COALESCE(score,0), payload_json
            FROM raw_trends
            WHERE date=? AND country=? AND term=?
            ORDER BY COALESCE(score,0) DESC
            LIMIT 5
            """,
            (date, country, term)
        ).fetchall()
        for s, sc, pj in src_rows:
            item = {"source": s, "score": float(sc or 0)}
            try:
                if pj:
                    obj = json.loads(pj)
                    # keep minimal
                    for k in ("pubDate", "approx_traffic", "permalink"):
                        if k in obj:
                            item[k] = obj.get(k)
            except Exception:
                pass
            payload["sources"].append(item)

        # upsert by (date,country,term)
        conn.execute(
            """
            INSERT INTO trends(date, country, category, term, growth, hit_score, action_level, payload_json, feedback_boost_score, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(date, country, term) DO UPDATE SET
                category=excluded.category,
                growth=excluded.growth,
                hit_score=excluded.hit_score,
                action_level=excluded.action_level,
                payload_json=excluded.payload_json,
                updated_at=excluded.updated_at
            """,
            (date, country, category, term, base, hit, action, json.dumps(payload, ensure_ascii=False), fb, now)
        )
        upserted += 1

    conn.commit()
    return upserted, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=os.getenv("TF_DATE", ""), help="YYYY-MM-DD, default today(UTC)")
    ap.add_argument("--country", default=os.getenv("COUNTRY", "US"), help="country, default US")
    ap.add_argument("--category", default=env_str("CATEGORY", "POD"), help="category label, default POD")
    args = ap.parse_args()

    db = get_db_path()
    date = args.date.strip() or today_utc_date()
    country = args.country.upper().strip()
    category = args.category.strip() or "POD"

    log(f"[INFO] db={db}")
    log(f"[INFO] build_trends_from_raw date={date} country={country} category={category}")

    conn = sqlite3.connect(db)
    upserted, raw_grouped = build_one(conn, date=date, country=country, category=category)
    conn.close()

    log(f"[OK] build_trends_from_raw date={date} upserted={upserted} (from raw grouped={raw_grouped}) db={db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())