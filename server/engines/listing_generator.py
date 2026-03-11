#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
LISTINGS_PER_TREND = int(os.getenv("LISTINGS_PER_TREND", "5"))
PLATFORM = os.getenv("LISTING_PLATFORM", "amazon")

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS listing_drafts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      concept_id INTEGER,
      sku_pack_id INTEGER,
      platform TEXT DEFAULT 'amazon',
      title TEXT,
      bullets_json TEXT,
      description TEXT,
      tags_json TEXT,
      score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_listing_drafts_trend ON listing_drafts(trend_id);
    CREATE INDEX IF NOT EXISTS idx_listing_drafts_platform ON listing_drafts(platform);
    """); conn.commit()
def fetch_trends(conn):
    return conn.execute("SELECT id, term, COALESCE(hit_score,0) AS hit_score FROM trends WHERE action_level='DO_NOW' ORDER BY hit_score DESC LIMIT 50").fetchall()
def fetch_concepts(conn, trend_id):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='design_concepts'").fetchone(): return []
    return conn.execute("SELECT id, concept, style, COALESCE(score,0) AS score FROM design_concepts WHERE trend_id=? ORDER BY score DESC, id ASC LIMIT 5", (trend_id,)).fetchall()
def fetch_skus(conn, trend_id):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sku_packs'").fetchone(): return []
    return conn.execute("SELECT id, product_type, title_seed, tags_json, COALESCE(score,0) AS score FROM sku_packs WHERE trend_id=? ORDER BY score DESC, id ASC LIMIT 10", (trend_id,)).fetchall()
def build_listing(term, concept, product, tags):
    title = f"{concept} {product} gift".strip()[:180]
    bullets = [
        f"Trending POD concept based on {term}",
        f"Designed for {product} buyers and gift shoppers",
        "Print-ready style direction for fast seller execution",
        "Optimized for trend-driven POD listing workflow",
        "Suitable for rapid marketplace validation",
    ]
    description = f"This {product} listing draft is generated from the trend '{term}'. It uses the concept '{concept}' and helps POD sellers move from trend to listing faster."
    return title, bullets, description, tags
def main():
    conn = connect(); ensure_schema(conn); trends = fetch_trends(conn); inserted = 0
    for tr in trends:
        trend_id, term = int(tr["id"]), str(tr["term"]).strip()
        concepts = fetch_concepts(conn, trend_id); skus = fetch_skus(conn, trend_id)
        conn.execute("DELETE FROM listing_drafts WHERE trend_id=? AND platform=?", (trend_id, PLATFORM))
        count = 0
        for c in concepts:
            for s in skus:
                if count >= LISTINGS_PER_TREND: break
                try: tags = json.loads(s["tags_json"] or "[]")
                except Exception: tags = []
                title, bullets, description, tags_out = build_listing(term, str(c["concept"]), str(s["product_type"]), tags)
                conn.execute("""INSERT INTO listing_drafts(trend_id, concept_id, sku_pack_id, platform, title, bullets_json, description, tags_json, score, payload_json, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             (trend_id, int(c["id"]), int(s["id"]), PLATFORM, title, json.dumps(bullets, ensure_ascii=False),
                              description, json.dumps(tags_out, ensure_ascii=False), float(c["score"])+float(s["score"]),
                              json.dumps({"term": term, "concept": str(c["concept"]), "product_type": str(s["product_type"])}, ensure_ascii=False), utc_now_iso()))
                inserted += 1; count += 1
    conn.commit(); print(f"[OK] listing_generator inserted={inserted} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
