#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, json, time, random, hashlib, sqlite3
from datetime import datetime, timezone
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
LIMIT_PER_SEED = int(os.getenv("ETSY_V3_LIMIT_PER_SEED", "18"))
MAX_PAGES = int(os.getenv("ETSY_V3_MAX_PAGES", "1"))
SLEEP_MIN = float(os.getenv("ETSY_V3_SLEEP_MIN", "1.2"))
SLEEP_MAX = float(os.getenv("ETSY_V3_SLEEP_MAX", "2.6"))
SOURCE = f"etsy:public:v3:{COUNTRY}"

SEEDS = ["retro shirt","funny cat shirt","minimalist line art","teacher gift","nurse shirt","dog mom mug","boho wall art","embroidery patch"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
]

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
def fetch_html(url):
    headers = {"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "en-US,en;q=0.9", "Referer": "https://www.etsy.com/", "Cache-Control":"no-cache", "Pragma":"no-cache"}
    req = Request(url, headers=headers)
    with urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")
def parse_titles(html):
    titles = []
    for m in re.finditer(r'"name"\s*:\s*"([^"]{4,180})"', html, flags=re.I):
        titles.append(m.group(1).strip())
    for m in re.finditer(r'alt="([^"]{4,180})"', html, flags=re.I):
        titles.append(m.group(1).strip())
    out, seen = [], set()
    for t in titles:
        k = t.lower()
        if k not in seen and len(k.split()) >= 2:
            seen.add(k); out.append(t)
    return out
def norm_term(title):
    t = re.sub(r"[^a-z0-9\s&'-]+", " ", title.lower())
    t = re.sub(r"\s+", " ", t).strip()
    return " ".join(t.split()[:4]).strip()
def insert_raw(conn, seed, terms):
    inserted = 0; cur = conn.cursor()
    for rank, term in enumerate(terms[:LIMIT_PER_SEED], start=1):
        if not term: continue
        score = max(1, 100-rank+1)
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date, country, term, score, source, payload_json, meta_json, dedup_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (date_str(), COUNTRY, term, float(score), SOURCE, json.dumps({"seed": seed, "rank": rank, "term": term}, ensure_ascii=False),
             json.dumps({"fetcher": "fetch_etsy_pod_v3.py"}, ensure_ascii=False), dedup, utc_now_iso()))
        if cur.rowcount > 0: inserted += 1
    conn.commit(); return inserted
def main():
    conn = connect(); ensure_schema(conn)
    total_inserted = 0; blocked = 0
    try:
        for seed in SEEDS:
            seed_inserted = 0
            for page in range(1, MAX_PAGES+1):
                url = f"https://www.etsy.com/search?q={quote_plus(seed)}&page={page}"
                try:
                    time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))
                    html = fetch_html(url)
                    terms = [norm_term(t) for t in parse_titles(html) if norm_term(t)]
                    seed_inserted += insert_raw(conn, seed, terms)
                    print(f"[OK] etsy v3 seed={seed} page={page} parsed={len(terms)} inserted={seed_inserted}")
                except HTTPError as e:
                    if getattr(e, "code", None) == 403: blocked += 1
                    print(f"[WARN] etsy v3 failed seed={seed} page={page} err={e}")
                    break
                except (URLError, TimeoutError, Exception) as e:
                    print(f"[WARN] etsy v3 failed seed={seed} page={page} err={e}")
                    break
            total_inserted += seed_inserted
        log_stats(conn, 1 if total_inserted > 0 else 0, total_inserted, blocked, "" if total_inserted > 0 else "No inserts")
        print(f"[OK] fetch_etsy_pod_v3 done inserted_raw={total_inserted} blocked={blocked} db={DB_PATH}")
    finally:
        conn.close()
if __name__ == "__main__":
    main()
