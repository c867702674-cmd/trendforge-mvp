#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/seller_alerts_v34.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, alert_level, alert_title, alert_text, alert_score
        FROM seller_alerts
        ORDER BY alert_score DESC, id ASC
        LIMIT 50
        """
    ).fetchall()

    data = {"items": [dict(r) for r in rows], "count": len(rows)}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] seller_alerts_v34_api wrote={OUTPUT} items={len(rows)}")
    conn.close()

if __name__ == "__main__":
    main()
