#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "allocation_board_v73"
TABLE_OUT = "release_routing_v74"

def pick_routing_lane(allocation_lane: str, priority_tier: str, product_type: str) -> str:
    if allocation_lane == "PRIMARY_ALLOCATION" and priority_tier == "P0":
        return "DIRECT_RELEASE_ROUTE"
    if allocation_lane == "CREATIVE_ALLOCATION":
        return "CREATIVE_ROUTE"
    if product_type == "poster":
        return "POSTER_ROUTE"
    if allocation_lane == "RESERVE_ALLOCATION":
        return "RESERVE_ROUTE"
    return "MANUAL_ROUTE"

def pick_routing_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "DIRECT_RELEASE_ROUTE":
        return f"Route {product_type} directly into release after final manual compliance review."
    if lane == "CREATIVE_ROUTE":
        return f"Route {product_type} through creative completion, then back into release path."
    if lane == "POSTER_ROUTE":
        return f"Route poster items through reusable poster workflow. Risk={risk_level}."
    if lane == "RESERVE_ROUTE":
        return f"Route to reserve pool until timing and capacity improve. Risk={risk_level}."
    return f"Route to manual queue for operator judgment. Risk={risk_level}."

def calc_routing_score(allocation_score: float, lane: str, priority_tier: str) -> float:
    score = float(allocation_score or 0)
    if lane == "DIRECT_RELEASE_ROUTE":
        score += 10
    elif lane == "CREATIVE_ROUTE":
        score += 6
    elif lane == "POSTER_ROUTE":
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
            allocation_score
        FROM {TABLE_IN}
        ORDER BY allocation_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_routing_lane(row["allocation_lane"], row["priority_tier"], row["product_type"])
        action = pick_routing_action(lane, row["product_type"], row["risk_level"])
        score = calc_routing_score(row["allocation_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                routing_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["allocation_lane"],
            row["allocation_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] release_routing_v74 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
