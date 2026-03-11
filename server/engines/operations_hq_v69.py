#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "war_room_v68"
TABLE_OUT = "operations_hq_v69"

def pick_hq_lane(war_lane: str, priority_tier: str, product_type: str) -> str:
    if war_lane == "DEPLOY_NOW" and priority_tier == "P0":
        return "GO_LIVE_HQ"
    if war_lane == "ART_COMMAND":
        return "ART_HQ"
    if product_type == "poster":
        return "POSTER_HQ"
    if war_lane == "RESERVE_QUEUE":
        return "RESERVE_HQ"
    return "MANUAL_HQ"

def pick_hq_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "GO_LIVE_HQ":
        return f"Push {product_type} live from HQ after final manual compliance review."
    if lane == "ART_HQ":
        return f"Coordinate artwork finish for {product_type} and return it to go-live flow."
    if lane == "POSTER_HQ":
        return f"Run poster pipeline from HQ with reusable layout assets. Risk={risk_level}."
    if lane == "RESERVE_HQ":
        return f"Keep in reserve HQ until capacity and timing align. Risk={risk_level}."
    return f"Keep in manual HQ for operator decision. Risk={risk_level}."

def calc_hq_score(war_score: float, lane: str, priority_tier: str) -> float:
    score = float(war_score or 0)
    if lane == "GO_LIVE_HQ":
        score += 10
    elif lane == "ART_HQ":
        score += 6
    elif lane == "POSTER_HQ":
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
            war_lane,
            war_score
        FROM {TABLE_IN}
        ORDER BY war_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_hq_lane(row["war_lane"], row["priority_tier"], row["product_type"])
        action = pick_hq_action(lane, row["product_type"], row["risk_level"])
        score = calc_hq_score(row["war_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                war_lane,
                war_score,
                hq_lane,
                hq_action,
                hq_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["war_lane"],
            row["war_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] operations_hq_v69 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
