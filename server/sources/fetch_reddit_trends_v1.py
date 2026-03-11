#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, hashlib, sqlite3
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
LIMIT = int(os.getenv("REDDIT_LIMIT", "20"))
SOURCE = f"reddit:trends:v1:{COUNTRY}"

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def date_str(): return datetime.now(timezone.utc).strftime("%Y-%m-%d")
def sha1(s): return hashlib.sha1(s.encode("utf-8")).hexdigest()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS raw_trends (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT, country TEXT, term TEXT, score REAL, source TEXT,
      payload_json TEXT, meta_json TEXT, dedup_hash TEXT, created_at TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_trends_dedup ON raw_trends(dedup_hash);
    CREATE TABLE IF NOT EXISTS trend_source_stats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL, run_at TEXT NOT NULL, ok INTEGER NOT NULL DEFAULT 0,
      inserted_count INTEGER NOT NULL DEFAULT 0, blocked_count INTEGER NOT NULL DEFAULT 0, error TEXT
    );
    """); conn.commit()
def log_stats(conn, ok, inserted, blocked, error=""):
    conn.execute("INSERT INTO trend_source_stats(source, run_at, ok, inserted_count, blocked_count, error) VALUES (?, ?, ?, ?, ?, ?)",
                 (SOURCE, utc_now_iso(), int(ok), int(inserted), int(blocked), error[:2000])); conn.commit()
def fetch_json(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 TrendForge/1.0"})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))
def insert_raw(conn, items):
    inserted = 0; cur = conn.cursor()
    for rank, item in enumerate(items[:LIMIT], start=1):
        term = str(item.get("term") or "").strip()
        if not term: continue
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date, country, term, score, source, payload_json, meta_json, dedup_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (date_str(), COUNTRY, term, float(max(1, 100-rank+1)), SOURCE, json.dumps(item, ensure_ascii=False),
             json.dumps({"fetcher": "fetch_reddit_trends_v1.py"}, ensure_ascii=False), dedup, utc_now_iso()))
        if cur.rowcount > 0: inserted += 1
    conn.commit(); return inserted
def main():
    conn = connect(); ensure_schema(conn)
    try:
        try:
            data = fetch_json("https://www.reddit.com/r/popular.json?limit=25")
            children = data.get("data", {}).get("children", [])
            items = []
            for c in children:
                d = c.get("data", {})
                title = str(d.get("title") or "").strip().lower()
                if title:
                    items.append({"term": " ".join(title.split()[:4]), "subreddit": d.get("subreddit"), "title": title})
            inserted = insert_raw(conn, items)
            log_stats(conn, 1 if inserted > 0 else 0, inserted, 0, "")
            print(f"[OK] fetch_reddit_trends_v1 inserted_raw={inserted} db={DB_PATH}")
        except (HTTPError, URLError, TimeoutError, Exception) as e:
            log_stats(conn, 0, 0, 0, str(e))
            print(f"[WARN] fetch_reddit_trends_v1 failed err={e}")
    finally:
        conn.close()
if __name__ == "__main__":
    main()
