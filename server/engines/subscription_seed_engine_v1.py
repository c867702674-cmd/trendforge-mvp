#!/usr/bin/env python3
import sqlite3, os
from datetime import datetime, timezone, timedelta

DB_PATH = os.getenv("DB_PATH","/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def renew():
    return (datetime.now(timezone.utc)+timedelta(days=30)).isoformat()

def main():
    conn=sqlite3.connect(DB_PATH)
    cur=conn.cursor()

    cur.execute("DELETE FROM subscriptions")

    cur.execute(
        "INSERT INTO subscriptions (user_email,plan,status,renew_date,created_at) VALUES (?,?,?,?,?)",
        ("admin@trendforge.ai","pro","active",renew(),utc())
    )

    conn.commit()
    print("[OK] subscription_seed_engine_v1 created default subscription")
    conn.close()

if __name__=="__main__":
    main()
