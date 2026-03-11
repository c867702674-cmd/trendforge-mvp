#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "control_tower_v67"
TABLE_OUT = "war_room_v68"

def pick_war_lane(tower_lane: str, priority_tier: str, product_type: str) -> str:
    if tower_lane == "LAUNCH_TOWER" and priority_tier == "P0":
        return "DEPLOY_NOW"
    if tower_lane == "ART_TOWER":
        return "ART_COMMAND"
    if product_type == "poster":
        return "POSTER_COMMAND"
    if tower_lane == "BACKLOG_TOWER":
        return "RESERVE_QUEUE"
    return "MANUAL_COMMAND"

def pick_war_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "DEPLOY_NOW":
        return f"Deploy {product_type} now after final manual compliance review."
    if lane == "ART_COMMAND":
        return f"Command artwork completion for {product_type}, then return to deploy flow."
    if lane == "POSTER_COMMAND":
        return f"Command poster asset workflow with reusable templates. Risk={risk_level}."
    if lane == "RESERVE_QUEUE":
        return f"Keep in reserve queue until capacity opens. Risk={risk_level}."
    return f"Hold in manual command queue for operator judgment. Risk={risk_level}."

def calc_war_score(tower_score: float, lane: str, priority_tier: str) -> float:
    score = float(tower_score or 0)
    if lane == "DEPLOY_NOW":
        score += 10
    elif lane == "ART_COMMAND":
        score += 6
    elif lane == "POSTER_COMMAND":
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
            tower_lane,
            tower_score
        FROM {TABLE_IN}
        ORDER BY tower_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_war_lane(row["tower_lane"], row["priority_tier"], row["product_type"])
        action = pick_war_action(lane, row["product_type"], row["risk_level"])
        score = calc_war_score(row["tower_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                tower_lane,
                tower_score,
                war_lane,
                war_action,
                war_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["tower_lane"],
            row["tower_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] war_room_v68 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
