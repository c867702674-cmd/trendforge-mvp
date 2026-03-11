#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS market_gaps (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      gap_type TEXT,
      gap_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_market_gaps_trend ON market_gaps(trend_id);
    """); conn.commit()
def fetch_trends(conn):
    return conn.execute("SELECT id, term FROM trends WHERE action_level='DO_NOW' ORDER BY hit_score DESC LIMIT 80").fetchall()
def detect_gaps(term):
    tl = (term or "").lower(); gaps = []
    if "retro" in tl or "vintage" in tl: gaps.append(("style_gap", 28.0))
    if "gift" in tl or "mom" in tl or "dad" in tl: gaps.append(("gift_intent_gap", 30.0))
    if "sports" in tl or "golf" in tl or "baseball" in tl: gaps.append(("fan_merch_gap", 24.0))
    if "cat" in tl or "dog" in tl: gaps.append(("pet_niche_gap", 22.0))
    if not gaps: gaps.append(("general_fast_test_gap", 12.0))
    return gaps[:3]
def main():
    conn = connect(); ensure_schema(conn); trends = fetch_trends(conn); inserted = 0
    for tr in trends:
        trend_id, term = int(tr["id"]), str(tr["term"] or "")
        conn.execute("DELETE FROM market_gaps WHERE trend_id=?", (trend_id,))
        for gap_type, score in detect_gaps(term):
            conn.execute("INSERT INTO market_gaps(trend_id, gap_type, gap_score, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
                         (trend_id, gap_type, score, json.dumps({"term": term}, ensure_ascii=False), utc_now_iso()))
            inserted += 1
    conn.commit(); print(f"[OK] market_gap_detector inserted={inserted} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
