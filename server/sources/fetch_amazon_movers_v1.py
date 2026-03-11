#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, json, hashlib, sqlite3
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
SOURCE = f"amazon:movers:v1:{COUNTRY}"
LIMIT = int(os.getenv("AMAZON_MOVERS_LIMIT", "30"))

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

def fetch_html(url):
    req = Request(url, headers={"User-Agent":"Mozilla/5.0","Accept-Language":"en-US,en;q=0.9"})
    with urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")

def parse_terms(html):
    titles = []
    for m in re.finditer(r'alt="([^"]{6,180})"', html, flags=re.I):
        titles.append(m.group(1).strip())
    for m in re.finditer(r'>([^<>]{6,120})</span>', html, flags=re.I):
        txt = m.group(1).strip()
        if any(ch.isalpha() for ch in txt):
            titles.append(txt)
    out, seen = [], set()
    for t in titles:
        t = re.sub(r"[^a-zA-Z0-9\s&'/-]+", " ", t.lower())
        t = " ".join(t.split()[:4]).strip()
        if len(t.split()) >= 2 and t not in seen:
            seen.add(t); out.append(t)
    return out[:LIMIT]

def insert_rows(conn, terms):
    cur = conn.cursor()
    raw_inserted = 0
    signal_inserted = 0
    for rank, term in enumerate(terms, start=1):
        score = float(max(1, 100-rank+1))
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date,country,term,score,source,payload_json,meta_json,dedup_hash,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (date_str(), COUNTRY, term, score, SOURCE,
             json.dumps({"term": term, "rank": rank}, ensure_ascii=False),
             json.dumps({"fetcher": "fetch_amazon_movers_v1.py"}, ensure_ascii=False),
             dedup, utc_now_iso()))
        if cur.rowcount > 0:
            raw_inserted += 1
        cur.execute("""INSERT INTO discovery_signals(source,term,signal_type,signal_score,payload_json,created_at)
                       VALUES (?,?,?,?,?,?)""",
                    (SOURCE, term, "amazon_mover", score,
                     json.dumps({"term": term, "rank": rank}, ensure_ascii=False), utc_now_iso()))
        signal_inserted += 1
    conn.commit()
    return raw_inserted, signal_inserted

def main():
    conn = connect(); ensure_schema(conn)
    try:
        try:
            html = fetch_html("https://www.amazon.com/gp/movers-and-shakers")
            terms = parse_terms(html)
            raw_inserted, signal_inserted = insert_rows(conn, terms)
            print(f"[OK] fetch_amazon_movers_v1 raw_inserted={raw_inserted} signals={signal_inserted} db={DB_PATH}")
        except (HTTPError, URLError, TimeoutError, Exception) as e:
            print(f"[WARN] fetch_amazon_movers_v1 failed err={e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
