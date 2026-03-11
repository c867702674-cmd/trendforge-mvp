#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "execution_pack_v60.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            listing_id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            tags_en,
            bullets_en,
            description_en,
            design_prompt_en,
            sku_code,
            execution_pack_text,
            pack_score,
            created_at
        FROM execution_packs_v60
        ORDER BY pack_score DESC, id DESC
    """).fetchall()

    items = []
    product_counter = Counter()
    risk_counter = Counter()

    for r in rows:
        product_counter[r["product_type"]] += 1
        risk_counter[r["risk_level"]] += 1
        items.append({
            "id": r["id"],
            "listing_id": r["listing_id"],
            "source_term": r["source_term"],
            "safe_term": r["safe_term"],
            "risk_level": r["risk_level"],
            "product_type": r["product_type"],
            "title_en": r["title_en"],
            "tags_en": r["tags_en"],
            "bullets_en": r["bullets_en"],
            "description_en": r["description_en"],
            "design_prompt_en": r["design_prompt_en"],
            "sku_code": r["sku_code"],
            "execution_pack_text": r["execution_pack_text"],
            "pack_score": r["pack_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v60",
        "module": "execution_pack",
        "summary": {
            "total": len(items),
            "by_product_type": dict(product_counter),
            "by_risk_level": dict(risk_counter),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] execution_pack_v60_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
