#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "mission_planner_v66"
TABLE_OUT = "control_tower_v67"

def pick_tower_lane(mission_lane: str, priority_tier: str, product_type: str) -> str:
    if mission_lane == "TODAY_LAUNCH" and priority_tier == "P0":
        return "LAUNCH_TOWER"
    if mission_lane == "ART_SPRINT":
        return "ART_TOWER"
    if product_type == "poster":
        return "POSTER_TOWER"
    if mission_lane == "BACKLOG_PIPE":
        return "BACKLOG_TOWER"
    return "MANUAL_TOWER"

def pick_tower_action(lane: str, product_type: str, risk_level: str) -> str:
    if lane == "LAUNCH_TOWER":
        return f"Send {product_type} into launch tower for same-day publish after final manual review."
    if lane == "ART_TOWER":
        return f"Coordinate artwork completion for {product_type}, then return to launch sequence."
    if lane == "POSTER_TOWER":
        return f"Coordinate poster program with shared layouts and reusable asset workflow. Risk={risk_level}."
    if lane == "BACKLOG_TOWER":
        return f"Monitor backlog timing and re-open when capacity is available. Risk={risk_level}."
    return f"Keep under manual tower supervision for operator decision. Risk={risk_level}."

def calc_tower_score(mission_score: float, lane: str, priority_tier: str) -> float:
    score = float(mission_score or 0)
    if lane == "LAUNCH_TOWER":
        score += 10
    elif lane == "ART_TOWER":
        score += 6
    elif lane == "POSTER_TOWER":
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
            mission_lane,
            mission_score
        FROM {TABLE_IN}
        ORDER BY mission_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_tower_lane(row["mission_lane"], row["priority_tier"], row["product_type"])
        action = pick_tower_action(lane, row["product_type"], row["risk_level"])
        score = calc_tower_score(row["mission_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                mission_lane,
                mission_score,
                tower_lane,
                tower_action,
                tower_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["mission_lane"],
            row["mission_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] control_tower_v67 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
