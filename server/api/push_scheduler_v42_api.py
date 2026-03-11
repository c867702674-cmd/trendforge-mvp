
#!/usr/bin/env python3
import sqlite3, os, json

DB_PATH = os.getenv("DB_PATH","/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/push_scheduler_v42.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT schedule_name,triggered,result,created_at FROM push_schedule_logs ORDER BY id DESC LIMIT 100"
    ).fetchall()

    data = {"items":[dict(r) for r in rows],"count":len(rows)}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

    print(f"[OK] push_scheduler_v42_api wrote={OUTPUT} items={len(rows)}")

if __name__ == "__main__":
    main()
