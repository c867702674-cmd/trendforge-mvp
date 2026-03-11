#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "execution_packs_v60"
TABLE_OUT = "launch_queue_v61"

def make_priority(pack_score: float, risk_level: str, product_type: str) -> str:
    score = float(pack_score or 0)
    if risk_level == "SAFE" and score >= 100 and product_type in ("shirt", "mug", "hoodie"):
        return "P0"
    if score >= 90:
        return "P1"
    return "P2"

def make_bucket(priority_tier: str, risk_level: str) -> str:
    if priority_tier == "P0" and risk_level == "SAFE":
        return "DO_NOW"
    if priority_tier in ("P0", "P1"):
        return "TODAY"
    return "THIS_WEEK"

def make_checklist(row) -> str:
    return (
        "1. Check marketplace trademark manually\n"
        "2. Confirm title length and keyword readability\n"
        "3. Review tags for duplication and platform policy\n"
        "4. Generate artwork from design prompt\n"
        "5. Upload mockup and verify print area\n"
        "6. Final publish after manual compliance review"
    )

def make_note(priority_tier: str, bucket: str, risk_level: str) -> str:
    return f"Queue={priority_tier} | Window={bucket} | Risk={risk_level}"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            id,
            listing_id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            sku_code,
            pack_score
        FROM {TABLE_IN}
        ORDER BY pack_score DESC, id DESC
        LIMIT 120
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        priority_tier = make_priority(row["pack_score"], row["risk_level"], row["product_type"])
        schedule_bucket = make_bucket(priority_tier, row["risk_level"])
        checklist_text = make_checklist(row)
        operator_note = make_note(priority_tier, schedule_bucket, row["risk_level"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
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
                publish_status,
                checklist_text,
                operator_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
            row["listing_id"],
            row["source_term"],
            row["safe_term"],
            row["risk_level"],
            row["product_type"],
            row["title_en"],
            row["sku_code"],
            row["pack_score"],
            priority_tier,
            schedule_bucket,
            "READY",
            checklist_text,
            operator_note,
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] launch_queue_v61 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
