#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""TrendForge - Trend Expansion Engine V2
-------------------------------------
Goal:
  Expand only POD-relevant trends into POD design themes (ideas) and store into design_ideas.

Upgrades vs V1:
  1) Uses POD Filter V2 to skip obvious non-POD trends (sports/news/weather/live-score queries).
  2) Uses rank buckets: product + style + niche contexts; controllable per-trend idea count.
  3) Stable "replace per trend" behavior (delete old ideas then insert new), with dedup unique index.

Env:
  DB_PATH                 SQLite path (default /root/trendforge-mvp/server/trendforge.db)
  EXPANSION_COUNTRY       If set, filter by country
  EXPANSION_LEVEL         do_now (default) or do_now_and_watch
  IDEAS_PER_TREND         default 30
  DELETE_BEFORE_INSERT    default 1
  MIN_HIT_SCORE           default 0
  POD_FILTER_MODE         strict (default) or loose
"""

import os
import sqlite3
import json
import itertools
from datetime import datetime, timezone
from typing import List, Dict, Tuple

from trend_filter_pod_v2 import is_pod_term

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
EXPANSION_COUNTRY = os.getenv("EXPANSION_COUNTRY", "").strip()
EXPANSION_LEVEL = os.getenv("EXPANSION_LEVEL", "do_now").strip().lower()
IDEAS_PER_TREND = int(os.getenv("IDEAS_PER_TREND", "30"))
DELETE_BEFORE_INSERT = os.getenv("DELETE_BEFORE_INSERT", "1").strip() != "0"
MIN_HIT_SCORE = float(os.getenv("MIN_HIT_SCORE", "0"))

PRODUCT_TYPES = [
    "shirt","tshirt","hoodie","sweatshirt","crewneck",
    "mug","sticker","poster","tote bag","patch","svg",
]

STYLE_MODIFIERS = [
    "vintage","retro","minimalist","aesthetic","distressed",
    "cute","funny","bold","hand drawn","line art","watercolor","cartoon",
]

NICHES = [
    "dog mom","cat mom","girl dad","boy mom",
    "teacher","nurse","mechanic","cowgirl","gamer",
]

SEASONS = [
    "valentine","christmas","halloween","easter","birthday",
]

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS design_ideas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      idea TEXT NOT NULL,
      category TEXT DEFAULT 'POD',
      score REAL DEFAULT 0,
      meta_json TEXT,
      created_at TEXT NOT NULL
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_design_ideas_trend_idea
    ON design_ideas(trend_id, idea);
    CREATE INDEX IF NOT EXISTS idx_design_ideas_trend
    ON design_ideas(trend_id);
    CREATE INDEX IF NOT EXISTS idx_design_ideas_score
    ON design_ideas(score);
    """)
    conn.commit()

def fetch_target_trends(conn: sqlite3.Connection):
    cur = conn.cursor()
    levels = ["DO_NOW"]
    if EXPANSION_LEVEL in ("do_now_and_watch", "all"):
        levels.append("WATCH")

    where = ["action_level IN ({})".format(",".join(["?"]*len(levels))), "hit_score >= ?"]
    params: List[object] = []
    params.extend(levels)
    params.append(MIN_HIT_SCORE)

    if EXPANSION_COUNTRY:
        where.append("country = ?")
        params.append(EXPANSION_COUNTRY)

    sql = f"""
      SELECT id, date, country, category, term, hit_score, action_level
      FROM trends
      WHERE {' AND '.join(where)}
      ORDER BY hit_score DESC
    """
    cur.execute(sql, params)
    return cur.fetchall()

def norm(s: str) -> str:
    return " ".join((s or "").strip().split())

def add_idea(store: Dict[str, Tuple[float, Dict]], idea: str, bonus: float, meta: Dict):
    x = norm(idea)
    if not x:
        return
    if x not in store or bonus > store[x][0]:
        store[x] = (bonus, meta)

def generate_ideas(term: str) -> List[Tuple[str, float, Dict]]:
    t = norm(term)
    store: Dict[str, Tuple[float, Dict]] = {}

    for p in PRODUCT_TYPES:
        add_idea(store, f"{t} {p}", 8.0, {"pattern":"term+product","product":p})

    for s, p in itertools.product(STYLE_MODIFIERS, PRODUCT_TYPES):
        add_idea(store, f"{s} {t} {p}", 12.0, {"pattern":"style+term+product","style":s,"product":p})

    for n, p in itertools.product(NICHES, PRODUCT_TYPES):
        add_idea(store, f"{t} {n} {p}", 10.0, {"pattern":"term+niche+product","niche":n,"product":p})

    for sea, p in itertools.product(SEASONS, PRODUCT_TYPES):
        add_idea(store, f"{t} {sea} {p}", 9.0, {"pattern":"term+season+product","season":sea,"product":p})

    ranked = sorted([(k,v[0],v[1]) for k,v in store.items()], key=lambda x: (-x[1], len(x[0])))
    return ranked

def replace_ideas(conn: sqlite3.Connection, trend_id: int, term: str, hit_score: float) -> int:
    ranked = generate_ideas(term)[:max(1, IDEAS_PER_TREND)]
    now = utc_now_iso()
    cur = conn.cursor()

    if DELETE_BEFORE_INSERT:
        cur.execute("DELETE FROM design_ideas WHERE trend_id = ?", (trend_id,))

    inserted = 0
    for idea, bonus, meta in ranked:
        score = float(hit_score) + float(bonus)
        cur.execute(
            """INSERT OR IGNORE INTO design_ideas
               (trend_id, idea, category, score, meta_json, created_at)
               VALUES (?, ?, 'POD', ?, ?, ?)""",
            (trend_id, idea, score, json.dumps(meta, ensure_ascii=False), now)
        )
        if cur.rowcount > 0:
            inserted += 1

    conn.commit()
    return inserted

def main():
    if IDEAS_PER_TREND <= 0:
        print("IDEAS_PER_TREND must be > 0")
        return

    conn = connect()
    try:
        ensure_schema(conn)
        trends = fetch_target_trends(conn)
        if not trends:
            print("No target trends found.")
            return

        total_new = 0
        skipped = 0
        for tr in trends:
            tid = int(tr["id"])
            term = str(tr["term"])
            hs = float(tr["hit_score"] or 0)

            ok, reason = is_pod_term(term)
            if not ok:
                skipped += 1
                print(f"SKIP trend_id={tid} term='{term}' hit_score={hs:.2f} reason={reason}")
                continue

            ins = replace_ideas(conn, tid, term, hs)
            total_new += ins
            print(f"OK   trend_id={tid} term='{term}' hit_score={hs:.2f} -> ideas_inserted={ins}")

        print(f"Trend Expansion V2 done. total_new_ideas={total_new} skipped_trends={skipped}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
