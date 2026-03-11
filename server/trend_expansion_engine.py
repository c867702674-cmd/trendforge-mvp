#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TrendForge - Trend Expansion Engine (V1)
---------------------------------------
Purpose:
  Expand 1 trend term into multiple POD design themes (ideas), store in SQLite table design_ideas.

Designed to be inserted into the V6 pipeline after build_trends_from_raw.py and before push_trends_feishu.py.

DB:
  default: /root/trendforge-mvp/server/trendforge.db (can override via env DB_PATH)

Env (optional):
  DB_PATH                 SQLite path
  EXPANSION_COUNTRY       Filter country (default: no filter)
  EXPANSION_LEVEL         'do_now' (default) or 'do_now_and_watch'
  IDEAS_PER_TREND         Max ideas stored per trend (default: 30)
  DELETE_BEFORE_INSERT    '1' (default) delete old ideas for a trend before inserting new ones
  MIN_HIT_SCORE           Only expand trends with hit_score >= this value (default: 0)
"""

import os
import sqlite3
import json
import itertools
from datetime import datetime, timezone
from typing import List, Tuple, Dict

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
EXPANSION_COUNTRY = os.getenv("EXPANSION_COUNTRY", "").strip()
EXPANSION_LEVEL = os.getenv("EXPANSION_LEVEL", "do_now").strip().lower()
IDEAS_PER_TREND = int(os.getenv("IDEAS_PER_TREND", "30"))
DELETE_BEFORE_INSERT = os.getenv("DELETE_BEFORE_INSERT", "1").strip() != "0"
MIN_HIT_SCORE = float(os.getenv("MIN_HIT_SCORE", "0"))

# Basic POD product types (can be extended later)
PRODUCT_TYPES = [
    "shirt",
    "tshirt",
    "hoodie",
    "sweatshirt",
    "crewneck",
    "mug",
    "sticker",
    "poster",
    "tote bag",
    "patch",
    "svg",
]

# Style / art directions (lightweight, safe defaults)
STYLE_MODIFIERS = [
    "vintage",
    "retro",
    "minimalist",
    "aesthetic",
    "distressed",
    "cute",
    "funny",
    "bold",
    "hand drawn",
    "line art",
    "watercolor",
    "cartoon",
]

# Context / niche modifiers (kept generic)
CONTEXT_MODIFIERS = [
    "gift",
    "for mom",
    "for dad",
    "for teachers",
    "for nurses",
    "for dog lovers",
    "for cat lovers",
    "birthday",
    "christmas",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
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
        """
    )
    conn.commit()


def fetch_target_trends(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cur = conn.cursor()

    levels = ["DO_NOW"]
    if EXPANSION_LEVEL in ("do_now_and_watch", "all"):
        levels.append("WATCH")

    where = ["action_level IN ({})".format(",".join(["?" for _ in levels])), "hit_score >= ?"]
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


def normalize_term(term: str) -> str:
    # keep simple: strip spaces, collapse multiple spaces
    t = " ".join(term.strip().split())
    return t


def generate_ideas(term: str) -> List[Tuple[str, float, Dict]]:
    """
    Returns list of (idea, bonus_score, meta)
    bonus_score is relative ranking bonus; final score = trend.hit_score + bonus_score
    """
    t = normalize_term(term)
    ideas: Dict[str, Tuple[float, Dict]] = {}

    def add(idea: str, bonus: float, meta: Dict):
        s = " ".join(idea.strip().split())
        if not s:
            return
        # prefer higher bonus if duplicate
        if s not in ideas or bonus > ideas[s][0]:
            ideas[s] = (bonus, meta)

    # 1) term + product
    for p in PRODUCT_TYPES:
        add(f"{t} {p}", 8.0, {"pattern": "term+product", "product": p})

    # 2) style + term (good for prompt directions)
    for s in STYLE_MODIFIERS:
        add(f"{s} {t}", 6.0, {"pattern": "style+term", "style": s})

    # 3) style + term + product (most useful for sellers)
    for s, p in itertools.product(STYLE_MODIFIERS, PRODUCT_TYPES):
        add(f"{s} {t} {p}", 12.0, {"pattern": "style+term+product", "style": s, "product": p})

    # 4) context + term + product (seasonal / gift)
    for c, p in itertools.product(CONTEXT_MODIFIERS, PRODUCT_TYPES):
        add(f"{t} {c} {p}", 10.0, {"pattern": "term+context+product", "context": c, "product": p})

    # Sort by bonus desc then shorter strings first (more general)
    ranked = sorted(
        [(k, v[0], v[1]) for k, v in ideas.items()],
        key=lambda x: (-x[1], len(x[0]))
    )
    return ranked


def replace_ideas_for_trend(
    conn: sqlite3.Connection,
    trend_id: int,
    trend_term: str,
    trend_hit_score: float
) -> int:
    ranked = generate_ideas(trend_term)[: max(1, IDEAS_PER_TREND)]
    now = utc_now_iso()

    cur = conn.cursor()
    if DELETE_BEFORE_INSERT:
        cur.execute("DELETE FROM design_ideas WHERE trend_id = ?", (trend_id,))

    inserted = 0
    for idea, bonus, meta in ranked:
        score = float(trend_hit_score) + float(bonus)
        cur.execute(
            """
            INSERT OR IGNORE INTO design_ideas
            (trend_id, idea, category, score, meta_json, created_at)
            VALUES (?, ?, 'POD', ?, ?, ?)
            """,
            (trend_id, idea, score, json.dumps(meta, ensure_ascii=False), now)
        )
        if cur.rowcount > 0:
            inserted += 1

    conn.commit()
    return inserted


def main() -> None:
    if IDEAS_PER_TREND <= 0:
        print("IDEAS_PER_TREND must be > 0")
        return

    conn = connect()
    try:
        ensure_schema(conn)
        trends = fetch_target_trends(conn)
        if not trends:
            print("No target trends found for expansion.")
            return

        total = 0
        for tr in trends:
            trend_id = int(tr["id"])
            term = str(tr["term"])
            hit_score = float(tr["hit_score"] or 0)
            inserted = replace_ideas_for_trend(conn, trend_id, term, hit_score)
            total += inserted
            print(f"Expanded trend_id={trend_id} term='{term}' hit_score={hit_score:.2f} -> ideas_inserted={inserted}")

        print(f"Trend Expansion Engine done. total_new_ideas={total}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
