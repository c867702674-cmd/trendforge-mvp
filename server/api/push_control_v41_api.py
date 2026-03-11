#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/push_control_v41.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        "SELECT payload_json FROM push_control_snapshots ORDER BY id DESC LIMIT 1"
    ).fetchone()

    payload = {}
    if row and row["payload_json"]:
        try:
            payload = json.loads(row["payload_json"])
        except Exception:
            payload = {}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    summary = payload.get("summary", {})
    print(f"[OK] push_control_v41_api wrote={OUTPUT} total={summary.get('total',0)} ok={summary.get('ok',0)} dry_run={summary.get('dry_run',0)} failed={summary.get('failed',0)}")
    conn.close()

if __name__ == "__main__":
    main()
