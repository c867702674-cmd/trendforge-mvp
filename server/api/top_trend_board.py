#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")
BOARD_LIMIT = int(os.getenv("TREND_BOARD_LIMIT", "50"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def fetch_board(conn):
    rows = conn.execute("SELECT id, term, action_level, COALESCE(hit_score,0) AS hit_score, COALESCE(growth,0) AS growth FROM trends ORDER BY hit_score DESC, id ASC LIMIT ?", (BOARD_LIMIT,)).fetchall()
    return [dict(r) for r in rows]
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect(); board = fetch_board(conn)
    out_path = os.path.join(OUTPUT_DIR, "top_trend_board.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": utc_now_iso(), "items": board}, f, ensure_ascii=False, indent=2)
    print(f"[OK] top_trend_board wrote={out_path} items={len(board)} db={DB_PATH}")
    conn.close()
if __name__ == "__main__": main()
