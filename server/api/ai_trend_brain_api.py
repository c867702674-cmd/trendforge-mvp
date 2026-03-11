#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")
LIMIT = int(os.getenv("AI_TREND_BRAIN_API_LIMIT", "30"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect()
    rows = conn.execute("""
        SELECT b.trend_id, t.term, b.cluster_label, b.brain_score, b.opportunity_score, b.risk_score,
               COALESCE(n.niche_label, '') AS niche_label,
               COALESCE(n.niche_score, 0) AS niche_score
        FROM ai_trend_brain b
        JOIN trends t ON t.id = b.trend_id
        LEFT JOIN niche_opportunities n ON n.trend_id = b.trend_id
        ORDER BY b.brain_score DESC, b.trend_id ASC
        LIMIT ?
    """, (LIMIT,)).fetchall()
    items = [dict(r) for r in rows]
    out_path = os.path.join(OUTPUT_DIR, "ai_trend_brain_api.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": utc_now_iso(), "items": items}, f, ensure_ascii=False, indent=2)
    print(f"[OK] ai_trend_brain_api wrote={out_path} items={len(items)} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
