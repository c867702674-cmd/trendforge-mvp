
#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/listing_auto_generator_api.json"

def utc():
    return datetime.now(timezone.utc).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT term, listing_title, bullet_points_json, description, seo_tags_json, image_prompt, draft_score
        FROM listing_auto_drafts
        ORDER BY draft_score DESC
        LIMIT 50
    """).fetchall()

    items = []
    for r in rows:
        item = dict(r)
        try:
            item["bullet_points_json"] = json.loads(item["bullet_points_json"] or "[]")
        except Exception:
            item["bullet_points_json"] = []
        try:
            item["seo_tags_json"] = json.loads(item["seo_tags_json"] or "[]")
        except Exception:
            item["seo_tags_json"] = []
        items.append(item)

    data = {
        "generated_at": utc(),
        "items": items
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] listing_auto_generator_api wrote={OUTPUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
