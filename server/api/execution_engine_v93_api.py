#!/usr/bin/env python3
import json, os, sqlite3

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
OUT_PATH = os.path.join(BASE_DIR, "docs", "execution_engine_v93.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        '''
        SELECT id, job_id, rule_code, target_channel, execution_status, executed_at, execution_log
        FROM execution_dashboard_v93
        ORDER BY job_id ASC
        '''
    ).fetchall()

    items = [dict(r) for r in rows]

    payload = {
        "ok": True,
        "version": "v93",
        "module": "execution_engine",
        "summary": {
            "total": len(items)
        },
        "items": items,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] execution_engine_v93_api wrote={OUT_PATH} items={len(items)}")

if __name__ == "__main__":
    main()
