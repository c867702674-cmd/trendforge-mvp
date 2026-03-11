#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "portfolio_matrix_v72"
TABLE_OUT = "allocation_board_v73"

def pick_allocation_lane(matrix_lane: str, priority_tier: str, product_type: str) -> str:
    if matrix_lane == "CORE_RELEASE_MATRIX" and priority_tier == "P0":
        return "PRIMARY_ALLOCATION"
    if matrix_lane == "CREATIVE_MATRIX":
        return "CREATIVE_ALLOCATION"
    if product_type == "poster":
        return "POSTER_ALLOCATION"
    if matrix_lane == "RESERVE_MATRIX":
        return "RESERVE_ALLOCATION"
    return "MANUAL_ALLOCATION"

def pick_allocation_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "PRIMARY_ALLOCATION":
        return f"Allocate {product_type} into the primary release slot after final manual compliance review."
    if lane == "CREATIVE_ALLOCATION":
        return f"Allocate {product_type} to creative completion, then return it to release allocation."
    if lane == "POSTER_ALLOCATION":
        return f"Allocate poster items into reusable template production flow. Risk={risk_level}."
    if lane == "RESERVE_ALLOCATION":
        return f"Allocate to reserve pool until timing and capacity improve. Risk={risk_level}."
    return f"Allocate to manual review pool for operator judgment. Risk={risk_level}."

def calc_allocation_score(matrix_score: float, lane: str, priority_tier: str) -> float:
    score = float(matrix_score or 0)
    if lane == "PRIMARY_ALLOCATION":
        score += 10
    elif lane == "CREATIVE_ALLOCATION":
        score += 6
    elif lane == "POSTER_ALLOCATION":
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
            matrix_score
        FROM {TABLE_IN}
        ORDER BY matrix_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_allocation_lane(row["matrix_lane"], row["priority_tier"], row["product_type"])
        action = pick_allocation_action(lane, row["product_type"], row["risk_level"])
        score = calc_allocation_score(row["matrix_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                allocation_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["executive_grid_id"],
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
            row["matrix_lane"],
            row["matrix_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] allocation_board_v73 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
