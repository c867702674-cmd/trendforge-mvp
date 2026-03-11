#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, hashlib, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "US").strip() or "US"
JSON_PATH = os.getenv("TIKTOK_TRENDS_JSON_PATH", "").strip()
SOURCE = f"tiktok:pod:v1:{COUNTRY}"

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
def insert_raw(conn, items):
    inserted = 0; cur = conn.cursor()
    for item in items:
        term = str(item.get("term") or "").strip()
        if not term: continue
        try: score = float(item.get("score") or 100)
        except Exception: score = 100.0
        dedup = sha1(f"{date_str()}|{COUNTRY}|{term}|{SOURCE}")
        cur.execute("""INSERT OR IGNORE INTO raw_trends
            (date, country, term, score, source, payload_json, meta_json, dedup_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (date_str(), COUNTRY, term, score, SOURCE, json.dumps(item, ensure_ascii=False), json.dumps({"fetcher":"fetch_tiktok_pod_trends_v1.py"}, ensure_ascii=False), dedup, utc_now_iso()))
        if cur.rowcount > 0: inserted += 1
    conn.commit(); return inserted
def main():
    conn = connect(); ensure_schema(conn)
    try:
        if not JSON_PATH:
            print("[WARN] TIKTOK_TRENDS_JSON_PATH not set. Skip TikTok ingest.")
            log_health(conn, 1, 0, "")
            return
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list): raise ValueError("TikTok JSON must be a list")
        inserted = insert_raw(conn, data)
        print(f"[OK] tiktok pod trends ingested={inserted} db={DB_PATH}")
        log_health(conn, 1, inserted, "")
    except Exception as e:
        print(f"[WARN] tiktok pod ingest failed: {e}")
        log_health(conn, 0, 0, str(e))
    finally:
        conn.close()
if __name__ == "__main__":
    main()
