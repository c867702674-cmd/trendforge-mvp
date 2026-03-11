
#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/seller_dashboard_v28_api.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        "SELECT payload_json FROM seller_dashboard_snapshots ORDER BY id DESC LIMIT 1"
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

    counts = {
        "opportunities": len(payload.get("top_opportunities", [])),
        "listings": len(payload.get("top_listings", [])),
        "profits": len(payload.get("top_profits", [])),
    }

    print(f"[OK] seller_dashboard_v28_api wrote={OUTPUT} opportunities={counts['opportunities']} listings={counts['listings']} profits={counts['profits']}")
    conn.close()

if __name__ == "__main__":
    main()
