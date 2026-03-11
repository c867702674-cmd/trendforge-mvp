
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
        SELECT term, rank_score
        FROM ai_trend_rankings
        ORDER BY rank_score DESC
        LIMIT 100
    """).fetchall()

    conn.execute("DELETE FROM pod_niche_profits")

    inserted = 0

    for r in rows:
        demand = float(r["rank_score"] or 0)
        niche = demand * 0.6
        profit = niche * 1.4

        conn.execute(
            """INSERT INTO pod_niche_profits
            (term, niche_score, profit_score, demand_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                r["term"],
                niche,
                profit,
                demand,
                json.dumps({"rank_score": demand}),
                utc()
            )
        )

        inserted += 1

    conn.commit()
    print(f"[OK] pod_niche_profit_engine_v1 inserted={inserted}")
    conn.close()

if __name__ == "__main__":
    main()
