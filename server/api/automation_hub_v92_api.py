#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "automation_hub_v92.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        '''
        SELECT id, job_id, rule_code, target_channel, job_status, execute_at, result_note, created_at
        FROM automation_dashboard_v92
        ORDER BY job_id ASC
        '''
    ).fetchall()

    items = []
    by_rule = Counter()
    by_channel = Counter()
    by_status = Counter()

    for r in rows:
        by_rule[r["rule_code"]] += 1
        by_channel[r["target_channel"]] += 1
        by_status[r["job_status"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v92",
        "module": "automation_hub",
        "summary": {
            "total": len(items),
            "by_rule": dict(by_rule),
            "by_channel": dict(by_channel),
            "by_status": dict(by_status),
        },
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] automation_hub_v92_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
