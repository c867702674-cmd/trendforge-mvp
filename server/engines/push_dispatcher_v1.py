#!/usr/bin/env python3
import sqlite3, os, json, datetime

DB = os.getenv("DB_PATH","/root/trendforge-mvp/server/trendforge.db")

def now():
    return datetime.datetime.utcnow().isoformat()

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT term,route_name,audience,title FROM audience_routes ORDER BY priority_score DESC LIMIT 100"
    ).fetchall()

    inserted=0

    for r in rows:
        conn.execute(
            "INSERT INTO push_dispatch_logs(term,route_name,audience,title,dispatched,created_at) VALUES (?,?,?,?,?,?)",
            (
                r["term"],
                r["route_name"],
                r["audience"],
                r["title"],
                1,
                now()
            )
        )
        inserted+=1

    conn.commit()
    print(f"[OK] push_dispatcher_v1 dispatched={inserted}")
    conn.close()

if __name__=="__main__":
    main()
