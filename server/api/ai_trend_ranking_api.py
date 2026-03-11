#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")

def utc():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect()
    rows = conn.execute("""
        SELECT term, brain_score, niche_score, board_score, source_count, rank_score
        FROM ai_trend_rankings
        ORDER BY rank_score DESC, id ASC
        LIMIT 50
    """).fetchall()
    out = {
        "generated_at": utc(),
        "items": [dict(r) for r in rows]
    }
    out_path = os.path.join(OUTPUT_DIR, "ai_trend_ranking_api.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[OK] ai_trend_ranking_api wrote={out_path} items={len(out['items'])}")
    conn.close()

if __name__ == "__main__":
    main()
