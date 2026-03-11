#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
MAX_TRENDS = int(os.getenv("AI_TREND_BRAIN_MAX_TRENDS", "120"))

CLUSTER_RULES = [
    ("sports_fandom", ["baseball", "golf", "celtics", "sports", "game"]),
    ("teacher_gift", ["teacher", "classroom", "school"]),
    ("nurse_healthcare", ["nurse", "medical", "hospital", "healthcare"]),
    ("pet_lovers", ["cat", "dog", "pet", "kitty", "puppy"]),
    ("retro_typography", ["retro", "vintage", "typography", "distressed"]),
    ("minimalist_art", ["minimalist", "line art", "outline", "clean"]),
    ("boho_decor", ["boho", "wall art", "earth tone", "poster"]),
]

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS ai_trend_brain (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      cluster_label TEXT,
      brain_score REAL DEFAULT 0,
      opportunity_score REAL DEFAULT 0,
      risk_score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_ai_trend_brain_trend ON ai_trend_brain(trend_id);
    """); conn.commit()
def pick_cluster(term):
    tl = (term or "").lower()
    for label, kws in CLUSTER_RULES:
        if any(k in tl for k in kws):
            return label
    return "general_pod"
def compute_scores(hit_score, pod_rel, term):
    tl = (term or "").lower()
    risk = 0.0
    if any(x in tl for x in ["war", "election", "storm", "forecast", "hurricane", "recall"]):
        risk += 35.0
    if len(tl.split()) <= 2:
        risk += 8.0
    opportunity = float(hit_score or 0) * 0.02 + float(pod_rel or 0) * 1.5 - risk * 0.4
    brain = opportunity + max(0.0, 20 - risk)
    return round(brain, 2), round(opportunity, 2), round(risk, 2)
def main():
    conn = connect(); ensure_schema(conn)
    rows = conn.execute("""
        SELECT id, term, COALESCE(hit_score,0) AS hit_score, COALESCE(pod_relevance_score,0) AS pod_relevance_score
        FROM trends
        ORDER BY hit_score DESC, id ASC
        LIMIT ?
    """, (MAX_TRENDS,)).fetchall()
    inserted = 0
    for r in rows:
        trend_id = int(r["id"]); term = str(r["term"] or "")
        cluster = pick_cluster(term)
        brain, opp, risk = compute_scores(r["hit_score"], r["pod_relevance_score"], term)
        conn.execute("DELETE FROM ai_trend_brain WHERE trend_id=?", (trend_id,))
        conn.execute("""INSERT INTO ai_trend_brain
            (trend_id, cluster_label, brain_score, opportunity_score, risk_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (trend_id, cluster, brain, opp, risk,
             json.dumps({"term": term, "hit_score": r["hit_score"], "pod_relevance_score": r["pod_relevance_score"]}, ensure_ascii=False),
             utc_now_iso()))
        inserted += 1
    conn.commit()
    print(f"[OK] ai_trend_brain_v1 inserted={inserted} db={DB_PATH}")
    conn.close()
if __name__ == "__main__":
    main()
