#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT = "/root/trendforge-mvp/server/docs/push_ready_v37.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, payload_type, priority_score, audience, title, body_json
        FROM push_ready_payloads
        ORDER BY priority_score DESC, id ASC
        LIMIT 50
        """
    ).fetchall()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["body_json"] = json.loads(d["body_json"] or "{}")
        except Exception:
            d["body_json"] = {}
        items.append(d)

    data = {"items": items, "count": len(items)}

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] push_ready_v37_api wrote={OUTPUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
