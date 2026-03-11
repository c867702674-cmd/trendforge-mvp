
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
        SELECT term, COUNT(DISTINCT source) as sources
        FROM global_trend_signals
        GROUP BY term
        ORDER BY sources DESC
        LIMIT 100
    """).fetchall()

    conn.execute("DELETE FROM auto_trend_discoveries")

    inserted = 0
    for r in rows:
        score = float(r["sources"]) * 10.0
        conn.execute(
            """INSERT INTO auto_trend_discoveries
            (term, discovery_score, signal_sources, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            (
                r["term"],
                score,
                r["sources"],
                json.dumps({"sources": r["sources"]}),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] auto_trend_discovery_engine_v1 inserted={inserted}")
    conn.close()

if __name__ == "__main__":
    main()
