#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "batch_studio_v65.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            command_center_id,
            ops_dashboard_id,
            publish_board_id,
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
            commander_lane,
            command_score,
            batch_group,
            batch_action,
            batch_score,
            created_at
        FROM batch_studio_v65
        ORDER BY batch_score DESC, id DESC
    """).fetchall()

    items = []
    by_group = Counter()
    by_product = Counter()
    by_priority = Counter()

    for r in rows:
        by_group[r["batch_group"]] += 1
        by_product[r["product_type"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append({
            "id": r["id"],
            "command_center_id": r["command_center_id"],
            "ops_dashboard_id": r["ops_dashboard_id"],
            "publish_board_id": r["publish_board_id"],
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
            "commander_lane": r["commander_lane"],
            "command_score": r["command_score"],
            "batch_group": r["batch_group"],
            "batch_action": r["batch_action"],
            "batch_score": r["batch_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v65",
        "module": "batch_studio",
        "summary": {
            "total": len(items),
            "by_batch_group": dict(by_group),
            "by_product_type": dict(by_product),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] batch_studio_v65_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
