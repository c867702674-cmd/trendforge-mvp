#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "strategic_hub_v70"
TABLE_OUT = "executive_grid_v71"

def pick_exec_lane(hub_lane: str, priority_tier: str, product_type: str) -> str:
    if hub_lane == "LIVE_PRIORITY_HUB" and priority_tier == "P0":
        return "EXECUTE_BOARD"
    if hub_lane == "CREATIVE_HUB":
        return "CREATIVE_BOARD"
    if product_type == "poster":
        return "POSTER_BOARD"
    if hub_lane == "RESERVE_HUB":
        return "RESERVE_BOARD"
    return "MANUAL_BOARD"

def pick_exec_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "EXECUTE_BOARD":
        return f"Approve and execute {product_type} release from executive board after final manual review."
    if lane == "CREATIVE_BOARD":
        return f"Keep {product_type} in creative board until assets are completed, then return to execute queue."
    if lane == "POSTER_BOARD":
        return f"Run poster line through board-level reusable template workflow. Risk={risk_level}."
    if lane == "RESERVE_BOARD":
        return f"Hold in reserve board until release capacity becomes available. Risk={risk_level}."
    return f"Keep in manual board for operator judgment. Risk={risk_level}."

def calc_exec_score(hub_score: float, lane: str, priority_tier: str) -> float:
    score = float(hub_score or 0)
    if lane == "EXECUTE_BOARD":
        score += 10
    elif lane == "CREATIVE_BOARD":
        score += 6
    elif lane == "POSTER_BOARD":
        score += 4
    if priority_tier == "P0":
        score += 4
    return round(score, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            id,
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
            hub_lane,
            hub_score
        FROM {TABLE_IN}
        ORDER BY hub_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_exec_lane(row["hub_lane"], row["priority_tier"], row["product_type"])
        action = pick_exec_action(lane, row["product_type"], row["risk_level"])
        score = calc_exec_score(row["hub_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                hub_lane,
                hub_score,
                exec_lane,
                exec_action,
                exec_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["operations_hq_id"],
            row["war_room_id"],
            row["control_tower_id"],
            row["mission_planner_id"],
            row["batch_studio_id"],
            row["command_center_id"],
            row["ops_dashboard_id"],
            row["publish_board_id"],
            row["launch_queue_id"],
            row["execution_pack_id"],
            row["listing_id"],
            row["source_term"],
            row["safe_term"],
            row["risk_level"],
            row["product_type"],
            row["title_en"],
            row["sku_code"],
            row["priority_tier"],
            row["hub_lane"],
            row["hub_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] executive_grid_v71 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
