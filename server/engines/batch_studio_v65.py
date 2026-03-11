#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "command_center_v64"
TABLE_OUT = "batch_studio_v65"

def pick_batch_group(commander_lane: str, product_type: str, priority_tier: str) -> str:
    if commander_lane == "EXECUTE_FIRST":
        return "FAST_PUBLISH_BATCH"
    if commander_lane == "ART_FACTORY":
        return "ART_BATCH"
    if product_type == "poster":
        return "POSTER_BATCH"
    if priority_tier == "P2":
        return "BACKLOG_BATCH"
    return "MANUAL_BATCH"

def pick_batch_action(batch_group: str, product_type: str, risk_level: str) -> str:
    if batch_group == "FAST_PUBLISH_BATCH":
        return f"Publish {product_type} in rapid sequence after final manual compliance check."
    if batch_group == "ART_BATCH":
        return f"Produce artwork assets for {product_type} in one batch, then push back to publish queue."
    if batch_group == "POSTER_BATCH":
        return f"Group poster items for shared layout/template reuse. Risk={risk_level}."
    if batch_group == "BACKLOG_BATCH":
        return f"Store for low-priority processing window. Risk={risk_level}."
    return f"Hold in manual batch for operator review. Risk={risk_level}."

def calc_batch_score(command_score: float, batch_group: str, priority_tier: str) -> float:
    score = float(command_score or 0)
    if batch_group == "FAST_PUBLISH_BATCH":
        score += 10
    elif batch_group == "ART_BATCH":
        score += 6
    elif batch_group == "POSTER_BATCH":
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
            commander_lane,
            command_score
        FROM {TABLE_IN}
        ORDER BY command_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        batch_group = pick_batch_group(row["commander_lane"], row["product_type"], row["priority_tier"])
        batch_action = pick_batch_action(batch_group, row["product_type"], row["risk_level"])
        batch_score = calc_batch_score(row["command_score"], batch_group, row["priority_tier"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                commander_lane,
                command_score,
                batch_group,
                batch_action,
                batch_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["commander_lane"],
            row["command_score"],
            batch_group,
            batch_action,
            batch_score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] batch_studio_v65 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
