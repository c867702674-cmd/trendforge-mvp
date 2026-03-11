#!/usr/bin/env python3
import sqlite3, json, os

DB="/root/trendforge-mvp/server/trendforge.db"
OUT="/root/trendforge-mvp/server/docs/push_dispatch_v39.json"

def main():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    rows=conn.execute(
        "SELECT term,route_name,audience,title FROM push_dispatch_logs ORDER BY id DESC LIMIT 80"
    ).fetchall()

    items=[dict(r) for r in rows]

    with open(OUT,"w",encoding="utf-8") as f:
        json.dump({"items":items},f,ensure_ascii=False,indent=2)

    print("[OK] push_dispatch_v39_api wrote",OUT)
    conn.close()

if __name__=="__main__":
    main()
