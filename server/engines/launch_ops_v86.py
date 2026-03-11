#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "commercial_launch_v85"
TABLE_OUT = "launch_ops_v86"

def pick_lane(launch_lane: str, publish_status: str, product_type: str) -> str:
    if launch_lane == "LIVE_BATCH" and publish_status == "READY_TO_PUSH":
        return "PUSH_NOW"
    if launch_lane == "ASSET_QUEUE":
        return "ASSET_TODO"
    if launch_lane == "COMPLIANCE_QUEUE":
        return "COMPLIANCE_TODO"
    if launch_lane == "POSTER_QUEUE" or product_type == "poster":
        return "POSTER_TODO"
    return "MANUAL_TODO"

def pick_status(lane: str) -> str:
    return "READY" if lane == "PUSH_NOW" else "PENDING"

def next_action(lane: str) -> str:
    mapping = {
        "PUSH_NOW": "Push listing into commercial beta publish batch",
        "ASSET_TODO": "Complete artwork and mockup, then requeue",
        "COMPLIANCE_TODO": "Finish compliance check, then requeue",
        "POSTER_TODO": "Finalize poster prep, then requeue",
        "MANUAL_TODO": "Manual operator review required",
    }
    return mapping.get(lane, "Manual operator review required")

def publish_note(product_type: str, lane: str) -> str:
    if lane == "PUSH_NOW":
        return f"{product_type} is operationally ready for beta publish."
    if lane == "ASSET_TODO":
        return f"{product_type} is waiting for asset completion before publish."
    if lane == "COMPLIANCE_TODO":
        return f"{product_type} is waiting for compliance clearance."
    if lane == "POSTER_TODO":
        return f"{product_type} is waiting for poster-specific prep."
    return f"{product_type} is held for manual operator decision."

def calc_score(priority_tier: str, risk_level: str, lane: str) -> float:
    score = 80
    if priority_tier == "P0":
        score += 14
    elif priority_tier == "P1":
        score += 7
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 2
    if lane == "PUSH_NOW":
        score += 6
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, launch_checklist_id, listing_ai_id, mj_prompt_id, product_type, priority_tier,
               risk_level, safe_term, title_en, sku_code, launch_lane, owner_role,
               publish_status, blocker_text
        FROM {TABLE_IN}
        ORDER BY launch_score DESC, id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0

    for row in rows:
        lane = pick_lane(row["launch_lane"], row["publish_status"], row["product_type"])
        status = pick_status(lane)
        action = next_action(lane)
        note = publish_note(row["product_type"], lane)
        score = calc_score(row["priority_tier"], row["risk_level"], lane)

        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                commercial_launch_id, launch_checklist_id, listing_ai_id, mj_prompt_id,
                product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
                ops_lane, owner_role, ops_status, blocker_text, next_action, publish_note, ops_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["launch_checklist_id"], row["listing_ai_id"], row["mj_prompt_id"],
            row["product_type"], row["priority_tier"], row["risk_level"], row["safe_term"],
            row["title_en"], row["sku_code"], lane, row["owner_role"], status, row["blocker_text"],
            action, note, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] launch_ops_v86 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
