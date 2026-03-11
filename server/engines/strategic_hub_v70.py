#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "operations_hq_v69"
TABLE_OUT = "strategic_hub_v70"

def pick_hub_lane(hq_lane: str, priority_tier: str, product_type: str) -> str:
    if hq_lane == "GO_LIVE_HQ" and priority_tier == "P0":
        return "LIVE_PRIORITY_HUB"
    if hq_lane == "ART_HQ":
        return "CREATIVE_HUB"
    if product_type == "poster":
        return "POSTER_HUB"
    if hq_lane == "RESERVE_HQ":
        return "RESERVE_HUB"
    return "MANUAL_HUB"

def pick_hub_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "LIVE_PRIORITY_HUB":
        return f"Prioritize {product_type} for live release from the hub after final manual review."
    if lane == "CREATIVE_HUB":
        return f"Route {product_type} through creative hub completion, then send back to live queue."
    if lane == "POSTER_HUB":
        return f"Manage poster candidates as a reusable template stream. Risk={risk_level}."
    if lane == "RESERVE_HUB":
        return f"Keep in reserve hub until release capacity opens. Risk={risk_level}."
    return f"Hold in manual hub for operator decision. Risk={risk_level}."

def calc_hub_score(hq_score: float, lane: str, priority_tier: str) -> float:
    score = float(hq_score or 0)
    if lane == "LIVE_PRIORITY_HUB":
        score += 10
    elif lane == "CREATIVE_HUB":
        score += 6
    elif lane == "POSTER_HUB":
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
            hq_lane,
            hq_score
        FROM {TABLE_IN}
        ORDER BY hq_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_hub_lane(row["hq_lane"], row["priority_tier"], row["product_type"])
        action = pick_hub_action(lane, row["product_type"], row["risk_level"])
        score = calc_hub_score(row["hq_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                hq_lane,
                hq_score,
                hub_lane,
                hub_action,
                hub_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["hq_lane"],
            row["hq_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] strategic_hub_v70 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
