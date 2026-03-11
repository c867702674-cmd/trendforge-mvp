#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3
BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "launch_ops_v86"
TABLE_OUT = "command_center_v87"
def pick_lane(ops_lane: str, ops_status: str, product_type: str) -> str:
    if ops_lane == "PUSH_NOW" and ops_status == "READY":
        return "LAUNCH_CENTER"
    if ops_lane == "ASSET_TODO":
        return "ASSET_CENTER"
    if ops_lane == "COMPLIANCE_TODO":
        return "COMPLIANCE_CENTER"
    if ops_lane == "POSTER_TODO" or product_type == "poster":
        return "POSTER_CENTER"
    return "MANUAL_CENTER"
def pick_module(lane: str) -> str:
    mapping = {
        "LAUNCH_CENTER": "Commercial Publish",
        "ASSET_CENTER": "Creative Asset",
        "COMPLIANCE_CENTER": "Compliance Review",
        "POSTER_CENTER": "Poster Workflow",
        "MANUAL_CENTER": "Operator Review",
    }
    return mapping.get(lane, "Operator Review")
def center_status(lane: str) -> str:
    return "ACTIVE" if lane == "LAUNCH_CENTER" else "WAITING"
def next_action(lane: str) -> str:
    mapping = {
        "LAUNCH_CENTER": "Enter commercial launch batch immediately",
        "ASSET_CENTER": "Finish artwork and mockup, then return to launch",
        "COMPLIANCE_CENTER": "Complete policy review, then return to launch",
        "POSTER_CENTER": "Complete poster prep and visual QA",
        "MANUAL_CENTER": "Manual operator assignment required",
    }
    return mapping.get(lane, "Manual operator assignment required")
def build_summary(title_en: str, product_type: str, safe_term: str) -> str:
    return f"{product_type} | {safe_term} | {title_en}"
def calc_score(priority_tier: str, risk_level: str, lane: str) -> float:
    score = 82
    if priority_tier == "P0":
        score += 14
    elif priority_tier == "P1":
        score += 7
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 2
    if lane == "LAUNCH_CENTER":
        score += 6
    return float(score)
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, commercial_launch_id, listing_ai_id, mj_prompt_id, product_type, priority_tier,
               risk_level, safe_term, title_en, sku_code, ops_lane, owner_role, ops_status,
               blocker_text
        FROM {TABLE_IN}
        ORDER BY ops_score DESC, id DESC
        LIMIT 200
    ''').fetchall()
    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0
    for row in rows:
        lane = pick_lane(row["ops_lane"], row["ops_status"], row["product_type"])
        module = pick_module(lane)
        status = center_status(lane)
        action = next_action(lane)
        summary = build_summary(row["title_en"], row["product_type"], row["safe_term"])
        score = calc_score(row["priority_tier"], row["risk_level"], lane)
        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                launch_ops_id, commercial_launch_id, listing_ai_id, mj_prompt_id,
                product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
                center_lane, center_module, owner_role, center_status, blocker_text,
                next_action, summary_text, center_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["commercial_launch_id"], row["listing_ai_id"], row["mj_prompt_id"],
            row["product_type"], row["priority_tier"], row["risk_level"], row["safe_term"],
            row["title_en"], row["sku_code"], lane, module, row["owner_role"], status,
            row["blocker_text"], action, summary, score
        ))
        inserted += 1
    conn.commit()
    conn.close()
    print(f"[OK] command_center_v87 inserted={inserted} db={DB_PATH}")
if __name__ == "__main__":
    main()
