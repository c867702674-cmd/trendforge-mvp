#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "mj_prompt_v81.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT id, listing_ai_id, saas_dashboard_id, release_command_id, product_type, priority_tier,
               risk_level, safe_term, title_en, sku_code, design_style, mj_prompt,
               negative_prompt, mockup_prompt, prompt_score, created_at
        FROM mj_prompt_v81
        ORDER BY prompt_score DESC, id DESC
    ''').fetchall()

    items = []
    by_product = Counter()
    by_priority = Counter()

    for r in rows:
        by_product[r["product_type"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v81",
        "module": "mj_prompt",
        "summary": {
            "total": len(items),
            "by_product_type": dict(by_product),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] mj_prompt_v81_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
