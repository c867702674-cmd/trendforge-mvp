#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, hashlib, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
JSON_PATH = os.getenv("TIKTOK_SOUND_TRENDS_JSON_PATH", "").strip()
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
SOURCE = f"tiktok:sounds:v1:{COUNTRY}"

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

def insert_rows(conn, items):
    cur = conn.cursor()
    raw_inserted = 0
    signal_inserted = 0
    for rank, item in enumerate(items, start=1):
        term = str(item.get("term") or item.get("sound") or "").strip().lower()
        if not term:
            continue
        term = " ".join(term.split()[:4])
        score = float(item.get("score") or max(1, 100-rank+1))
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date,country,term,score,source,payload_json,meta_json,dedup_hash,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (date_str(), COUNTRY, term, score, SOURCE,
             json.dumps(item, ensure_ascii=False),
             json.dumps({"fetcher": "fetch_tiktok_sound_trends_v1.py"}, ensure_ascii=False),
             dedup, utc_now_iso()))
        if cur.rowcount > 0:
            raw_inserted += 1
        cur.execute("""INSERT INTO discovery_signals(source,term,signal_type,signal_score,payload_json,created_at)
                       VALUES (?,?,?,?,?,?)""",
                    (SOURCE, term, "tiktok_sound", score, json.dumps(item, ensure_ascii=False), utc_now_iso()))
        signal_inserted += 1
    conn.commit()
    return raw_inserted, signal_inserted

def main():
    conn = connect(); ensure_schema(conn)
    try:
        if not JSON_PATH or not os.path.exists(JSON_PATH):
            print("[WARN] TIKTOK_SOUND_TRENDS_JSON_PATH not set or file missing. Skip sound ingest.")
            return
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("items", [])
        raw_inserted, signal_inserted = insert_rows(conn, items)
        print(f"[OK] fetch_tiktok_sound_trends_v1 raw_inserted={raw_inserted} signals={signal_inserted} db={DB_PATH}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
