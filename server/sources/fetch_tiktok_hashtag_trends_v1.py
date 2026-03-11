#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3, hashlib
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
SOURCE = f"tiktok:hashtag:v1:{COUNTRY}"
JSON_PATH = os.getenv("TIKTOK_HASHTAG_TRENDS_JSON_PATH", "").strip()

FALLBACK_ITEMS = [
    {"term": "coquette room decor", "score": 92},
    {"term": "teacher survival kit", "score": 88},
    {"term": "soft girl cat hoodie", "score": 86},
    {"term": "clean girl desk setup", "score": 84},
    {"term": "dog mom gift", "score": 83},
    {"term": "nurse night shift", "score": 82},
    {"term": "minimalist dorm decor", "score": 81},
    {"term": "retro varsity shirt", "score": 80},
]

def utc():
    return datetime.now(timezone.utc).isoformat()

def dstr():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS raw_trends (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT, country TEXT, term TEXT, score REAL, source TEXT,
      payload_json TEXT, meta_json TEXT, dedup_hash TEXT, created_at TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_trends_dedup ON raw_trends(dedup_hash);

    CREATE TABLE IF NOT EXISTS tiktok_trend_signals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL,
      trend_type TEXT,
      term TEXT NOT NULL,
      signal_score REAL DEFAULT 0,
      intent_label TEXT,
      payload_json TEXT,
      created_at TEXT
    );
    """)
    conn.commit()

def norm(term):
    return " ".join(str(term).strip().lower().split()[:4])

def load_items():
    if JSON_PATH and os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("items", [])
    return FALLBACK_ITEMS

def main():
    conn = connect(); ensure_schema(conn)
    items = load_items()
    cur = conn.cursor()
    raw_inserted = 0
    signal_inserted = 0
    for idx, item in enumerate(items, start=1):
        term = norm(item.get("term"))
        if not term:
            continue
        score = float(item.get("score") or max(1, 100 - idx + 1))
        dedup = sha1(f"{dstr()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date,country,term,score,source,payload_json,meta_json,dedup_hash,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (dstr(), COUNTRY, term, score, SOURCE,
             json.dumps(item, ensure_ascii=False),
             json.dumps({"fetcher":"fetch_tiktok_hashtag_trends_v1.py"}, ensure_ascii=False),
             dedup, utc()))
        if cur.rowcount > 0:
            raw_inserted += 1
        cur.execute("""INSERT INTO tiktok_trend_signals
            (source,trend_type,term,signal_score,intent_label,payload_json,created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (SOURCE, "hashtag", term, score, "", json.dumps(item, ensure_ascii=False), utc()))
        signal_inserted += 1
    conn.commit()
    print(f"[OK] fetch_tiktok_hashtag_trends_v1 raw_inserted={raw_inserted} signals={signal_inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
