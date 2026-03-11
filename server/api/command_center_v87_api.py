#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter
BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "command_center_v87.json")
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT id, launch_ops_id, commercial_launch_id, listing_ai_id, mj_prompt_id,
               product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
               center_lane, center_module, owner_role, center_status, blocker_text,
               next_action, summary_text, center_score, created_at
        FROM command_center_v87
        ORDER BY center_score DESC, id DESC
    ''').fetchall()
    items = []
    by_lane = Counter()
    by_status = Counter()
    by_module = Counter()
    for r in rows:
        by_lane[r["center_lane"]] += 1
        by_status[r["center_status"]] += 1
        by_module[r["center_module"]] += 1
        items.append(dict(r))
    payload = {
        "ok": True,
        "version": "v87",
        "module": "command_center",
        "summary": {
            "total": len(items),
            "by_center_lane": dict(by_lane),
            "by_center_status": dict(by_status),
            "by_center_module": dict(by_module),
        },
        "items": items
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[OK] command_center_v87_api wrote={OUT_PATH} items={len(items)}")
    conn.close()
if __name__ == "__main__":
    main()
