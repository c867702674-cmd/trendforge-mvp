#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "publish_board_v62.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            launch_queue_id,
            execution_pack_id,
            listing_id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            sku_code,
            priority_tier,
            schedule_bucket,
            publish_status,
            board_column,
            board_rank,
            publish_note,
            created_at
        FROM publish_board_v62
        ORDER BY
            CASE board_column
                WHEN 'READY_TO_PUBLISH' THEN 1
                WHEN 'ARTWORK_PENDING' THEN 2
                ELSE 3
            END,
            board_rank DESC,
            id DESC
    """).fetchall()

    items = []
    by_column = Counter()
    by_status = Counter()
    by_priority = Counter()

    for r in rows:
        by_column[r["board_column"]] += 1
        by_status[r["publish_status"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append({
            "id": r["id"],
            "launch_queue_id": r["launch_queue_id"],
            "execution_pack_id": r["execution_pack_id"],
            "listing_id": r["listing_id"],
            "source_term": r["source_term"],
            "safe_term": r["safe_term"],
            "risk_level": r["risk_level"],
            "product_type": r["product_type"],
            "title_en": r["title_en"],
            "sku_code": r["sku_code"],
            "priority_tier": r["priority_tier"],
            "schedule_bucket": r["schedule_bucket"],
            "publish_status": r["publish_status"],
            "board_column": r["board_column"],
            "board_rank": r["board_rank"],
            "publish_note": r["publish_note"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v62",
        "module": "publish_board",
        "summary": {
            "total": len(items),
            "by_board_column": dict(by_column),
            "by_publish_status": dict(by_status),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] publish_board_v62_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
