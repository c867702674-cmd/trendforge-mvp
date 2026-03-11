#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
TOP_RANK_PREVIEW = int(os.getenv("TOP_RANK_PREVIEW", "20"))

def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn

def ensure_columns(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts);").fetchall()]
    if "rank_score" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN rank_score REAL DEFAULT 0;")
    conn.commit()

def main():
    conn = connect(); ensure_columns(conn)
    rows = conn.execute("""
        SELECT ld.id, ld.trend_id, ld.title, COALESCE(ld.rank_score,0) AS rank_score,
               COALESCE(t.hit_score,0) AS hit_score
        FROM listing_drafts ld
        LEFT JOIN trends t ON t.id = ld.trend_id
        ORDER BY hit_score DESC, rank_score DESC, ld.id ASC
    """).fetchall()
    updated = 0
    for r in rows:
        combined = float(r["rank_score"]) + float(r["hit_score"]) * 0.01
        conn.execute("UPDATE listing_drafts SET rank_score=? WHERE id=?", (combined, int(r["id"])))
        updated += 1
    conn.commit()
    preview = conn.execute("SELECT id, trend_id, title, COALESCE(rank_score,0) AS rank_score FROM listing_drafts ORDER BY rank_score DESC, id ASC LIMIT ?", (TOP_RANK_PREVIEW,)).fetchall()
    print(f"[OK] listing_ranker updated={updated} preview_top={len(preview)} db={DB_PATH}")
    for r in preview[:10]:
        print(f"[TOP] listing_id={r['id']} trend_id={r['trend_id']} rank_score={float(r['rank_score']):.2f} title={str(r['title'])[:120]}")
    conn.close()

if __name__ == "__main__": main()
