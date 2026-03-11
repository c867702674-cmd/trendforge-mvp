#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "publish_board_v62"
TABLE_OUT = "ops_dashboard_v63"

def pick_ops_stage(board_column: str, publish_status: str, priority_tier: str) -> str:
    if board_column == "READY_TO_PUBLISH" and publish_status == "READY":
        return "QUEUE_NOW"
    if board_column == "ARTWORK_PENDING":
        return "MAKE_ART"
    if priority_tier == "P2":
        return "BACKLOG_REVIEW"
    return "MANUAL_REVIEW"

def make_action_hint(stage: str, product_type: str, risk_level: str) -> str:
    if stage == "QUEUE_NOW":
        return f"Publish first for {product_type}; do final trademark/manual check before listing."
    if stage == "MAKE_ART":
        return f"Generate artwork for {product_type} using the approved prompt, then return to publish queue."
    if stage == "BACKLOG_REVIEW":
        return f"Keep in backlog; review when primary queue slows down. Risk={risk_level}."
    return f"Manual operator review needed before next step. Risk={risk_level}."

def calc_dashboard_score(board_rank: float, priority_tier: str, board_column: str) -> float:
    score = float(board_rank or 0)
    if priority_tier == "P0":
        score += 10
    elif priority_tier == "P1":
        score += 5
    if board_column == "READY_TO_PUBLISH":
        score += 8
    return round(score, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            id,
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
            board_rank
        FROM {TABLE_IN}
        ORDER BY
            CASE board_column
                WHEN 'READY_TO_PUBLISH' THEN 1
                WHEN 'ARTWORK_PENDING' THEN 2
                ELSE 3
            END,
            board_rank DESC,
            id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        ops_stage = pick_ops_stage(row["board_column"], row["publish_status"], row["priority_tier"])
        action_hint = make_action_hint(ops_stage, row["product_type"], row["risk_level"])
        dashboard_score = calc_dashboard_score(row["board_rank"], row["priority_tier"], row["board_column"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                board_rank,
                ops_stage,
                action_hint,
                dashboard_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            row["board_rank"],
            ops_stage,
            action_hint,
            dashboard_score,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] ops_dashboard_v63 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
