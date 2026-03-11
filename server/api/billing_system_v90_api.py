#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "billing_system_v90.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        '''
        SELECT id, user_id, email, username, current_plan, payment_provider, billing_cycle,
               subscription_status, amount_usd, renew_at, daily_trend_limit,
               can_view_listing_ai, can_view_mj_prompt, can_view_command_center, created_at
        FROM billing_dashboard_v90
        ORDER BY user_id ASC
        '''
    ).fetchall()

    items = []
    by_plan = Counter()
    by_status = Counter()
    by_provider = Counter()

    for r in rows:
        by_plan[r["current_plan"]] += 1
        by_status[r["subscription_status"]] += 1
        by_provider[r["payment_provider"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v90",
        "module": "billing_system",
        "summary": {
            "total": len(items),
            "by_plan": dict(by_plan),
            "by_status": dict(by_status),
            "by_provider": dict(by_provider),
        },
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] billing_system_v90_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
