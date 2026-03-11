#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "control_tower_v67.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            mission_planner_id,
            batch_studio_id,
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
            mission_lane,
            mission_score,
            tower_lane,
            tower_action,
            tower_score,
            created_at
        FROM control_tower_v67
        ORDER BY tower_score DESC, id DESC
    """).fetchall()

    items = []
    by_lane = Counter()
    by_product = Counter()
    by_priority = Counter()

    for r in rows:
        by_lane[r["tower_lane"]] += 1
        by_product[r["product_type"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append({
            "id": r["id"],
            "mission_planner_id": r["mission_planner_id"],
            "batch_studio_id": r["batch_studio_id"],
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
            "mission_lane": r["mission_lane"],
            "mission_score": r["mission_score"],
            "tower_lane": r["tower_lane"],
            "tower_action": r["tower_action"],
            "tower_score": r["tower_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v67",
        "module": "control_tower",
        "summary": {
            "total": len(items),
            "by_tower_lane": dict(by_lane),
            "by_product_type": dict(by_product),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] control_tower_v67_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
