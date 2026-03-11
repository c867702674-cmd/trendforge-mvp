
#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def main():
    conn = connect()

    rows = conn.execute("""
        SELECT term, profit_score
        FROM pod_niche_profits
        ORDER BY profit_score DESC
        LIMIT 100
    """).fetchall()

    conn.execute("DELETE FROM seller_opportunity_feed")

    inserted = 0

    for r in rows:
        score = float(r["profit_score"] or 0)

        conn.execute(
            """INSERT INTO seller_opportunity_feed
            (term, opportunity_score, source, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            (
                r["term"],
                score,
                "profit_engine",
                json.dumps({"profit_score": score}),
                utc()
            )
        )

        inserted += 1

    conn.commit()
    print(f"[OK] seller_opportunity_feed_engine_v1 inserted={inserted}")
    conn.close()

if __name__ == "__main__":
    main()
