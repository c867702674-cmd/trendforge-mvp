
#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/web_dashboard_v29_api.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        "SELECT payload_json FROM web_dashboard_bundles ORDER BY id DESC LIMIT 1"
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

    opp = len(payload.get("top_opportunities", []))
    lis = len(payload.get("top_listings", []))
    pro = len(payload.get("top_profits", []))
    print(f"[OK] web_dashboard_v29_api wrote={OUTPUT} opportunities={opp} listings={lis} profits={pro}")
    conn.close()

if __name__ == "__main__":
    main()
