#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_columns(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts)").fetchall()]
    for col, ddl in [
        ("amazon_title_ai", "ALTER TABLE listing_drafts ADD COLUMN amazon_title_ai TEXT"),
        ("amazon_bullets_ai_json", "ALTER TABLE listing_drafts ADD COLUMN amazon_bullets_ai_json TEXT"),
        ("amazon_description_ai", "ALTER TABLE listing_drafts ADD COLUMN amazon_description_ai TEXT"),
    ]:
        if col not in cols:
            conn.execute(ddl)
    conn.commit()
def bullets(term, title):
    return [
        f"AI-enhanced Amazon angle built around trend '{term}'.",
        f"Optimized to improve click-through for title '{title[:80]}'.",
        "Structured for POD testing across shirts, hoodies, mugs, and posters.",
        "Highlights buyer intent, niche fit, and fast-launch potential.",
        "Ready for seller review and platform-specific refinement.",
    ]
def main():
    conn = connect(); ensure_columns(conn)
    rows = conn.execute("""
        SELECT id, title, amazon_title, amazon_description, payload_json
        FROM listing_drafts
        ORDER BY id ASC
    """).fetchall()
    updated = 0
    for r in rows:
        try:
            payload = json.loads(r["payload_json"] or "{}")
        except Exception:
            payload = {}
        term = str(payload.get("term") or "")
        base_title = str(r["amazon_title"] or r["title"] or "")
        ai_title = f"{base_title} | Fast POD Trend Launch".strip()[:190]
        ai_bullets = bullets(term, ai_title)
        ai_desc = f"{str(r['amazon_description'] or '')} This AI-enhanced draft emphasizes niche relevance, quick POD execution, and stronger buyer-intent alignment.".strip()
        conn.execute("""UPDATE listing_drafts
                        SET amazon_title_ai=?, amazon_bullets_ai_json=?, amazon_description_ai=?
                        WHERE id=?""",
                     (ai_title, json.dumps(ai_bullets, ensure_ascii=False), ai_desc, int(r["id"])))
        updated += 1
    conn.commit()
    print(f"[OK] amazon_listing_ai_enhancer_v1 updated={updated} db={DB_PATH}")
    conn.close()
if __name__ == "__main__":
    main()
