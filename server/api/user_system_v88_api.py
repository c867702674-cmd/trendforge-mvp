#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "user_system_v88.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        '''
        SELECT id, user_id, email, username, plan_code, role_code, api_token, daily_trend_limit,
               can_view_listing_ai, can_view_mj_prompt, can_view_command_center, account_status, created_at
        FROM user_dashboard_v88
        ORDER BY user_id ASC
        '''
    ).fetchall()

    items = []
    by_plan = Counter()
    by_status = Counter()

    for r in rows:
        by_plan[r["plan_code"]] += 1
        by_status[r["account_status"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v88",
        "module": "user_system",
        "summary": {
            "total": len(items),
            "by_plan": dict(by_plan),
            "by_status": dict(by_status),
        },
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] user_system_v88_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
