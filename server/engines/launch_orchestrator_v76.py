#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "dispatch_center_v75"
TABLE_OUT = "launch_orchestrator_v76"

def pick_lane(dispatch_lane: str, priority_tier: str, product_type: str) -> str:
    if dispatch_lane == "FAST_DISPATCH" and priority_tier == "P0":
        return "ORCHESTRATE_NOW"
    if dispatch_lane == "CREATIVE_DISPATCH":
        return "CREATIVE_ORCHESTRATION"
    if product_type == "poster":
        return "POSTER_ORCHESTRATION"
    if dispatch_lane == "RESERVE_DISPATCH":
        return "RESERVE_ORCHESTRATION"
    return "MANUAL_ORCHESTRATION"

def pick_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "ORCHESTRATE_NOW":
        return f"Orchestrate immediate launch for {product_type} after final manual compliance review."
    if lane == "CREATIVE_ORCHESTRATION":
        return f"Orchestrate creative completion for {product_type}, then return it to launch flow."
    if lane == "POSTER_ORCHESTRATION":
        return f"Orchestrate poster production with reusable template flow. Risk={risk_level}."
    if lane == "RESERVE_ORCHESTRATION":
        return f"Orchestrate reserve holding until release timing improves. Risk={risk_level}."
    return f"Orchestrate via manual review path for operator judgment. Risk={risk_level}."

def calc_score(dispatch_score: float, lane: str, priority_tier: str) -> float:
    score = float(dispatch_score or 0)
    if lane == "ORCHESTRATE_NOW":
        score += 10
    elif lane == "CREATIVE_ORCHESTRATION":
        score += 6
    elif lane == "POSTER_ORCHESTRATION":
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
            release_routing_id,
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
            dispatch_lane,
            dispatch_score
        FROM {TABLE_IN}
        ORDER BY dispatch_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0
    for row in rows:
        lane = pick_lane(row["dispatch_lane"], row["priority_tier"], row["product_type"])
        action = pick_action(lane, row["product_type"], row["risk_level"])
        score = calc_score(row["dispatch_score"], lane, row["priority_tier"])
        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
                dispatch_center_id,
                release_routing_id,
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
                dispatch_lane,
                dispatch_score,
                orchestrator_lane,
                orchestrator_action,
                orchestrator_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["release_routing_id"],
            row["allocation_board_id"],
            row["portfolio_matrix_id"],
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
            row["dispatch_lane"],
            row["dispatch_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] launch_orchestrator_v76 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
