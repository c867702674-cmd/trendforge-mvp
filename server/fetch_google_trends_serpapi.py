#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, hashlib, sqlite3
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
GOOGLE_TRENDS_GEO = os.getenv("GOOGLE_TRENDS_GEO", COUNTRY).strip() or "US"
GOOGLE_TRENDS_LIMIT = int(os.getenv("GOOGLE_TRENDS_LIMIT", "20"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()
SOURCE = f"google_trends:serpapi:{GOOGLE_TRENDS_GEO}"

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def date_str():
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
      date TEXT,
      country TEXT,
      term TEXT,
      score REAL,
      source TEXT,
      payload_json TEXT,
      meta_json TEXT,
      dedup_hash TEXT,
      created_at TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_trends_dedup ON raw_trends(dedup_hash);
    CREATE TABLE IF NOT EXISTS trend_source_health (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL,
      run_at TEXT NOT NULL,
      ok INTEGER NOT NULL DEFAULT 0,
      inserted_count INTEGER NOT NULL DEFAULT 0,
      error TEXT
    );
    """)
    conn.commit()

def log_health(conn, ok, inserted, error=""):
    conn.execute(
        "INSERT INTO trend_source_health(source, run_at, ok, inserted_count, error) VALUES (?, ?, ?, ?, ?)",
        (SOURCE, utc_now_iso(), int(ok), int(inserted), error[:2000]),
    )
    conn.commit()

def http_get_json(url, timeout=20):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))

def fetch_serpapi():
    if not SERPAPI_KEY:
        print("[WARN] SERPAPI_KEY not set. Skip Google Trends fetch.")
        return []
    params = {
        "engine": "google_trends_trending_now",
        "geo": GOOGLE_TRENDS_GEO,
        "api_key": SERPAPI_KEY,
    }
    url = "https://serpapi.com/search.json?" + urlencode(params)
    data = http_get_json(url)

    candidates = []
    for key in ("trending_searches", "trending_now", "searches", "organic_results"):
        if isinstance(data.get(key), list):
            candidates = data.get(key)
            break

    out = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        term = item.get("query") or item.get("title") or item.get("name") or item.get("keyword") or ""
        term = str(term).strip()
        if not term:
            continue
        score = item.get("search_volume") or item.get("value") or item.get("score") or item.get("traffic") or 100
        try:
            score = float(str(score).replace(",", "").replace("+", "").strip() or "100")
        except Exception:
            score = 100.0
        out.append({"term": term, "score": score, "payload": item})
    return out[:max(1, GOOGLE_TRENDS_LIMIT)]

def insert_raw(conn, items):
    inserted = 0
    cur = conn.cursor()
    for item in items:
        term = str(item["term"]).strip()
        score = float(item.get("score") or 0)
        payload = item.get("payload") or {}
        meta = {"fetcher": "fetch_google_trends_serpapi.py"}
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute(
            """
            INSERT OR IGNORE INTO raw_trends
            (date, country, term, score, source, payload_json, meta_json, dedup_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date_str(), COUNTRY, term, score, SOURCE,
                json.dumps(payload, ensure_ascii=False),
                json.dumps(meta, ensure_ascii=False),
                dedup, utc_now_iso(),
            ),
        )
        if cur.rowcount > 0:
            inserted += 1
    conn.commit()
    return inserted

def main():
    conn = connect()
    try:
        ensure_schema(conn)
        try:
            items = fetch_serpapi()
            if not items:
                log_health(conn, ok=1 if not SERPAPI_KEY else 0, inserted=0, error="" if not SERPAPI_KEY else "No items returned")
                return
            inserted = insert_raw(conn, items)
            print(f"[OK] google trends serpapi fetched={len(items)} inserted={inserted} db={DB_PATH}")
            log_health(conn, ok=1, inserted=inserted, error="")
        except (HTTPError, URLError, TimeoutError) as e:
            print(f"[WARN] Google Trends fetch failed: {e}")
            log_health(conn, ok=0, inserted=0, error=str(e))
        except Exception as e:
            print(f"[WARN] Google Trends fetch failed: {e}")
            log_health(conn, ok=0, inserted=0, error=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
