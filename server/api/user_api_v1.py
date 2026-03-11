
#!/usr/bin/env python3
import sqlite3, json, os

DB_PATH = os.getenv("DB_PATH","/root/trendforge-mvp/server/trendforge.db")
OUTPUT="/root/trendforge-mvp/server/docs/user_api_v31.json"

def main():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row

    rows=conn.execute("SELECT email,plan FROM users").fetchall()

    data={
        "users":[dict(r) for r in rows],
        "count":len(rows)
    }

    with open(OUTPUT,"w") as f:
        json.dump(data,f,indent=2)

    print(f"[OK] user_api_v1 wrote={OUTPUT} users={len(rows)}")
    conn.close()

if __name__=="__main__":
    main()
