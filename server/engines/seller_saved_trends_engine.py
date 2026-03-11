#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DEFAULT_SELLER_EMAIL = os.getenv("DEFAULT_SELLER_EMAIL", "owner@trendforge.local")
SAVE_TOP_N = int(os.getenv("SAVE_TOP_TRENDS_N", "20"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS seller_accounts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      name TEXT,
      tier TEXT DEFAULT 'trial',
      created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS seller_saved_trends (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      seller_id INTEGER NOT NULL,
      trend_id INTEGER NOT NULL,
      note TEXT,
      created_at TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_seller_saved_trends ON seller_saved_trends(seller_id, trend_id);
    """)
    conn.commit()

def main():
    conn = connect(); ensure_schema(conn)
    seller = conn.execute("SELECT id FROM seller_accounts WHERE email=?", (DEFAULT_SELLER_EMAIL,)).fetchone()
    if not seller:
        print(f"[WARN] seller_saved_trends_engine missing seller {DEFAULT_SELLER_EMAIL} db={DB_PATH}")
        conn.close(); return
    seller_id = int(seller["id"])
    trends = conn.execute("""
        SELECT id, term, COALESCE(hit_score,0) AS hit_score
        FROM trends
        WHERE action_level='DO_NOW'
        ORDER BY hit_score DESC, id ASC
        LIMIT ?
    """, (SAVE_TOP_N,)).fetchall()
    inserted = 0
    for tr in trends:
        conn.execute("INSERT OR IGNORE INTO seller_saved_trends(seller_id, trend_id, note, created_at) VALUES (?, ?, ?, ?)",
                     (seller_id, int(tr["id"]), "auto_saved_top_trend", utc_now_iso()))
        if conn.total_changes > inserted:
            inserted += 1
    conn.commit()
    print(f"[OK] seller_saved_trends_engine inserted={inserted} seller_id={seller_id} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
