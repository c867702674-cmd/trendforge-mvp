#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn

def ensure_schema(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS listing_quality_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      listing_id INTEGER NOT NULL,
      score REAL DEFAULT 0,
      quality_json TEXT,
      created_at TEXT
    );""")
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts);").fetchall()]
    if "quality_json" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN quality_json TEXT;")
    if "rank_score" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN rank_score REAL DEFAULT 0;")
    conn.commit()

def score_title(title):
    t = (title or "").strip(); score = 0.0; n = len(t); tl = t.lower()
    if 40 <= n <= 140: score += 30
    elif 20 <= n < 40: score += 15
    elif n > 140: score += 10
    for kw in ["gift","shirt","hoodie","sticker","mug","poster","retro","vintage","minimalist","funny","cute"]:
        if kw in tl: score += 6
    return score

def score_bullets(bullets):
    if not isinstance(bullets, list): return 0.0
    score = min(len(bullets), 5) * 8.0
    for b in bullets[:5]:
        if len(str(b).strip()) >= 25: score += 2.0
    return score

def score_tags(tags):
    if not isinstance(tags, list): return 0.0
    return min(len(tags), 12) * 2.5

def upgrade_description(description, term, product):
    desc = (description or "").strip()
    if len(desc) < 120:
        desc = (
            f"This {product} listing is generated from the trend '{term}'. "
            f"It is designed for POD sellers who want to move quickly from trend discovery to publish-ready execution. "
            f"Use this draft as a starting point for stronger niche positioning and faster marketplace testing."
        )
    return desc

def main():
    conn = connect(); ensure_schema(conn)
    rows = conn.execute("SELECT id, title, bullets_json, description, tags_json, payload_json FROM listing_drafts ORDER BY id ASC").fetchall()
    updated = 0
    for r in rows:
        try: bullets = json.loads(r["bullets_json"] or "[]")
        except Exception: bullets = []
        try: tags = json.loads(r["tags_json"] or "[]")
        except Exception: tags = []
        try: payload = json.loads(r["payload_json"] or "{}")
        except Exception: payload = {}
        term = str(payload.get("term") or "")
        product = str(payload.get("product_type") or "product")
        title = str(r["title"] or "")
        description = upgrade_description(str(r["description"] or ""), term, product)
        title_score = score_title(title); bullet_score = score_bullets(bullets); tag_score = score_tags(tags); total = title_score + bullet_score + tag_score
        qj = {"title_score": title_score, "bullet_score": bullet_score, "tag_score": tag_score, "total_score": total}
        conn.execute("UPDATE listing_drafts SET description=?, quality_json=?, rank_score=? WHERE id=?",
                     (description, json.dumps(qj, ensure_ascii=False), float(total), int(r["id"])))
        conn.execute("INSERT INTO listing_quality_logs(listing_id, score, quality_json, created_at) VALUES (?, ?, ?, ?)",
                     (int(r["id"]), float(total), json.dumps(qj, ensure_ascii=False), utc_now_iso()))
        updated += 1
    conn.commit(); print(f"[OK] listing_quality_engine updated={updated} db={DB_PATH}"); conn.close()

if __name__ == "__main__": main()
