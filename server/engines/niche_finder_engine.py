#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
MAX_SIGNALS_PER_TREND = int(os.getenv("NICHE_SIGNALS_PER_TREND", "5"))
NICHE_HINTS = ["gift","mom","dad","teacher","nurse","sports","cat","dog","retro","minimalist","funny","cute","holiday","boho","vintage"]

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS niche_signals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      niche_term TEXT,
      signal_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_niche_signals_trend ON niche_signals(trend_id);
    """); conn.commit()
def fetch_trends(conn):
    return conn.execute("SELECT id, term FROM trends WHERE action_level='DO_NOW' ORDER BY hit_score DESC LIMIT 80").fetchall()
def build_signals(term):
    term_l = (term or "").lower(); out = []
    for idx, hint in enumerate(NICHE_HINTS, start=1):
        score = 0.0
        if hint in term_l: score = 30 + (20 - idx)
        elif hint in {"retro","minimalist","funny","cute","gift"}: score = 10 + (10 - min(idx,10))
        if score > 0: out.append((hint, float(score)))
    toks = [x for x in term_l.split() if x.strip()]
    if toks: out.insert(0, (toks[0], 35.0))
    dedup, seen = [], set()
    for k, s in out:
        if k not in seen:
            seen.add(k); dedup.append((k, s))
    return dedup[:MAX_SIGNALS_PER_TREND]
def main():
    conn = connect(); ensure_schema(conn); trends = fetch_trends(conn); inserted = 0
    for tr in trends:
        trend_id, term = int(tr["id"]), str(tr["term"] or "")
        conn.execute("DELETE FROM niche_signals WHERE trend_id=?", (trend_id,))
        for niche_term, score in build_signals(term):
            conn.execute("INSERT INTO niche_signals(trend_id, niche_term, signal_score, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
                         (trend_id, niche_term, score, json.dumps({"term": term}, ensure_ascii=False), utc_now_iso()))
            inserted += 1
    conn.commit(); print(f"[OK] niche_finder_engine inserted={inserted} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
