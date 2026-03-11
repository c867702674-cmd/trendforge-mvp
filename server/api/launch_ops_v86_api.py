#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "launch_ops_v86.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT id, commercial_launch_id, launch_checklist_id, listing_ai_id, mj_prompt_id,
               product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
               ops_lane, owner_role, ops_status, blocker_text, next_action, publish_note,
               ops_score, created_at
        FROM launch_ops_v86
        ORDER BY ops_score DESC, id DESC
    ''').fetchall()

    items = []
    by_lane = Counter()
    by_status = Counter()
    by_owner = Counter()

    for r in rows:
        by_lane[r["ops_lane"]] += 1
        by_status[r["ops_status"]] += 1
        by_owner[r["owner_role"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v86",
        "module": "launch_ops",
        "summary": {
            "total": len(items),
            "by_ops_lane": dict(by_lane),
            "by_ops_status": dict(by_status),
            "by_owner_role": dict(by_owner),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] launch_ops_v86_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
