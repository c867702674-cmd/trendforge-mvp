#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, json, time, random, hashlib, sqlite3
from datetime import datetime, timezone
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
AMAZON_POD_LIMIT_PER_SEED = int(os.getenv("AMAZON_POD_LIMIT_PER_SEED", "18"))
AMAZON_POD_MAX_PAGES = int(os.getenv("AMAZON_POD_MAX_PAGES", "1"))
SOURCE = f"amazon:pod:v2:{COUNTRY}"
SEEDS = ["retro shirt","funny cat shirt","minimalist line art","teacher gift","nurse shirt","dog mom mug","boho wall art","embroidery patch"]
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
]
def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def date_str(): return datetime.now(timezone.utc).strftime("%Y-%m-%d")
def sha1(s): return hashlib.sha1(s.encode("utf-8")).hexdigest()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS raw_trends (
      id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, country TEXT, term TEXT, score REAL, source TEXT, payload_json TEXT, meta_json TEXT, dedup_hash TEXT, created_at TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_trends_dedup ON raw_trends(dedup_hash);
    CREATE TABLE IF NOT EXISTS trend_source_health (
      id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, run_at TEXT NOT NULL, ok INTEGER NOT NULL DEFAULT 0, inserted_count INTEGER NOT NULL DEFAULT 0, error TEXT
    );
    """); conn.commit()
def log_health(conn, ok, inserted, error=""):
    conn.execute("INSERT INTO trend_source_health(source, run_at, ok, inserted_count, error) VALUES (?, ?, ?, ?, ?)",
                 (SOURCE, utc_now_iso(), int(ok), int(inserted), error[:2000])); conn.commit()
def fetch_html(url):
    req = Request(url, headers={"User-Agent": random.choice(UAS), "Accept-Language": "en-US,en;q=0.9"})
    with urlopen(req, timeout=20) as resp: return resp.read().decode("utf-8", errors="replace")
def parse_titles(html):
    titles = []
    for m in re.finditer(r'alt="([^"]{4,220})"', html, flags=re.I):
        t = m.group(1).strip()
        if len(t.split()) >= 2: titles.append(t)
    out, seen = [], set()
    for t in titles:
        k = t.lower()
        if k not in seen: seen.add(k); out.append(t)
    return out
def norm_term(title):
    t = re.sub(r"[^a-z0-9\s&'-]+", " ", title.lower())
    t = re.sub(r"\s+", " ", t).strip()
    return " ".join(t.split()[:4]).strip()
def insert_raw(conn, seed, terms):
    inserted = 0; cur = conn.cursor()
    for rank, term in enumerate(terms[:AMAZON_POD_LIMIT_PER_SEED], start=1):
        if not term: continue
        score = max(1, 100 - rank + 1)
        payload = {"seed": seed, "rank": rank, "term": term}
        meta = {"fetcher": "fetch_amazon_pod_terms_v2.py"}
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date, country, term, score, source, payload_json, meta_json, dedup_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (date_str(), COUNTRY, term, float(score), SOURCE, json.dumps(payload, ensure_ascii=False), json.dumps(meta, ensure_ascii=False), dedup, utc_now_iso()))
        if cur.rowcount > 0: inserted += 1
    conn.commit(); return inserted
def main():
    conn = connect(); ensure_schema(conn); total_inserted = 0; failed = 0
    try:
        for seed in SEEDS:
            seed_inserted = 0
            for page in range(1, AMAZON_POD_MAX_PAGES + 1):
                try:
                    url = f"https://www.amazon.com/s?k={quote_plus(seed)}&page={page}"
                    html = fetch_html(url); titles = parse_titles(html); terms = [norm_term(t) for t in titles if norm_term(t)]
                    seed_inserted += insert_raw(conn, seed, terms)
                    print(f"[OK] amazon pod v2 seed={seed} page={page} parsed={len(terms)} inserted={seed_inserted}")
                    time.sleep(random.uniform(0.8, 1.6))
                except (HTTPError, URLError, TimeoutError) as e:
                    print(f"[WARN] amazon pod v2 failed seed={seed} page={page} err={e}"); failed += 1; break
                except Exception as e:
                    print(f"[WARN] amazon pod v2 failed seed={seed} page={page} err={e}"); failed += 1; break
            total_inserted += seed_inserted
        log_health(conn, 1 if total_inserted > 0 else 0, total_inserted, "" if total_inserted > 0 else f"failed={failed}")
        print(f"[OK] fetch_amazon_pod_terms_v2 done inserted_raw={total_inserted} failed={failed} db={DB_PATH}")
    finally:
        conn.close()
if __name__ == "__main__":
    main()
