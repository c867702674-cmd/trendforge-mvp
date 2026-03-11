#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/saas_core_v30_api.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT payload_json FROM saas_core_snapshots ORDER BY id DESC LIMIT 1"
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

    counts = payload.get("counts", {})
    print(f"[OK] saas_core_v30_api wrote={OUTPUT} opportunities={counts.get('opportunities',0)} listings={counts.get('listings',0)} profits={counts.get('profits',0)} rankings={counts.get('rankings',0)}")
    conn.close()

if __name__ == "__main__":
    main()
