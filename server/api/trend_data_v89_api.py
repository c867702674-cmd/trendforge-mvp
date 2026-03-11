#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "trend_data_v89.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT id, source_name, source_term, market_code, product_type, trend_score,
               growth_rate, competition_level, action_level, source_url, payload_json, created_at
        FROM trend_data_v89
        ORDER BY trend_score DESC, id DESC
    ''').fetchall()

    items = []
    by_source = Counter()
    by_action = Counter()
    by_product = Counter()

    for r in rows:
        by_source[r["source_name"]] += 1
        by_action[r["action_level"]] += 1
        by_product[r["product_type"]] += 1
        row = dict(r)
        try:
            row["payload_json"] = json.loads(row["payload_json"]) if row["payload_json"] else {}
        except Exception:
            pass
        items.append(row)

    payload = {
        "ok": True,
        "version": "v89",
        "module": "trend_data_engine",
        "summary": {
            "total": len(items),
            "by_source": dict(by_source),
            "by_action_level": dict(by_action),
            "by_product_type": dict(by_product),
        },
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] trend_data_v89_api wrote={OUT_PATH} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
