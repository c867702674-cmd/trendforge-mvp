#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "release_routing_v74.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            allocation_board_id,
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
            allocation_lane,
            allocation_score,
            routing_lane,
            routing_action,
            routing_score,
            created_at
        FROM release_routing_v74
        ORDER BY routing_score DESC, id DESC
    """).fetchall()

    items = []
    by_lane = Counter()
    by_product = Counter()
    by_priority = Counter()

    for r in rows:
        by_lane[r["routing_lane"]] += 1
        by_product[r["product_type"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append({
            "id": r["id"],
            "allocation_board_id": r["allocation_board_id"],
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
            "allocation_lane": r["allocation_lane"],
            "allocation_score": r["allocation_score"],
            "routing_lane": r["routing_lane"],
            "routing_action": r["routing_action"],
            "routing_score": r["routing_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v74",
        "module": "release_routing",
        "summary": {
            "total": len(items),
            "by_routing_lane": dict(by_lane),
            "by_product_type": dict(by_product),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] release_routing_v74_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
