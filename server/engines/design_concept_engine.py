#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
CONCEPTS_PER_TREND = int(os.getenv("CONCEPTS_PER_TREND", "3"))
STYLE_POOL = ["minimalist line art","retro typography","vintage distressed","cute cartoon","bold graphic","aesthetic collage"]

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS design_concepts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      concept TEXT NOT NULL,
      style TEXT,
      score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_design_concepts_trend ON design_concepts(trend_id);
    """); conn.commit()
def fetch_trends(conn):
    return conn.execute("SELECT id, term, COALESCE(hit_score,0) AS hit_score FROM trends WHERE action_level='DO_NOW' ORDER BY hit_score DESC LIMIT 50").fetchall()
def fetch_ideas(conn, trend_id, limit=3):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='design_ideas'").fetchone(): return []
    return conn.execute("SELECT idea, COALESCE(score,0) AS score FROM design_ideas WHERE trend_id=? ORDER BY score DESC, id ASC LIMIT ?", (trend_id, limit)).fetchall()
def build_concepts(term, ideas):
    ideas_txt = [str(r["idea"]) for r in ideas] if ideas else [term]
    out = []
    for i, style in enumerate(STYLE_POOL[:max(1, CONCEPTS_PER_TREND)]):
        seed = ideas_txt[i % len(ideas_txt)]
        out.append((f"{style} {seed}", style, float(100 - i)))
    return out[:CONCEPTS_PER_TREND]
def main():
    conn = connect(); ensure_schema(conn); trends = fetch_trends(conn); inserted = 0
    for tr in trends:
        trend_id, term = int(tr["id"]), str(tr["term"])
        ideas = fetch_ideas(conn, trend_id, CONCEPTS_PER_TREND)
        concepts = build_concepts(term, ideas)
        conn.execute("DELETE FROM design_concepts WHERE trend_id=?", (trend_id,))
        for concept, style, score in concepts:
            conn.execute("INSERT INTO design_concepts(trend_id, concept, style, score, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                         (trend_id, concept, style, score, json.dumps({"term": term}, ensure_ascii=False), utc_now_iso()))
            inserted += 1
    conn.commit(); print(f"[OK] design_concept_engine inserted={inserted} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
