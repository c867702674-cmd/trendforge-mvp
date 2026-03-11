
#!/usr/bin/env python3
import sqlite3, json, os

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT = "/root/trendforge-mvp/server/docs/pod_sku_packs_v56.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT term, sku_type, sku_title, mj_prompt, listing_title, tags_json FROM pod_sku_packs_v56 LIMIT 100"
    ).fetchall()

    items = [dict(r) for r in rows]

    data = {
        "items": items,
        "count": len(items)
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] pod_sku_pack_v56_api wrote={OUT}")
if __name__ == "__main__":
    main()
