#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "launch_queue_v61"
TABLE_OUT = "publish_board_v62"

def pick_board_column(priority_tier: str, schedule_bucket: str, risk_level: str) -> str:
    if priority_tier == "P0" and schedule_bucket == "DO_NOW" and risk_level == "SAFE":
        return "READY_TO_PUBLISH"
    if priority_tier in ("P0", "P1"):
        return "ARTWORK_PENDING"
    return "REVIEW_QUEUE"

def make_publish_status(board_column: str) -> str:
    if board_column == "READY_TO_PUBLISH":
        return "READY"
    if board_column == "ARTWORK_PENDING":
        return "WAIT_ART"
    return "REVIEW"

def calc_board_rank(pack_score: float, priority_tier: str, risk_level: str) -> float:
    score = float(pack_score or 0)
    if priority_tier == "P0":
        score += 20
    elif priority_tier == "P1":
        score += 10
    if risk_level == "SAFE":
        score += 8
    return round(score, 2)

def make_publish_note(priority_tier: str, schedule_bucket: str, board_column: str) -> str:
    return f"Priority={priority_tier} | Window={schedule_bucket} | Board={board_column}"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            id,
            execution_pack_id,
            listing_id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            sku_code,
            pack_score,
            priority_tier,
            schedule_bucket,
            publish_status
        FROM {TABLE_IN}
        ORDER BY
            CASE priority_tier WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END,
            pack_score DESC,
            id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        board_column = pick_board_column(row["priority_tier"], row["schedule_bucket"], row["risk_level"])
        publish_status = make_publish_status(board_column)
        board_rank = calc_board_rank(row["pack_score"], row["priority_tier"], row["risk_level"])
        publish_note = make_publish_note(row["priority_tier"], row["schedule_bucket"], board_column)

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                publish_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
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
            publish_status,
            board_column,
            board_rank,
            publish_note,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] publish_board_v62 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
