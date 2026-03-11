#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/opportunity_cards_v33.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, card_title, card_subtitle, opportunity_score, design_direction,
               recommended_products_json, recommended_title, image_prompt
        FROM opportunity_cards
        ORDER BY opportunity_score DESC, id ASC
        LIMIT 50
        """
    ).fetchall()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["recommended_products_json"] = json.loads(d["recommended_products_json"] or "[]")
        except Exception:
            d["recommended_products_json"] = []
        items.append(d)

    data = {"items": items, "count": len(items)}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] opportunity_cards_v33_api wrote={OUTPUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
