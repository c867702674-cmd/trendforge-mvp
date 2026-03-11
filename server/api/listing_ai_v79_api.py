#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter
BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "listing_ai_v79.json")
def main():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, release_command_id, launch_control_id, launch_orchestrator_id, dispatch_center_id, release_routing_id, allocation_board_id, portfolio_matrix_id, executive_grid_id, strategic_hub_id, operations_hq_id, war_room_id, control_tower_id, mission_planner_id, batch_studio_id, command_center_id, ops_dashboard_id, publish_board_id, launch_queue_id, execution_pack_id, listing_id, source_term, safe_term, risk_level, product_type, priority_tier, title_en, tags_text, bullets_text, description_text, design_prompt, mockup_prompt, sku_code, listing_score, created_at FROM listing_ai_v79 ORDER BY listing_score DESC, id DESC").fetchall()
    items=[]; by_product=Counter(); by_priority=Counter()
    for r in rows:
        by_product[r['product_type']]+=1; by_priority[r['priority_tier']]+=1; items.append(dict(r))
    payload={"ok":True,"version":"v79","module":"listing_ai","summary":{"total":len(items),"by_product_type":dict(by_product),"by_priority":dict(by_priority)},"items":items}
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH,'w',encoding='utf-8') as f: json.dump(payload,f,ensure_ascii=False,indent=2)
    print(f"[OK] listing_ai_v79_api wrote={OUT_PATH} items={len(items)}")
    conn.close()
if __name__ == '__main__': main()
