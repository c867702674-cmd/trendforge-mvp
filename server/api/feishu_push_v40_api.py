#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/feishu_push_v40.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, audience, title, ok, dry_run, http_status, response_text, created_at
        FROM feishu_push_results
        ORDER BY id DESC
        LIMIT 100
        """
    ).fetchall()

    data = {"items": [dict(r) for r in rows], "count": len(rows)}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] feishu_push_v40_api wrote={OUTPUT} items={len(rows)}")
    conn.close()

if __name__ == "__main__":
    main()
