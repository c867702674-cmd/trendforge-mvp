#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, re
BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "release_command_v78"
TABLE_OUT = "listing_ai_v79"
def nice_words(text):
    text = (text or "").replace("-", " ").replace("_", " ").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return [w for w in text.split(" ") if w]
def title_case_words(words): return " ".join(w.capitalize() for w in words[:8])
def build_title(safe_term, product_type):
    words = nice_words(safe_term)
    core = title_case_words(words)
    suffix_map = {"shirt":"Minimalist POD Graphic Tee","mug":"Giftable POD Coffee Cup","poster":"Printable Wall Art Decor"}
    return f"{core}, {suffix_map.get(product_type, 'POD Listing')}"
def build_tags(safe_term, product_type):
    words = nice_words(safe_term)[:6]
    extras = {"shirt":["shirt","pod","gift idea","trending design"],"mug":["mug","pod","gift idea","trending design"],"poster":["poster","wall art","printable","trending design"]}.get(product_type,["pod","gift idea","trending design"])
    arr=[]
    for w in words+extras:
        if w not in arr: arr.append(w)
    return ", ".join(arr[:13])
def build_bullets(safe_term, product_type):
    theme = title_case_words(nice_words(safe_term))
    style_map = {"shirt":"minimalist","mug":"graphic","poster":"printable wall art"}
    audience_map = {"shirt":"general","mug":"gift buyer","poster":"home decor"}
    bullets = [f"- Theme: {theme}",f"- Product: {product_type.capitalize()}",f"- Style: {style_map.get(product_type,'clean pod design')}",f"- Audience: {audience_map.get(product_type,'general')}","- Use for POD listing draft, then manually review trademark and marketplace policy."]
    return "\n".join(bullets)
def build_description(safe_term, product_type):
    theme = title_case_words(nice_words(safe_term))
    return f"This {product_type} listing draft is built around the theme '{theme}'. It is positioned as a clean commercial POD concept for online marketplace sellers. Use this as a ready-to-edit draft foundation, then manually refine sizing, materials, production details, and compliance checks before publishing."
def build_design_prompt(safe_term, product_type):
    return f"{safe_term}, {product_type} design, commercial POD style, centered artwork, clean composition, high contrast, print-ready, no mockup, transparent background"
def build_mockup_prompt(safe_term, product_type):
    scene_map = {"shirt":"folded tee mockup on neutral background, ecommerce lighting","mug":"ceramic mug mockup on simple desk scene, ecommerce lighting","poster":"framed wall art mockup in modern interior, ecommerce lighting"}
    return f"{safe_term}, {scene_map.get(product_type, 'ecommerce mockup scene')}, realistic product presentation"
def calc_score(priority_tier, risk_level, product_type):
    score = 80
    if priority_tier == "P0": score += 12
    elif priority_tier == "P1": score += 6
    if risk_level == "SAFE": score += 8
    elif risk_level == "REVIEW": score += 2
    if product_type == "poster": score -= 2
    return float(score)
def main():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT id, launch_control_id, launch_orchestrator_id, dispatch_center_id, release_routing_id, allocation_board_id, portfolio_matrix_id, executive_grid_id, strategic_hub_id, operations_hq_id, war_room_id, control_tower_id, mission_planner_id, batch_studio_id, command_center_id, ops_dashboard_id, publish_board_id, launch_queue_id, execution_pack_id, listing_id, source_term, safe_term, risk_level, product_type, priority_tier FROM {TABLE_IN} ORDER BY command_score DESC, id DESC LIMIT 200").fetchall()
    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0
    for row in rows:
        title = build_title(row['safe_term'], row['product_type'])
        tags = build_tags(row['safe_term'], row['product_type'])
        bullets = build_bullets(row['safe_term'], row['product_type'])
        desc = build_description(row['safe_term'], row['product_type'])
        design_prompt = build_design_prompt(row['safe_term'], row['product_type'])
        mockup_prompt = build_mockup_prompt(row['safe_term'], row['product_type'])
        score = calc_score(row['priority_tier'], row['risk_level'], row['product_type'])
        sku = f"TF-V79-{row['product_type'].upper()}-{row['id']:04d}"
        conn.execute(f"INSERT INTO {TABLE_OUT} (release_command_id, launch_control_id, launch_orchestrator_id, dispatch_center_id, release_routing_id, allocation_board_id, portfolio_matrix_id, executive_grid_id, strategic_hub_id, operations_hq_id, war_room_id, control_tower_id, mission_planner_id, batch_studio_id, command_center_id, ops_dashboard_id, publish_board_id, launch_queue_id, execution_pack_id, listing_id, source_term, safe_term, risk_level, product_type, priority_tier, title_en, tags_text, bullets_text, description_text, design_prompt, mockup_prompt, sku_code, listing_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (row['id'], row['launch_control_id'], row['launch_orchestrator_id'], row['dispatch_center_id'], row['release_routing_id'], row['allocation_board_id'], row['portfolio_matrix_id'], row['executive_grid_id'], row['strategic_hub_id'], row['operations_hq_id'], row['war_room_id'], row['control_tower_id'], row['mission_planner_id'], row['batch_studio_id'], row['command_center_id'], row['ops_dashboard_id'], row['publish_board_id'], row['launch_queue_id'], row['execution_pack_id'], row['listing_id'], row['source_term'], row['safe_term'], row['risk_level'], row['product_type'], row['priority_tier'], title, tags, bullets, desc, design_prompt, mockup_prompt, sku, score))
        inserted += 1
    conn.commit(); conn.close(); print(f"[OK] listing_ai_v79 inserted={inserted} db={DB_PATH}")
if __name__ == '__main__': main()
