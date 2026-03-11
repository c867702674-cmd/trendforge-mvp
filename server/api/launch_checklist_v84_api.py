#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "launch_checklist_v84.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT id, commercial_golive_id, launch_readiness_id, listing_ai_id, mj_prompt_id,
               product_type, priority_tier, risk_level, safe_term, title_en, sku_code,
               checklist_lane, checklist_owner, checklist_status, must_do_text,
               launch_blocker, next_action, checklist_score, created_at
        FROM launch_checklist_v84
        ORDER BY checklist_score DESC, id DESC
    ''').fetchall()

    items = []
    by_lane = Counter()
    by_owner = Counter()
    by_status = Counter()

    for r in rows:
        by_lane[r["checklist_lane"]] += 1
        by_owner[r["checklist_owner"]] += 1
        by_status[r["checklist_status"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v84",
        "module": "launch_checklist",
        "summary": {
            "total": len(items),
            "by_checklist_lane": dict(by_lane),
            "by_owner": dict(by_owner),
            "by_status": dict(by_status),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] launch_checklist_v84_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
