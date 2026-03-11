#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT = "/root/trendforge-mvp/server/docs/trend_expansion_v57.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT base_term, expanded_term, expansion_type, score
        FROM trend_expansion_v57
        ORDER BY score DESC, id ASC
        LIMIT 300
        """
    ).fetchall()

    items = [dict(r) for r in rows]
    data = {"items": items, "count": len(items)}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] trend_expansion_v57_api wrote={OUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
