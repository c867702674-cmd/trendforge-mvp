#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
MAX_ROWS = int(os.getenv("POD_IMAGE_PROMPTS_MAX_ROWS", "200"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS pod_image_prompts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      listing_id INTEGER,
      prompt_type TEXT,
      prompt_text TEXT,
      prompt_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_pod_image_prompts_trend ON pod_image_prompts(trend_id);
    """); conn.commit()
def build_prompt(term, title):
    return (
        f"POD product mockup, clean commercial style, trend theme '{term}', "
        f"design direction based on '{title}', white background, studio lighting, "
        f"high contrast, print-ready composition, ecommerce thumbnail friendly"
    )
def main():
    conn = connect(); ensure_schema(conn)
    rows = conn.execute("""
        SELECT id, trend_id, COALESCE(amazon_title_ai, amazon_title, title) AS ref_title
        FROM listing_drafts
        ORDER BY COALESCE(rank_score,0) DESC, id ASC
        LIMIT ?
    """, (MAX_ROWS,)).fetchall()
    inserted = 0
    for r in rows:
        listing_id = int(r["id"]); trend_id = int(r["trend_id"]); ref_title = str(r["ref_title"] or "")
        trend = conn.execute("SELECT term FROM trends WHERE id=?", (trend_id,)).fetchone()
        term = str(trend["term"] or "") if trend else ""
        prompt = build_prompt(term, ref_title)
        score = min(100.0, 40.0 + len(term.split()) * 4 + len(ref_title.split()) * 1.2)
        conn.execute("DELETE FROM pod_image_prompts WHERE listing_id=?", (listing_id,))
        conn.execute("""INSERT INTO pod_image_prompts
            (trend_id, listing_id, prompt_type, prompt_text, prompt_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (trend_id, listing_id, "mockup_prompt", prompt, float(round(score,2)),
             json.dumps({"term": term, "title": ref_title}, ensure_ascii=False), utc_now_iso()))
        inserted += 1
    conn.commit()
    print(f"[OK] pod_image_prompt_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()
if __name__ == "__main__":
    main()
