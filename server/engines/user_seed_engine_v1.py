
#!/usr/bin/env python3
import sqlite3, uuid, os
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH","/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    email = "admin@trendforge.ai"
    api_key = str(uuid.uuid4())

    cur.execute("DELETE FROM users")

    cur.execute(
        "INSERT INTO users (email,api_key,plan,created_at) VALUES (?,?,?,?)",
        (email,api_key,"pro",utc())
    )

    conn.commit()
    print("[OK] user_seed_engine_v1 created admin user")
    conn.close()

if __name__ == "__main__":
    main()
