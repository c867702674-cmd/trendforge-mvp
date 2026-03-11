#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""TrendForge - MJ Prompt Generator (V1)
---------------------------------------
Goal:
  Generate Midjourney-style prompts from design_ideas and store into design_prompts.

This is template-based (no API needed). Later V2 can use LLM.

Env:
  DB_PATH               SQLite path
  PROMPTS_PER_TREND     default 5 (for each trend, generate prompts for top N ideas by score)
  MODEL_NAME            default 'midjourney'
  PROMPT_STYLE          default 'vector t-shirt design'
"""

import os
import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
PROMPTS_PER_TREND = int(os.getenv("PROMPTS_PER_TREND", "5"))
MODEL_NAME = os.getenv("MODEL_NAME", "midjourney")
PROMPT_STYLE = os.getenv("PROMPT_STYLE", "vector t-shirt design, high contrast, print-ready, clean background")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS design_prompts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      idea_id INTEGER NOT NULL,
      prompt TEXT NOT NULL,
      model TEXT DEFAULT 'midjourney',
      style TEXT,
      score REAL DEFAULT 0,
      meta_json TEXT,
      created_at TEXT NOT NULL
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_design_prompts_idea_model
    ON design_prompts(idea_id, model);
    CREATE INDEX IF NOT EXISTS idx_design_prompts_idea
    ON design_prompts(idea_id);
    CREATE INDEX IF NOT EXISTS idx_design_prompts_score
    ON design_prompts(score);
    """)
    conn.commit()

def build_prompt(idea: str) -> str:
    return f"{idea}, {PROMPT_STYLE}"

def main():
    conn = connect()
    try:
        ensure_schema(conn)
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT trend_id FROM design_ideas")
        trend_ids = [int(r["trend_id"]) for r in cur.fetchall()]
        if not trend_ids:
            print("No design_ideas found. Run expansion first.")
            return

        now = utc_now_iso()
        total = 0

        for tid in trend_ids:
            cur.execute(
                """SELECT id, idea, score
                   FROM design_ideas
                   WHERE trend_id=?
                   ORDER BY score DESC, id ASC
                   LIMIT ?""",
                (tid, PROMPTS_PER_TREND)
            )
            ideas = cur.fetchall()
            for row in ideas:
                idea_id = int(row["id"])
                idea = str(row["idea"])
                score = float(row["score"] or 0)
                prompt = build_prompt(idea)
                meta = {"source":"template_v1"}

                cur.execute(
                    """INSERT OR REPLACE INTO design_prompts
                       (idea_id, prompt, model, style, score, meta_json, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (idea_id, prompt, MODEL_NAME, PROMPT_STYLE, score, json.dumps(meta, ensure_ascii=False), now)
                )
                total += 1

        conn.commit()
        print(f"MJ Prompt Generator done. total_prompts_upserted={total}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
