#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN_A = "saas_dashboard_v80"
TABLE_IN_B = "mj_prompt_v81"
TABLE_OUT = "launch_readiness_v82"

def pick_lane(priority_tier: str, risk_level: str, product_type: str) -> str:
    if priority_tier == "P0" and risk_level == "SAFE":
        return "READY_TO_LAUNCH"
    if risk_level == "SAFE":
        return "READY_AFTER_ASSET"
    if risk_level == "REVIEW":
        return "POLICY_REVIEW"
    if product_type == "poster":
        return "POSTER_PREP"
    return "MANUAL_CHECK"

def build_note(lane: str, product_type: str) -> str:
    mapping = {
        "READY_TO_LAUNCH": f"{product_type} can move into commercial beta launch queue after final human review.",
        "READY_AFTER_ASSET": f"{product_type} is commercially usable after artwork/mockup asset completion.",
        "POLICY_REVIEW": f"{product_type} needs policy/trademark review before launch.",
        "POSTER_PREP": f"{product_type} should complete poster asset preparation before release.",
        "MANUAL_CHECK": f"{product_type} should stay in manual desk until operator confirms readiness.",
    }
    return mapping.get(lane, "Needs manual readiness confirmation.")

def build_checklist(lane: str) -> str:
    items = [
        "1. Check trademark / policy manually",
        "2. Confirm title readability and keyword quality",
        "3. Confirm listing images / mockup assets",
        "4. Confirm product specs and marketplace settings",
        "5. Final publish decision by operator"
    ]
    if lane == "READY_TO_LAUNCH":
        items.insert(0, "0. Push into beta launch queue")
    elif lane == "READY_AFTER_ASSET":
        items.insert(0, "0. Complete design and mockup assets")
    elif lane == "POLICY_REVIEW":
        items.insert(0, "0. Complete compliance review first")
    elif lane == "POSTER_PREP":
        items.insert(0, "0. Finish poster frame / ratio / mockup prep")
    else:
        items.insert(0, "0. Manual desk review first")
    return "\n".join(items)

def calc_score(priority_tier: str, risk_level: str, product_type: str) -> float:
    score = 72
    if priority_tier == "P0":
        score += 14
    elif priority_tier == "P1":
        score += 7
    if risk_level == "SAFE":
        score += 10
    elif risk_level == "REVIEW":
        score += 2
    if product_type == "poster":
        score -= 1
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f'''
        SELECT
            a.id AS saas_dashboard_id,
            a.listing_ai_id,
            b.id AS mj_prompt_id,
            a.product_type,
            a.priority_tier,
            a.risk_level,
            a.safe_term,
            a.title_en,
            a.sku_code
        FROM {TABLE_IN_A} a
        LEFT JOIN {TABLE_IN_B} b ON a.listing_ai_id = b.listing_ai_id
        ORDER BY a.dashboard_score DESC, a.id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for row in rows:
        lane = pick_lane(row["priority_tier"], row["risk_level"], row["product_type"])
        note = build_note(lane, row["product_type"])
        checklist = build_checklist(lane)
        score = calc_score(row["priority_tier"], row["risk_level"], row["product_type"])

        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                saas_dashboard_id, listing_ai_id, mj_prompt_id, product_type, priority_tier,
                risk_level, safe_term, title_en, sku_code, readiness_lane,
                readiness_note, checklist_text, readiness_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["saas_dashboard_id"], row["listing_ai_id"], row["mj_prompt_id"],
            row["product_type"], row["priority_tier"], row["risk_level"],
            row["safe_term"], row["title_en"], row["sku_code"], lane,
            note, checklist, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] launch_readiness_v82 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
