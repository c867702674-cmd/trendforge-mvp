#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_columns(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts);").fetchall()]
    if "rank_score" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN rank_score REAL DEFAULT 0;")
    if "quality_json" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN quality_json TEXT;")
    conn.commit()
def fetch_gap_score(conn, trend_id):
    row = conn.execute("SELECT COALESCE(MAX(gap_score),0) AS s FROM market_gaps WHERE trend_id=?", (trend_id,)).fetchone()
    return float(row["s"]) if row else 0.0
def fetch_niche_score(conn, trend_id):
    row = conn.execute("SELECT COALESCE(MAX(signal_score),0) AS s FROM niche_signals WHERE trend_id=?", (trend_id,)).fetchone()
    return float(row["s"]) if row else 0.0
def main():
    conn = connect(); ensure_columns(conn)
    rows = conn.execute("SELECT id, trend_id, COALESCE(rank_score,0) AS rank_score, quality_json FROM listing_drafts ORDER BY id ASC").fetchall()
    updated = 0
    for r in rows:
        ld_id, trend_id = int(r["id"]), int(r["trend_id"])
        base = float(r["rank_score"] or 0); gap = fetch_gap_score(conn, trend_id); niche = fetch_niche_score(conn, trend_id)
        profit_score = base + gap + niche
        try: qj = json.loads(r["quality_json"] or "{}")
        except Exception: qj = {}
        qj["profit_score"] = profit_score; qj["gap_score"] = gap; qj["niche_score"] = niche
        conn.execute("UPDATE listing_drafts SET rank_score=?, quality_json=? WHERE id=?",
                     (profit_score, json.dumps(qj, ensure_ascii=False), ld_id))
        updated += 1
    conn.commit(); print(f"[OK] profit_score_engine updated={updated} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
