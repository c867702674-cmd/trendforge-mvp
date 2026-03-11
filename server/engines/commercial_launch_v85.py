#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "launch_checklist_v84"
TABLE_OUT = "commercial_launch_v85"

def pick_lane(checklist_lane: str, checklist_status: str, product_type: str) -> str:
    if checklist_lane == "PUBLISH_BATCH" and checklist_status == "READY":
        return "LIVE_BATCH"
    if checklist_lane == "ASSET_BLOCKER":
        return "ASSET_QUEUE"
    if checklist_lane == "COMPLIANCE_BLOCKER":
        return "COMPLIANCE_QUEUE"
    if checklist_lane == "POSTER_BLOCKER" or product_type == "poster":
        return "POSTER_QUEUE"
    return "MANUAL_QUEUE"

def publish_status(lane: str) -> str:
    return "READY_TO_PUSH" if lane == "LIVE_BATCH" else "PENDING"

def next_action(lane: str) -> str:
    mapping = {
        "LIVE_BATCH": "Push into commercial beta launch batch now",
        "ASSET_QUEUE": "Complete artwork + mockup, then move to live batch",
        "COMPLIANCE_QUEUE": "Finish compliance review, then move to live batch",
        "POSTER_QUEUE": "Finalize poster prep, then move to live batch",
        "MANUAL_QUEUE": "Manual operator review and queue assignment",
    }
    return mapping.get(lane, "Manual operator review and queue assignment")

def build_launch_pack(product_type: str, safe_term: str) -> str:
    return (
        f"Safe Term: {safe_term}\n"
        f"Product: {product_type}\n"
        f"Pack: title + tags + description + design prompt + mockup prompt\n"
        f"Use: final QA -> upload -> beta publish"
    )

def calc_score(priority_tier: str, risk_level: str, lane: str) -> float:
    score = 78
    if priority_tier == "P0":
        score += 14
    elif priority_tier == "P1":
        score += 7
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 2
    if lane == "LIVE_BATCH":
        score += 6
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, commercial_golive_id, listing_ai_id, mj_prompt_id, product_type, priority_tier,
               risk_level, safe_term, title_en, sku_code, checklist_lane, checklist_owner,
               checklist_status, launch_blocker, next_action
        FROM {TABLE_IN}
        ORDER BY checklist_score DESC, id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0

    for row in rows:
        lane = pick_lane(row["checklist_lane"], row["checklist_status"], row["product_type"])
        status = publish_status(lane)
        action = next_action(lane)
        pack = build_launch_pack(row["product_type"], row["safe_term"])
        score = calc_score(row["priority_tier"], row["risk_level"], lane)

        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                launch_checklist_id, commercial_golive_id, listing_ai_id, mj_prompt_id,
                product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
                launch_lane, owner_role, publish_status, blocker_text, next_action,
                launch_pack_text, launch_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["commercial_golive_id"], row["listing_ai_id"], row["mj_prompt_id"],
            row["product_type"], row["priority_tier"], row["risk_level"], row["safe_term"],
            row["title_en"], row["sku_code"], lane, row["checklist_owner"], status,
            row["launch_blocker"], action, pack, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] commercial_launch_v85 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
