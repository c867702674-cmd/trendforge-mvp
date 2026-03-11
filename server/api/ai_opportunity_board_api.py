
#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")

def utc():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = connect()

    rows = conn.execute("""
    SELECT term, final_score, opportunity_score, niche_score
    FROM ai_opportunity_board
    ORDER BY final_score DESC
    LIMIT 30
    """).fetchall()

    items = [dict(r) for r in rows]

    out = os.path.join(OUTPUT_DIR, "ai_opportunity_board.json")

    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": utc(),
            "items": items
        }, f, ensure_ascii=False, indent=2)

    print(f"[OK] ai_opportunity_board_api wrote={out}")
    conn.close()

if __name__ == "__main__":
    main()
