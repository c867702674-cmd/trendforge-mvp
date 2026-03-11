#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT = "/root/trendforge-mvp/server/docs/ai_listing_v54.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, platform, title, bullet_1, bullet_2, bullet_3, bullet_4, bullet_5,
               description, tags_json, design_prompt
        FROM ai_listing_drafts
        ORDER BY id ASC
        LIMIT 100
        """
    ).fetchall()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["tags_json"] = json.loads(d["tags_json"] or "[]")
        except Exception:
            d["tags_json"] = []
        items.append(d)

    data = {"items": items, "count": len(items)}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] ai_listing_v54_api wrote={OUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
