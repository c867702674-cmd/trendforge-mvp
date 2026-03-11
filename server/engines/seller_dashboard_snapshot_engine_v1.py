
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

def fetch_rows(conn, sql, limit):
    rows = conn.execute(sql, (limit,)).fetchall()
    return [dict(r) for r in rows]

def main():
    conn = connect()

    opportunities = fetch_rows(
        conn,
        "SELECT term, opportunity_score FROM seller_opportunity_feed ORDER BY opportunity_score DESC LIMIT ?",
        20
    )

    listings = fetch_rows(
        conn,
        "SELECT term, listing_title, draft_score FROM listing_auto_drafts ORDER BY draft_score DESC LIMIT ?",
        20
    )

    profits = fetch_rows(
        conn,
        "SELECT term, profit_score, demand_score FROM pod_niche_profits ORDER BY profit_score DESC LIMIT ?",
        20
    )

    payload = {
        "generated_at": utc(),
        "top_opportunities": opportunities,
        "top_listings": listings,
        "top_profits": profits
    }

    conn.execute("DELETE FROM seller_dashboard_snapshots")
    conn.execute(
        "INSERT INTO seller_dashboard_snapshots (snapshot_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("latest", json.dumps(payload, ensure_ascii=False), utc())
    )

    conn.commit()
    print(f"[OK] seller_dashboard_snapshot_engine_v1 wrote snapshot db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
