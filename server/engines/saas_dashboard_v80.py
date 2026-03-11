#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "listing_ai_v79"
TABLE_OUT = "saas_dashboard_v80"

def pick_lane(priority_tier, risk_level, product_type):
    if priority_tier == "P0" and risk_level == "SAFE":
        return "DO_NOW"
    if risk_level == "SAFE":
        return "READY_PACK"
    if risk_level == "REVIEW":
        return "REVIEW_QUEUE"
    if product_type == "poster":
        return "POSTER_LAB"
    return "MANUAL_DESK"

def calc_score(priority_tier, risk_level, product_type):
    score = 70
    if priority_tier == "P0":
        score += 15
    elif priority_tier == "P1":
        score += 8
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 3
    if product_type == "poster":
        score -= 2
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, release_command_id, product_type, priority_tier, risk_level, safe_term,
               title_en, sku_code, tags_text, description_text, design_prompt, mockup_prompt
        FROM {TABLE_IN}
        ORDER BY listing_score DESC, id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0
    for row in rows:
        lane = pick_lane(row["priority_tier"], row["risk_level"], row["product_type"])
        score = calc_score(row["priority_tier"], row["risk_level"], row["product_type"])
        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                listing_ai_id, release_command_id, product_type, priority_tier, risk_level,
                safe_term, title_en, sku_code, tags_text, description_text, design_prompt,
                mockup_prompt, dashboard_lane, dashboard_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["release_command_id"], row["product_type"], row["priority_tier"],
            row["risk_level"], row["safe_term"], row["title_en"], row["sku_code"],
            row["tags_text"], row["description_text"], row["design_prompt"],
            row["mockup_prompt"], lane, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] saas_dashboard_v80 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
