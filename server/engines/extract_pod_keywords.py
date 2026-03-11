#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, json, sqlite3
from collections import Counter
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
POD_KEYWORD_LIMIT = int(os.getenv("POD_KEYWORD_LIMIT", "200"))
SOURCE = "pod_keywords:extractor:v1"

ALLOW = {
    "retro","vintage","minimalist","aesthetic","line","art","funny","cute","gift",
    "cat","dog","mom","dad","teacher","nurse","cowboy","boho","sunset","flower",
    "skull","dragon","bee","patch","sticker","mug","hoodie","shirt","tshirt",
    "svg","poster","embroidery","typography","graphic","valentine","christmas",
    "halloween","birthday","golf"
}
STOP = {"the","and","for","with","from","this","that","your","our","their","you","are","watch","live","score","match","game","news","storm","forecast","club","america","fc","vs","recall","update","outfit","concert","ticket","tour"}

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def date_str(): return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS pod_keywords (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT, country TEXT, source TEXT, keyword TEXT, score REAL DEFAULT 0, payload_json TEXT, created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_pod_keywords_date ON pod_keywords(date);
    CREATE INDEX IF NOT EXISTS idx_pod_keywords_source ON pod_keywords(source);
    CREATE INDEX IF NOT EXISTS idx_pod_keywords_keyword ON pod_keywords(keyword);
    CREATE TABLE IF NOT EXISTS trend_source_health (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL, run_at TEXT NOT NULL, ok INTEGER NOT NULL DEFAULT 0, inserted_count INTEGER NOT NULL DEFAULT 0, error TEXT
    );
    """)
    conn.commit()

def log_health(conn, ok, inserted, error=""):
    conn.execute("INSERT INTO trend_source_health(source, run_at, ok, inserted_count, error) VALUES (?, ?, ?, ?, ?)",
                 (SOURCE, utc_now_iso(), int(ok), int(inserted), error[:2000]))
    conn.commit()

def tokenize(text):
    t = (text or "").lower()
    t = re.sub(r"[^a-z0-9\s&'-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return [x for x in t.split() if len(x) >= 3]

def main():
    conn = connect()
    try:
        ensure_schema(conn)
        rows = conn.execute("SELECT term, source, COALESCE(score,0) AS score FROM raw_trends WHERE country=? ORDER BY id DESC LIMIT 2000", (COUNTRY,)).fetchall()
        c = Counter(); meta = {}
        for r in rows:
            term, src, base = str(r["term"] or ""), str(r["source"] or ""), float(r["score"] or 0)
            for tk in tokenize(term):
                if tk in STOP: continue
                if tk not in ALLOW and len(tk) < 4: continue
                weight = 2.0 if tk in ALLOW else 1.0
                c[tk] += max(1.0, base * 0.05 * weight)
                meta.setdefault(tk, {"sources": set(), "samples": []})
                meta[tk]["sources"].add(src)
                if len(meta[tk]["samples"]) < 3: meta[tk]["samples"].append(term)
        cur = conn.cursor(); inserted = 0
        for kw, score in c.most_common(POD_KEYWORD_LIMIT):
            payload = {"sources": sorted(meta.get(kw, {}).get("sources", set())), "samples": meta.get(kw, {}).get("samples", [])}
            cur.execute("INSERT INTO pod_keywords(date, country, source, keyword, score, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (date_str(), COUNTRY, SOURCE, kw, float(score), json.dumps(payload, ensure_ascii=False), utc_now_iso()))
            inserted += 1
        conn.commit()
        print(f"[OK] extract_pod_keywords inserted={inserted} db={DB_PATH}")
        log_health(conn, 1, inserted, "")
    except Exception as e:
        print(f"[WARN] extract_pod_keywords failed: {e}")
        log_health(conn, 0, 0, str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
