#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "listing_ai_v79"
TABLE_OUT = "mj_prompt_v81"

def pick_style(product_type: str, priority_tier: str) -> str:
    if product_type == "shirt":
        return "minimalist commercial POD"
    if product_type == "mug":
        return "clean giftable graphic"
    if product_type == "poster":
        return "printable wall art"
    return "clean commercial POD"

def build_mj_prompt(safe_term: str, product_type: str, style: str) -> str:
    aspect = {"shirt":"--ar 1:1", "mug":"--ar 1:1", "poster":"--ar 3:4"}.get(product_type, "--ar 1:1")
    return (
        f"{safe_term}, {product_type} artwork, {style}, centered composition, "
        f"vector-like clean shapes, high contrast, commercial POD design, "
        f"print-ready, isolated artwork, transparent background style, no mockup {aspect} --v 6"
    )

def build_negative_prompt(product_type: str) -> str:
    return (
        "no watermark, no logo, no brand name, no signature, no text paragraph, "
        "no messy background, no extra limbs, no frame glare, no mockup scene"
    )

def build_mockup_prompt(safe_term: str, product_type: str) -> str:
    scene = {
        "shirt": "flat lay tshirt mockup on neutral background, clean ecommerce lighting",
        "mug": "white ceramic mug mockup on clean desk scene, ecommerce lighting",
        "poster": "framed poster mockup in modern minimal interior, ecommerce lighting",
    }.get(product_type, "clean ecommerce mockup")
    return f"{safe_term}, {scene}, realistic product showcase"

def calc_score(priority_tier: str, risk_level: str, product_type: str) -> float:
    score = 78
    if priority_tier == "P0":
        score += 12
    elif priority_tier == "P1":
        score += 6
    if risk_level == "SAFE":
        score += 8
    elif risk_level == "REVIEW":
        score += 2
    if product_type == "poster":
        score += 1
    return float(score)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, release_command_id, product_type, priority_tier, risk_level, safe_term, title_en, sku_code
        FROM {TABLE_IN}
        ORDER BY listing_score DESC, id DESC
        LIMIT 200
    ''').fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0
    for row in rows:
        style = pick_style(row["product_type"], row["priority_tier"])
        mj = build_mj_prompt(row["safe_term"], row["product_type"], style)
        neg = build_negative_prompt(row["product_type"])
        mockup = build_mockup_prompt(row["safe_term"], row["product_type"])
        score = calc_score(row["priority_tier"], row["risk_level"], row["product_type"])

        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                listing_ai_id, saas_dashboard_id, release_command_id, product_type, priority_tier,
                risk_level, safe_term, title_en, sku_code, design_style, mj_prompt,
                negative_prompt, mockup_prompt, prompt_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["id"], row["release_command_id"], row["product_type"], row["priority_tier"],
            row["risk_level"], row["safe_term"], row["title_en"], row["sku_code"], style, mj,
            neg, mockup, score
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] mj_prompt_v81 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
