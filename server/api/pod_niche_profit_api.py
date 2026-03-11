
#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/pod_niche_profit_api.json"

def utc():
    return datetime.now(timezone.utc).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT term, niche_score, profit_score, demand_score
        FROM pod_niche_profits
        ORDER BY profit_score DESC
        LIMIT 50
    """).fetchall()

    data = {
        "generated_at": utc(),
        "items": [dict(r) for r in rows]
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] pod_niche_profit_api wrote={OUTPUT} items={len(data['items'])}")

    conn.close()

if __name__ == "__main__":
    main()
