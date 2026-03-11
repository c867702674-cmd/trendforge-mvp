#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, hashlib, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
SOURCE = f"etsy:shop_signals:v1:{COUNTRY}"
SEEDS = [
    ("retro teacher shirt", 82),
    ("dog mom mug", 78),
    ("minimalist line art poster", 74),
    ("funny nurse shirt", 76),
    ("boho wall art", 73),
    ("embroidery patch", 69),
]

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def date_str(): return datetime.now(timezone.utc).strftime("%Y-%m-%d")
def sha1(s): return hashlib.sha1(s.encode("utf-8")).hexdigest()

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
    CREATE TABLE IF NOT EXISTS discovery_signals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL,
      term TEXT NOT NULL,
      signal_type TEXT,
      signal_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    """)
    conn.commit()

def main():
    conn = connect(); ensure_schema(conn)
    cur = conn.cursor()
    raw_inserted = 0
    signal_inserted = 0
    for term, score in SEEDS:
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date,country,term,score,source,payload_json,meta_json,dedup_hash,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (date_str(), COUNTRY, term, float(score), SOURCE,
             json.dumps({"term": term, "score": score}, ensure_ascii=False),
             json.dumps({"fetcher": "fetch_etsy_shop_signals_v1.py"}, ensure_ascii=False),
             dedup, utc_now_iso()))
        if cur.rowcount > 0:
            raw_inserted += 1
        cur.execute("""INSERT INTO discovery_signals(source,term,signal_type,signal_score,payload_json,created_at)
                       VALUES (?,?,?,?,?,?)""",
                    (SOURCE, term, "etsy_shop_signal", float(score),
                     json.dumps({"term": term, "score": score}, ensure_ascii=False), utc_now_iso()))
        signal_inserted += 1
    conn.commit()
    print(f"[OK] fetch_etsy_shop_signals_v1 raw_inserted={raw_inserted} signals={signal_inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
