#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/execution_pack_distribution_v36.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, pack_title, pack_score, task_list_json, listing_title, image_prompt
        FROM execution_pack_distributions
        ORDER BY pack_score DESC, id ASC
        LIMIT 50
        """
    ).fetchall()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["task_list_json"] = json.loads(d["task_list_json"] or "[]")
        except Exception:
            d["task_list_json"] = []
        items.append(d)

    data = {"items": items, "count": len(items)}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] execution_pack_distribution_v36_api wrote={OUTPUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
