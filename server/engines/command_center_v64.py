#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "ops_dashboard_v63"
TABLE_OUT = "command_center_v64"

def pick_lane(ops_stage: str, priority_tier: str, product_type: str) -> str:
    if ops_stage == "QUEUE_NOW" and priority_tier == "P0":
        return "EXECUTE_FIRST"
    if ops_stage == "MAKE_ART":
        return "ART_FACTORY"
    if product_type == "poster":
        return "POSTER_LAB"
    return "REVIEW_HOLD"

def pick_action(lane: str, risk_level: str, product_type: str) -> str:
    if lane == "EXECUTE_FIRST":
        return f"Push {product_type} to publish now; keep final manual trademark review."
    if lane == "ART_FACTORY":
        return f"Generate art assets for {product_type}, then return to publish board."
    if lane == "POSTER_LAB":
        return f"Bundle poster candidates for artwork batching and template reuse. Risk={risk_level}."
    return f"Hold for manual review and secondary prioritization. Risk={risk_level}."

def calc_score(dashboard_score: float, lane: str, priority_tier: str) -> float:
    score = float(dashboard_score or 0)
    if lane == "EXECUTE_FIRST":
        score += 12
    elif lane == "ART_FACTORY":
        score += 6
    elif lane == "POSTER_LAB":
        score += 4
    if priority_tier == "P0":
        score += 6
    return round(score, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            id,
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
            schedule_bucket,
            publish_status,
            board_column,
            ops_stage,
            dashboard_score
        FROM {TABLE_IN}
        ORDER BY dashboard_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_lane(row["ops_stage"], row["priority_tier"], row["product_type"])
        action = pick_action(lane, row["risk_level"], row["product_type"])
        score = calc_score(row["dashboard_score"], lane, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                schedule_bucket,
                publish_status,
                board_column,
                ops_stage,
                dashboard_score,
                commander_lane,
                commander_action,
                command_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["schedule_bucket"],
            row["publish_status"],
            row["board_column"],
            row["ops_stage"],
            row["dashboard_score"],
            lane,
            action,
            score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] command_center_v64 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
