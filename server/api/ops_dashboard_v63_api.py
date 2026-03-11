#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "ops_dashboard_v63.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            publish_board_id,
            launch_queue_id,
            execution_pack_id,
            listing_id,
            source_term,
            safe_term,
            risk_level,
            product_type,
            title_en,
            sku_code,
            priority_tier,
            schedule_bucket,
            publish_status,
            board_column,
            board_rank,
            ops_stage,
            action_hint,
            dashboard_score,
            created_at
        FROM ops_dashboard_v63
        ORDER BY dashboard_score DESC, id DESC
    """).fetchall()

    items = []
    by_stage = Counter()
    by_product = Counter()
    by_priority = Counter()

    for r in rows:
        by_stage[r["ops_stage"]] += 1
        by_product[r["product_type"]] += 1
        by_priority[r["priority_tier"]] += 1
        items.append({
            "id": r["id"],
            "publish_board_id": r["publish_board_id"],
            "launch_queue_id": r["launch_queue_id"],
            "execution_pack_id": r["execution_pack_id"],
            "listing_id": r["listing_id"],
            "source_term": r["source_term"],
            "safe_term": r["safe_term"],
            "risk_level": r["risk_level"],
            "product_type": r["product_type"],
            "title_en": r["title_en"],
            "sku_code": r["sku_code"],
            "priority_tier": r["priority_tier"],
            "schedule_bucket": r["schedule_bucket"],
            "publish_status": r["publish_status"],
            "board_column": r["board_column"],
            "board_rank": r["board_rank"],
            "ops_stage": r["ops_stage"],
            "action_hint": r["action_hint"],
            "dashboard_score": r["dashboard_score"],
            "created_at": r["created_at"],
        })

    payload = {
        "ok": True,
        "version": "v63",
        "module": "ops_dashboard",
        "summary": {
            "total": len(items),
            "by_ops_stage": dict(by_stage),
            "by_product_type": dict(by_product),
            "by_priority": dict(by_priority),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] ops_dashboard_v63_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
