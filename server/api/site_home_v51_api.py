#!/usr/bin/env python3
import os, sqlite3, json
DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT = "/root/trendforge-mvp/server/docs/site_home_v51.json"
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT payload_json FROM site_home_snapshots ORDER BY id DESC LIMIT 1").fetchone()
    payload = {}
    if row and row["payload_json"]:
        try: payload = json.loads(row["payload_json"])
        except Exception: payload = {}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    summary = payload.get("summary", {})
    print(f"[OK] site_home_v51_api wrote={OUT} top_items={summary.get('top_items',0)} do_now={summary.get('do_now',0)} push_total={summary.get('push_total',0)}")
    conn.close()
if __name__ == "__main__":
    main()
