#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "batch_studio_v65"
TABLE_OUT = "mission_planner_v66"

def pick_mission_lane(batch_group: str, priority_tier: str, product_type: str) -> str:
    if batch_group == "FAST_PUBLISH_BATCH" and priority_tier == "P0":
        return "TODAY_LAUNCH"
    if batch_group == "ART_BATCH":
        return "ART_SPRINT"
    if product_type == "poster":
        return "POSTER_PROGRAM"
    if batch_group == "BACKLOG_BATCH":
        return "BACKLOG_PIPE"
    return "MANUAL_DESK"

def pick_mission_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "TODAY_LAUNCH":
        return f"Launch {product_type} today after final manual trademark and policy review."
    if lane == "ART_SPRINT":
        return f"Finish artwork sprint for {product_type}, then hand back to launch flow."
    if lane == "POSTER_PROGRAM":
        return f"Process poster assets as a grouped program with reusable layouts. Risk={risk_level}."
    if lane == "BACKLOG_PIPE":
        return f"Keep in backlog pipe for later release window. Risk={risk_level}."
    return f"Route to manual desk for operator decision. Risk={risk_level}."

def calc_mission_score(batch_score: float, lane: str, priority_tier: str) -> float:
    score = float(batch_score or 0)
    if lane == "TODAY_LAUNCH":
        score += 10
    elif lane == "ART_SPRINT":
        score += 6
    elif lane == "POSTER_PROGRAM":
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
            batch_group,
            batch_score
        FROM {TABLE_IN}
        ORDER BY batch_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_mission_lane(row["batch_group"], row["priority_tier"], row["product_type"])
        action = pick_mission_action(lane, row["product_type"], row["risk_level"])
        score = calc_mission_score(row["batch_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                batch_group,
                batch_score,
                mission_lane,
                mission_action,
                mission_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["batch_group"],
            row["batch_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] mission_planner_v66 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
