#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "feishu_card_v95.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        '''
        SELECT id, job_id, target_channel, card_title, send_status, response_text, sent_at, created_at
        FROM feishu_card_dashboard_v95
        ORDER BY job_id ASC
        '''
    ).fetchall()

    items = []
    by_channel = Counter()
    by_status = Counter()
    for r in rows:
        by_channel[r["target_channel"]] += 1
        by_status[r["send_status"]] += 1
        items.append(dict(r))

    payload = {
        "ok": True,
        "version": "v95",
        "module": "feishu_card_studio",
        "summary": {
            "total": len(items),
            "by_channel": dict(by_channel),
            "by_status": dict(by_status),
        },
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] feishu_card_v95_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
