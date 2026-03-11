#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3
BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "launch_control_v77"
TABLE_OUT = "release_command_v78"

def pick_lane(control_lane, priority_tier, product_type):
    if control_lane == "CONTROL_RELEASE" and priority_tier == "P0":
        return "COMMAND_LAUNCH"
    if control_lane == "CONTROL_CREATIVE":
        return "COMMAND_CREATIVE"
    if product_type == "poster":
        return "COMMAND_POSTER"
    if control_lane == "CONTROL_RESERVE":
        return "COMMAND_RESERVE"
    return "COMMAND_MANUAL"

def pick_action(lane, product_type, risk_level):
    if lane == "COMMAND_LAUNCH":
        return f"Command immediate launch for {product_type} after final manual compliance review."
    if lane == "COMMAND_CREATIVE":
        return f"Command creative completion for {product_type}, then return it to launch control."
    if lane == "COMMAND_POSTER":
        return f"Command poster workflow through reusable template pipeline. Risk={risk_level}."
    if lane == "COMMAND_RESERVE":
        return f"Command reserve holding until release timing improves. Risk={risk_level}."
    return f"Command via manual review path for operator judgment. Risk={risk_level}."

def calc_score(control_score, lane, priority_tier):
    score = float(control_score or 0)
    if lane == "COMMAND_LAUNCH":
        score += 10
    elif lane == "COMMAND_CREATIVE":
        score += 6
    elif lane == "COMMAND_POSTER":
        score += 4
    if priority_tier == "P0":
        score += 4
    return round(score, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f'''
        SELECT id, launch_orchestrator_id, dispatch_center_id, release_routing_id, allocation_board_id,
               portfolio_matrix_id, executive_grid_id, strategic_hub_id, operations_hq_id, war_room_id,
               control_tower_id, mission_planner_id, batch_studio_id, command_center_id, ops_dashboard_id,
               publish_board_id, launch_queue_id, execution_pack_id, listing_id, source_term, safe_term,
               risk_level, product_type, title_en, sku_code, priority_tier, control_lane, control_score
        FROM {TABLE_IN}
        ORDER BY control_score DESC, id DESC
        LIMIT 120
    ''').fetchall()
    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0
    for row in rows:
        lane = pick_lane(row["control_lane"], row["priority_tier"], row["product_type"])
        action = pick_action(lane, row["product_type"], row["risk_level"])
        score = calc_score(row["control_score"], lane, row["priority_tier"])
        conn.execute(f'''
            INSERT INTO {TABLE_OUT} (
                launch_control_id, launch_orchestrator_id, dispatch_center_id, release_routing_id,
                allocation_board_id, portfolio_matrix_id, executive_grid_id, strategic_hub_id,
                operations_hq_id, war_room_id, control_tower_id, mission_planner_id, batch_studio_id,
                command_center_id, ops_dashboard_id, publish_board_id, launch_queue_id, execution_pack_id,
                listing_id, source_term, safe_term, risk_level, product_type, title_en, sku_code,
                priority_tier, control_lane, control_score, command_lane, command_action, command_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["id"], row["launch_orchestrator_id"], row["dispatch_center_id"], row["release_routing_id"],
            row["allocation_board_id"], row["portfolio_matrix_id"], row["executive_grid_id"], row["strategic_hub_id"],
            row["operations_hq_id"], row["war_room_id"], row["control_tower_id"], row["mission_planner_id"],
            row["batch_studio_id"], row["command_center_id"], row["ops_dashboard_id"], row["publish_board_id"],
            row["launch_queue_id"], row["execution_pack_id"], row["listing_id"], row["source_term"],
            row["safe_term"], row["risk_level"], row["product_type"], row["title_en"], row["sku_code"],
            row["priority_tier"], row["control_lane"], row["control_score"], lane, action, score
        ))
        inserted += 1
    conn.commit()
    conn.close()
    print(f"[OK] release_command_v78 inserted={inserted} db={DB_PATH}")
if __name__ == "__main__":
    main()
