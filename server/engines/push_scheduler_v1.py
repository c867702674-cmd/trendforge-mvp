
#!/usr/bin/env python3
import sqlite3, os, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH","/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT count(*) FROM feishu_push_results").fetchone()
    total = rows[0] if rows else 0

    result = {"checked_push_records": total}

    conn.execute(
        "INSERT INTO push_schedule_logs (schedule_name,triggered,result,created_at) VALUES (?,?,?,?)",
        ("auto_push_scheduler",1,json.dumps(result),utc())
    )

    conn.commit()
    print(f"[OK] push_scheduler_v1 checked={total}")
    conn.close()

if __name__ == "__main__":
    main()
