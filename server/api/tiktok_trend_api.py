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
    signals = conn.execute("""
        SELECT trend_type, term, signal_score, intent_label
        FROM tiktok_trend_signals
        ORDER BY signal_score DESC, id DESC
        LIMIT 30
    """).fetchall()
    bridges = conn.execute("""
        SELECT source_term, bridge_term, bridge_score
        FROM tiktok_semantic_links
        ORDER BY bridge_score DESC, id DESC
        LIMIT 40
    """).fetchall()
    out = {
        "generated_at": utc(),
        "signals": [dict(r) for r in signals],
        "bridges": [dict(r) for r in bridges],
    }
    out_path = os.path.join(OUTPUT_DIR, "tiktok_trend_api.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[OK] tiktok_trend_api wrote={out_path}")
    conn.close()

if __name__ == "__main__":
    main()
