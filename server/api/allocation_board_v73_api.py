#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "allocation_board_v73.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            portfolio_matrix_id,
            executive_grid_id,
            strategic_hub_id,
            operations_hq_id,
            war_room_id,
            control_tower_id,
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
            matrix_lane,
            matrix_score,
            allocation_lane,
            allocation_action,
            allocation_score,
            created_at
        FROM allocation_board_v73
        ORDER BY allocation_score DESC, id DESC
    """).fetchall()

    items = []
    by_lane = Counter()
    by_product = Counter()
    by_priority = Counter()

    for r in rows:
        by_lane[r["allocation_lane"]] += 1
        by_product[r["product_type"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append({
            "id": r["id"],
            "portfolio_matrix_id": r["portfolio_matrix_id"],
            "executive_grid_id": r["executive_grid_id"],
            "strategic_hub_id": r["strategic_hub_id"],
            "operations_hq_id": r["operations_hq_id"],
            "war_room_id": r["war_room_id"],
            "control_tower_id": r["control_tower_id"],
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
            "matrix_lane": r["matrix_lane"],
            "matrix_score": r["matrix_score"],
            "allocation_lane": r["allocation_lane"],
            "allocation_action": r["allocation_action"],
            "allocation_score": r["allocation_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v73",
        "module": "allocation_board",
        "summary": {
            "total": len(items),
            "by_allocation_lane": dict(by_lane),
            "by_product_type": dict(by_product),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] allocation_board_v73_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
