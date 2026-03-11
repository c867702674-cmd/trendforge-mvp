
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
    SELECT
        t.id as trend_id,
        t.term,
        b.brain_score,
        n.niche_score
    FROM trends t
    LEFT JOIN ai_trend_brain b ON b.trend_id = t.id
    LEFT JOIN niche_opportunities n ON n.trend_id = t.id
    ORDER BY b.brain_score DESC
    LIMIT 100
    """).fetchall()

    inserted = 0

    for r in rows:

        brain = r["brain_score"] or 0
        niche = r["niche_score"] or 0
        profit = (brain * 0.3 + niche * 0.7)

        final = brain * 0.4 + niche * 0.4 + profit * 0.2

        conn.execute("DELETE FROM ai_opportunity_board WHERE trend_id=?", (r["trend_id"],))

        conn.execute(
            """INSERT INTO ai_opportunity_board
            (trend_id, term, opportunity_score, niche_score, profit_score, final_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                r["trend_id"],
                r["term"],
                brain,
                niche,
                profit,
                final,
                json.dumps({"brain": brain, "niche": niche}),
                utc()
            )
        )

        inserted += 1

    conn.commit()
    print(f"[OK] ai_opportunity_board_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
