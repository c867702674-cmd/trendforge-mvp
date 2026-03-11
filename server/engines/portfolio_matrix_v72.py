#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "executive_grid_v71"
TABLE_OUT = "portfolio_matrix_v72"

def pick_matrix_lane(exec_lane: str, priority_tier: str, product_type: str) -> str:
    if exec_lane == "EXECUTE_BOARD" and priority_tier == "P0":
        return "CORE_RELEASE_MATRIX"
    if exec_lane == "CREATIVE_BOARD":
        return "CREATIVE_MATRIX"
    if product_type == "poster":
        return "POSTER_MATRIX"
    if exec_lane == "RESERVE_BOARD":
        return "RESERVE_MATRIX"
    return "MANUAL_MATRIX"

def pick_matrix_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "CORE_RELEASE_MATRIX":
        return f"Place {product_type} into the core release matrix for immediate publish after final manual review."
    if lane == "CREATIVE_MATRIX":
        return f"Keep {product_type} inside the creative matrix until assets are finished, then return to release flow."
    if lane == "POSTER_MATRIX":
        return f"Manage poster items in a reusable matrix lane for template efficiency. Risk={risk_level}."
    if lane == "RESERVE_MATRIX":
        return f"Hold in reserve matrix until capacity and timing improve. Risk={risk_level}."
    return f"Route into manual matrix for operator decision. Risk={risk_level}."

def calc_matrix_score(exec_score: float, lane: str, priority_tier: str) -> float:
    score = float(exec_score or 0)
    if lane == "CORE_RELEASE_MATRIX":
        score += 10
    elif lane == "CREATIVE_MATRIX":
        score += 6
    elif lane == "POSTER_MATRIX":
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
            exec_lane,
            exec_score
        FROM {TABLE_IN}
        ORDER BY exec_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_matrix_lane(row["exec_lane"], row["priority_tier"], row["product_type"])
        action = pick_matrix_action(lane, row["product_type"], row["risk_level"])
        score = calc_matrix_score(row["exec_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                exec_lane,
                exec_score,
                matrix_lane,
                matrix_action,
                matrix_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["strategic_hub_id"],
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
            row["exec_lane"],
            row["exec_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] portfolio_matrix_v72 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
