#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "listing_v59.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            source_term,
            candidate_term,
            safe_term,
            risk_level,
            product_type,
            style_hint,
            audience_hint,
            title_en,
            tags_en,
            bullets_en,
            description_en,
            design_prompt_en,
            sku_code,
            listing_score,
            created_at
        FROM listing_candidates_v59
        ORDER BY listing_score DESC, id DESC
    """).fetchall()

    items = []
    product_counter = Counter()

    for r in rows:
        product_counter[r["product_type"]] += 1
        items.append({
            "id": r["id"],
            "source_term": r["source_term"],
            "candidate_term": r["candidate_term"],
            "safe_term": r["safe_term"],
            "risk_level": r["risk_level"],
            "product_type": r["product_type"],
            "style_hint": r["style_hint"],
            "audience_hint": r["audience_hint"],
            "title_en": r["title_en"],
            "tags_en": r["tags_en"],
            "bullets_en": r["bullets_en"],
            "description_en": r["description_en"],
            "design_prompt_en": r["design_prompt_en"],
            "sku_code": r["sku_code"],
            "listing_score": r["listing_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v59",
        "module": "listing_generator",
        "summary": {
            "total": len(items),
            "by_product_type": dict(product_counter)
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] listing_v59_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
