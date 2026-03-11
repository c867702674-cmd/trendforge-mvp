#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "launch_readiness_v82"
TABLE_OUT = "commercial_golive_v83"

def pick_lane(readiness_lane: str, product_type: str, risk_level: str) -> str:
    if readiness_lane == "READY_TO_LAUNCH":
        return "GO_LIVE_NOW"
    if readiness_lane == "READY_AFTER_ASSET":
        return "ASSET_FINISH"
    if readiness_lane == "POLICY_REVIEW":
        return "COMPLIANCE_GATE"
    if readiness_lane == "POSTER_PREP" or product_type == "poster":
        return "POSTER_FINALIZE"
    return "OPERATOR_HOLD"

def build_note(lane: str, product_type: str) -> str:
    if lane == "GO_LIVE_NOW":
        return f"{product_type} is ready for commercial beta go-live after final operator confirmation."
    if lane == "ASSET_FINISH":
        return f"{product_type} needs final design/mockup asset completion before go-live."
    if lane == "COMPLIANCE_GATE":
        return f"{product_type} must pass compliance / trademark gate before publishing."
    if lane == "POSTER_FINALIZE":
        return f"{product_type} should finish poster-specific ratio, framing, and mockup prep."
    return f"{product_type} should remain on operator hold until manually approved."

def build_operator_action(lane: str) -> str:
    mapping = {
        "GO_LIVE_NOW": "Push into beta launch batch",
        "ASSET_FINISH": "Complete design + mockup, then return",
        "COMPLIANCE_GATE": "Complete manual compliance review",
        "POSTER_FINALIZE": "Complete poster prep and recheck",
        "OPERATOR_HOLD": "Manual desk review required",
    }
    return mapping.get(lane, "Manual desk review required")

def build_checklist(lane: str) -> str:
    common = [
        "1. Verify title / tags / description",
        "2. Verify artwork and mockup quality",
        "3. Verify marketplace settings and pricing",
        "4. Final trademark / policy check",
        "5. Operator confirms publish decision"
    ]
    if lane == "GO_LIVE_NOW":
        common.insert(0, "0. Add to commercial beta go-live queue")
    elif lane == "ASSET_FINISH":
        common.insert(0, "0. Finish artwork and mockup assets")
    elif lane == "COMPLIANCE_GATE":
        common.insert(0, "0. Finish compliance gate review")
    elif lane == "POSTER_FINALIZE":
        common.insert(0, "0. Finalize poster size / ratio / frame / mockup")
    else:
        common.insert(0, "0. Keep in operator hold")
    return "\n".join(common)

def calc_score(priority_tier: str, risk_level: str, lane: str) -> float:
    score = 74
    if priority_tier == "P0":
        score += 14
    elif priority_tier == "P1":
        score += 7
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 2
    if lane == "GO_LIVE_NOW":
        score += 6
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f'''
        SELECT id, saas_dashboard_id, listing_ai_id, mj_prompt_id, product_type, priority_tier,
               risk_level, safe_term, title_en, sku_code, readiness_lane
        FROM {TABLE_IN}
        ORDER BY readiness_score DESC, id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_lane(row["readiness_lane"], row["product_type"], row["risk_level"])
        note = build_note(lane, row["product_type"])
        operator_action = build_operator_action(lane)
        checklist = build_checklist(lane)
        score = calc_score(row["priority_tier"], row["risk_level"], lane)

        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                launch_readiness_id, saas_dashboard_id, listing_ai_id, mj_prompt_id,
                product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
                golive_lane, golive_note, operator_action, checklist_text, golive_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["saas_dashboard_id"], row["listing_ai_id"], row["mj_prompt_id"],
            row["product_type"], row["priority_tier"], row["risk_level"], row["safe_term"],
            row["title_en"], row["sku_code"], lane, note, operator_action, checklist, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] commercial_golive_v83 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
