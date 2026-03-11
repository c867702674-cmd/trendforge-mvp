#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
MAX_LINKS_PER_TREND = int(os.getenv("SEMANTIC_LINKS_PER_TREND", "6"))

SEMANTIC_MAP = {
    "winter paralympics": ["adaptive sport", "wheelchair pride", "disabled athlete", "paralympic support"],
    "teacher": ["classroom gift", "teacher appreciation", "school pride", "teacher humor"],
    "nurse": ["healthcare hero", "nurse appreciation", "hospital life", "medical humor"],
    "cat": ["cat mom gift", "kitty line art", "cute pet design", "cat lover shirt"],
    "dog": ["dog mom gift", "puppy line art", "pet lover mug", "dog lover shirt"],
    "golf": ["golf dad gift", "retro golf design", "weekend golfer", "golf humor"],
    "baseball": ["baseball mom gift", "game day shirt", "sports fan mug", "baseball pride"],
    "retro": ["vintage style", "throwback design", "old school typography", "distressed graphic"],
    "minimalist": ["clean line art", "simple graphic", "modern outline", "neutral aesthetic"],
    "boho": ["earth tone decor", "bohemian poster", "boho line art", "organic wall art"],
}

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS semantic_trend_links (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      base_term TEXT NOT NULL,
      expanded_term TEXT NOT NULL,
      link_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_semantic_trend_links_trend
    ON semantic_trend_links(trend_id);
    """)
    conn.commit()

def build_expansions(term):
    tl = (term or "").lower()
    out = []
    for key, expansions in SEMANTIC_MAP.items():
        if key in tl:
            for idx, item in enumerate(expansions, start=1):
                out.append((item, float(40 - idx)))
    toks = tl.split()
    if len(toks) >= 2:
        out.append((f"{toks[0]} gift idea", 16.0))
        out.append((f"{toks[0]} shirt design", 15.0))
    seen = set()
    dedup = []
    for item, score in out:
        if item not in seen:
            seen.add(item)
            dedup.append((item, score))
    return dedup[:MAX_LINKS_PER_TREND]

def main():
    conn = connect(); ensure_schema(conn)
    trends = conn.execute("""
        SELECT id, term
        FROM trends
        WHERE action_level='DO_NOW'
        ORDER BY hit_score DESC, id ASC
        LIMIT 100
    """).fetchall()
    inserted = 0
    for tr in trends:
        trend_id = int(tr["id"])
        term = str(tr["term"] or "")
        conn.execute("DELETE FROM semantic_trend_links WHERE trend_id=?", (trend_id,))
        for expanded_term, score in build_expansions(term):
            conn.execute("""INSERT INTO semantic_trend_links
                (trend_id, base_term, expanded_term, link_score, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (trend_id, term, expanded_term, float(score),
                 json.dumps({"base_term": term, "expanded_term": expanded_term}, ensure_ascii=False),
                 utc_now_iso()))
            inserted += 1
    conn.commit()
    print(f"[OK] trend_semantic_expander_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
