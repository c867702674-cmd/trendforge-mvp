#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
MAX_ITEMS = int(os.getenv("AI_NICHE_MAX_ITEMS", "120"))

NICHE_RULES = [
    ("gift_intent", ["gift", "mom", "dad", "teacher", "nurse"]),
    ("pet_niche", ["cat", "dog", "pet"]),
    ("sports_fan", ["golf", "baseball", "sports", "game"]),
    ("decor_niche", ["poster", "wall art", "boho", "minimalist"]),
    ("funny_apparel", ["funny", "humor", "shirt"]),
]

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS niche_opportunities (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      niche_label TEXT,
      niche_score REAL DEFAULT 0,
      competition_score REAL DEFAULT 0,
      demand_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_niche_opportunities_trend ON niche_opportunities(trend_id);
    """); conn.commit()
def analyze(term, hit_score, pod_rel):
    tl = (term or "").lower()
    label = "general_niche"
    for lb, kws in NICHE_RULES:
        if any(k in tl for k in kws):
            label = lb; break
    demand = float(hit_score or 0) * 0.015 + max(0.0, float(pod_rel or 0))
    competition = 8.0
    if any(x in tl for x in ["celtics", "real madrid", "paralympics", "celeb", "election"]):
        competition += 18.0
    if any(x in tl for x in ["minimalist", "retro", "teacher", "nurse", "cat", "dog"]):
        competition -= 3.0
    niche = demand - competition * 0.6
    return label, round(max(niche, -20), 2), round(competition, 2), round(demand, 2)
def main():
    conn = connect(); ensure_schema(conn)
    rows = conn.execute("""
        SELECT id, term, COALESCE(hit_score,0) AS hit_score, COALESCE(pod_relevance_score,0) AS pod_relevance_score
        FROM trends
        ORDER BY hit_score DESC, id ASC
        LIMIT ?
    """, (MAX_ITEMS,)).fetchall()
    inserted = 0
    for r in rows:
        trend_id = int(r["id"]); term = str(r["term"] or "")
        label, niche_score, comp, demand = analyze(term, r["hit_score"], r["pod_relevance_score"])
        conn.execute("DELETE FROM niche_opportunities WHERE trend_id=?", (trend_id,))
        conn.execute("""INSERT INTO niche_opportunities
            (trend_id, niche_label, niche_score, competition_score, demand_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (trend_id, label, niche_score, comp, demand,
             json.dumps({"term": term}, ensure_ascii=False), utc_now_iso()))
        inserted += 1
    conn.commit()
    print(f"[OK] ai_niche_opportunity_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()
if __name__ == "__main__":
    main()
