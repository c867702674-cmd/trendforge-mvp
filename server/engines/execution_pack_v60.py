#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "listing_candidates_v59"
TABLE_OUT = "execution_packs_v60"

def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def make_execution_pack(row) -> str:
    return (
        f"SKU: {row['sku_code']}\n"
        f"Product: {row['product_type']}\n"
        f"Risk Level: {row['risk_level']}\n"
        f"Title: {row['title_en']}\n"
        f"Tags: {row['tags_en']}\n\n"
        f"Bullets:\n{row['bullets_en']}\n\n"
        f"Description:\n{row['description_en']}\n\n"
        f"Design Prompt:\n{row['design_prompt_en']}\n"
    )

def calc_pack_score(listing_score: float, risk_level: str, product_type: str) -> float:
    bonus = 0
    if product_type in ("shirt", "hoodie", "mug"):
        bonus += 5
    if risk_level == "SAFE":
        bonus += 8
    return round(float(listing_score or 0) + bonus, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            tags_en,
            bullets_en,
            description_en,
            design_prompt_en,
            sku_code,
            listing_score
        FROM {TABLE_IN}
        ORDER BY listing_score DESC, id DESC
        LIMIT 150
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        execution_pack_text = make_execution_pack(row)
        pack_score = calc_pack_score(row["listing_score"], row["risk_level"], row["product_type"])

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
                listing_id,
                source_term,
                safe_term,
                risk_level,
                product_type,
                title_en,
                tags_en,
                bullets_en,
                description_en,
                design_prompt_en,
                sku_code,
                execution_pack_text,
                pack_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["id"],
            clean_spaces(row["source_term"]),
            clean_spaces(row["safe_term"]),
            row["risk_level"],
            row["product_type"],
            row["title_en"],
            row["tags_en"],
            row["bullets_en"],
            row["description_en"],
            row["design_prompt_en"],
            row["sku_code"],
            execution_pack_text,
            pack_score,
        ))
        inserted += 1

    conn.commit()
    conn.close()

    print(f"[OK] execution_pack_v60 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
