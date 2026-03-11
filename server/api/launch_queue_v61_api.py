#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "launch_queue_v61.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            execution_pack_id,
            listing_id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            sku_code,
            pack_score,
            priority_tier,
            schedule_bucket,
            publish_status,
            checklist_text,
            operator_note,
            created_at
        FROM launch_queue_v61
        ORDER BY
            CASE priority_tier WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END,
            pack_score DESC,
            id DESC
    """).fetchall()

    items = []
    by_priority = Counter()
    by_bucket = Counter()
    by_product = Counter()

    for r in rows:
        by_priority[r["priority_tier"]] += 1
        by_bucket[r["schedule_bucket"]] += 1
        by_product[r["product_type"]] += 1
        items.append({
            "id": r["id"],
            "execution_pack_id": r["execution_pack_id"],
            "listing_id": r["listing_id"],
            "source_term": r["source_term"],
            "safe_term": r["safe_term"],
            "risk_level": r["risk_level"],
            "product_type": r["product_type"],
            "title_en": r["title_en"],
            "sku_code": r["sku_code"],
            "pack_score": r["pack_score"],
            "priority_tier": r["priority_tier"],
            "schedule_bucket": r["schedule_bucket"],
            "publish_status": r["publish_status"],
            "checklist_text": r["checklist_text"],
            "operator_note": r["operator_note"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v61",
        "module": "launch_queue",
        "summary": {
            "total": len(items),
            "by_priority": dict(by_priority),
            "by_schedule_bucket": dict(by_bucket),
            "by_product_type": dict(by_product),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] launch_queue_v61_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
