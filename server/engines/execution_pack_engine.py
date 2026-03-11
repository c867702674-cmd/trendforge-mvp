#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
PACKS_PER_TREND = int(os.getenv("PACKS_PER_TREND", "3"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS execution_packs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      listing_id INTEGER,
      pack_json TEXT,
      score REAL DEFAULT 0,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_execution_packs_trend ON execution_packs(trend_id);
    """); conn.commit()
def fetch_top_listings(conn, trend_id, limit):
    return conn.execute("""
        SELECT id, title, bullets_json, description, tags_json, COALESCE(rank_score,0) AS rank_score
        FROM listing_drafts
        WHERE trend_id=?
        ORDER BY rank_score DESC, id ASC
        LIMIT ?
    """, (trend_id, limit)).fetchall()
def fetch_trends(conn):
    return conn.execute("SELECT id, term FROM trends WHERE action_level='DO_NOW' ORDER BY hit_score DESC LIMIT 80").fetchall()
def fetch_concepts(conn, trend_id, limit=3):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='design_concepts'").fetchone():
        return []
    rows = conn.execute("SELECT concept, style FROM design_concepts WHERE trend_id=? ORDER BY score DESC, id ASC LIMIT ?", (trend_id, limit)).fetchall()
    return [{"concept": str(r["concept"]), "style": str(r["style"] or "")} for r in rows]
def fetch_gaps(conn, trend_id):
    rows = conn.execute("SELECT gap_type, gap_score FROM market_gaps WHERE trend_id=? ORDER BY gap_score DESC, id ASC LIMIT 3", (trend_id,)).fetchall()
    return [{"gap_type": str(r["gap_type"]), "gap_score": float(r["gap_score"] or 0)} for r in rows]
def fetch_niches(conn, trend_id):
    rows = conn.execute("SELECT niche_term, signal_score FROM niche_signals WHERE trend_id=? ORDER BY signal_score DESC, id ASC LIMIT 5", (trend_id,)).fetchall()
    return [{"niche_term": str(r["niche_term"]), "signal_score": float(r["signal_score"] or 0)} for r in rows]
def main():
    conn = connect(); ensure_schema(conn); trends = fetch_trends(conn); inserted = 0
    for tr in trends:
        trend_id, term = int(tr["id"]), str(tr["term"] or "")
        conn.execute("DELETE FROM execution_packs WHERE trend_id=?", (trend_id,))
        listings = fetch_top_listings(conn, trend_id, PACKS_PER_TREND)
        concepts = fetch_concepts(conn, trend_id, 3); gaps = fetch_gaps(conn, trend_id); niches = fetch_niches(conn, trend_id)
        for ld in listings:
            try: bullets = json.loads(ld["bullets_json"] or "[]")
            except Exception: bullets = []
            try: tags = json.loads(ld["tags_json"] or "[]")
            except Exception: tags = []
            payload = {
                "trend_term": term,
                "listing_id": int(ld["id"]),
                "title": str(ld["title"] or ""),
                "bullets": bullets,
                "description": str(ld["description"] or ""),
                "tags": tags,
                "rank_score": float(ld["rank_score"] or 0),
                "design_concepts": concepts,
                "market_gaps": gaps,
                "niche_signals": niches,
            }
            conn.execute("INSERT INTO execution_packs(trend_id, listing_id, pack_json, score, created_at) VALUES (?, ?, ?, ?, ?)",
                         (trend_id, int(ld["id"]), json.dumps(payload, ensure_ascii=False), float(ld["rank_score"] or 0), utc_now_iso()))
            inserted += 1
    conn.commit(); print(f"[OK] execution_pack_engine inserted={inserted} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
