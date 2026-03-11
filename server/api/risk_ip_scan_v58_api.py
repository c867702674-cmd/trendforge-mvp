#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TrendForge V58 Risk / IP Scan API Export
file: /root/trendforge-mvp/server/risk_ip_scan_v58_api.py
"""

import json
import os
import sqlite3
from collections import Counter

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "risk_ip_scan_v58.json")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            id,
            source_term,
            candidate_term,
            normalized_term,
            safe_term,
            rewrite_suggestion,
            risk_level,
            risk_score,
            flags_json,
            duplicate_group,
            source_type,
            source_score,
            created_at
        FROM risk_ip_scan_results_v58
        ORDER BY
            CASE risk_level
                WHEN 'SAFE' THEN 1
                WHEN 'REVIEW' THEN 2
                WHEN 'BLOCK' THEN 3
                ELSE 4
            END,
            risk_score ASC,
            id DESC
    """).fetchall()

    items = []
    counter = Counter()

    for r in rows:
        flags = []
        try:
            flags = json.loads(r["flags_json"] or "[]")
        except Exception:
            flags = []

        item = {
            "id": r["id"],
            "source_term": r["source_term"],
            "candidate_term": r["candidate_term"],
            "normalized_term": r["normalized_term"],
            "safe_term": r["safe_term"],
            "rewrite_suggestion": r["rewrite_suggestion"],
            "risk_level": r["risk_level"],
            "risk_score": r["risk_score"],
            "flags": flags,
            "duplicate_group": r["duplicate_group"],
            "source_type": r["source_type"],
            "source_score": r["source_score"],
            "created_at": r["created_at"],
        }
        items.append(item)
        counter[r["risk_level"]] += 1

    payload = {
        "ok": True,
        "version": "v58",
        "module": "risk_ip_scan",
        "summary": {
            "total": len(items),
            "safe": counter.get("SAFE", 0),
            "review": counter.get("REVIEW", 0),
            "block": counter.get("BLOCK", 0),
        },
        "items": items
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] risk_ip_scan_v58_api wrote={OUT_PATH} items={len(items)}")

    conn.close()


if __name__ == "__main__":
    main()