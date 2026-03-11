#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "commercial_golive_v83"
TABLE_OUT = "launch_checklist_v84"

def pick_lane(golive_lane: str) -> str:
    if golive_lane == "GO_LIVE_NOW":
        return "PUBLISH_BATCH"
    if golive_lane == "ASSET_FINISH":
        return "ASSET_BLOCKER"
    if golive_lane == "COMPLIANCE_GATE":
        return "COMPLIANCE_BLOCKER"
    if golive_lane == "POSTER_FINALIZE":
        return "POSTER_BLOCKER"
    return "MANUAL_BLOCKER"

def pick_owner(lane: str, product_type: str) -> str:
    if lane == "PUBLISH_BATCH":
        return "operator"
    if lane == "ASSET_BLOCKER":
        return "designer"
    if lane == "COMPLIANCE_BLOCKER":
        return "operator"
    if lane == "POSTER_BLOCKER":
        return "designer"
    return "operator"

def pick_status(lane: str) -> str:
    if lane == "PUBLISH_BATCH":
        return "READY"
    return "BLOCKED"

def must_do(lane: str, product_type: str) -> str:
    if lane == "PUBLISH_BATCH":
        return "1. Final operator confirm\n2. Final marketplace settings\n3. Push into commercial beta batch"
    if lane == "ASSET_BLOCKER":
        return f"1. Finish {product_type} artwork\n2. Finish mockup assets\n3. Return to publish batch"
    if lane == "COMPLIANCE_BLOCKER":
        return "1. Trademark / policy review\n2. Fix risky wording\n3. Return to publish batch"
    if lane == "POSTER_BLOCKER":
        return "1. Confirm poster ratio / frame / mockup\n2. Final visual QA\n3. Return to publish batch"
    return "1. Manual desk review\n2. Operator decision\n3. Return to appropriate queue"

def blocker(lane: str, product_type: str) -> str:
    if lane == "PUBLISH_BATCH":
        return "none"
    if lane == "ASSET_BLOCKER":
        return f"{product_type} asset not finished"
    if lane == "COMPLIANCE_BLOCKER":
        return "compliance review pending"
    if lane == "POSTER_BLOCKER":
        return "poster prep pending"
    return "manual operator hold"

def next_action(lane: str) -> str:
    mapping = {
        "PUBLISH_BATCH": "Publish in beta batch",
        "ASSET_BLOCKER": "Complete artwork and mockup",
        "COMPLIANCE_BLOCKER": "Finish compliance review",
        "POSTER_BLOCKER": "Finalize poster prep",
        "MANUAL_BLOCKER": "Manual operator review",
    }
    return mapping.get(lane, "Manual operator review")

def calc_score(priority_tier: str, risk_level: str, lane: str) -> float:
    score = 76
    if priority_tier == "P0":
        score += 14
    elif priority_tier == "P1":
        score += 7
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 2
    if lane == "PUBLISH_BATCH":
        score += 6
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, launch_readiness_id, listing_ai_id, mj_prompt_id, product_type, priority_tier,
               risk_level, safe_term, title_en, sku_code, golive_lane
        FROM {TABLE_IN}
        ORDER BY golive_score DESC, id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0

    for row in rows:
        lane = pick_lane(row["golive_lane"])
        owner = pick_owner(lane, row["product_type"])
        status = pick_status(lane)
        todo = must_do(lane, row["product_type"])
        block = blocker(lane, row["product_type"])
        action = next_action(lane)
        score = calc_score(row["priority_tier"], row["risk_level"], lane)

        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                commercial_golive_id, launch_readiness_id, listing_ai_id, mj_prompt_id,
                product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
                checklist_lane, checklist_owner, checklist_status, must_do_text,
                launch_blocker, next_action, checklist_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["launch_readiness_id"], row["listing_ai_id"], row["mj_prompt_id"],
            row["product_type"], row["priority_tier"], row["risk_level"], row["safe_term"],
            row["title_en"], row["sku_code"], lane, owner, status, todo, block, action, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] launch_checklist_v84 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
