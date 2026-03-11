#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT = "/root/trendforge-mvp/server/docs/mj_prompt_v55.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, platform, style_name, subject_line, mj_prompt, sdxl_prompt,
               negative_prompt, aspect_ratio, sku_hint
        FROM mj_prompt_drafts_v55
        ORDER BY id ASC
        LIMIT 100
        """
    ).fetchall()

    items = [dict(r) for r in rows]
    data = {"items": items, "count": len(items)}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] mj_prompt_v55_api wrote={OUT} items={len(items)}")
    conn.close()

if __name__ == "__main__":
    main()
