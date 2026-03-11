#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT = "/root/trendforge-mvp/server/docs/main_index_v53.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT payload_json FROM main_index_snapshots ORDER BY id DESC LIMIT 1").fetchone()

    payload = {}
    if row and row["payload_json"]:
        try:
            payload = json.loads(row["payload_json"])
        except Exception:
            payload = {}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] main_index_v53_api wrote={OUT} pricing={len(payload.get('pricing', []))} top_items={len(payload.get('top_items', []))}")
    conn.close()

if __name__ == "__main__":
    main()
