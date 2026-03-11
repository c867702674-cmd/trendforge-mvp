
#!/usr/bin/env python3
import sqlite3, json, os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.utcnow().isoformat()

def choose_sku(term):
    t = term.lower()
    if "cat" in t or "dog" in t:
        return "tshirt"
    if "retro" in t:
        return "poster"
    if "gift" in t:
        return "mug"
    return "tshirt"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT term, title, design_prompt, tags_json FROM ai_listing_drafts LIMIT 120"
    ).fetchall()

    conn.execute("DELETE FROM pod_sku_packs_v56")

    inserted = 0

    for r in rows:
        term = r["term"]
        sku = choose_sku(term)

        title = r["title"]
        prompt = r["design_prompt"]

        conn.execute(
            """
            INSERT INTO pod_sku_packs_v56
            (term, sku_type, sku_title, mj_prompt, listing_title, tags_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                sku,
                f"{term} {sku} design",
                prompt,
                title,
                r["tags_json"],
                utc()
            )
        )

        inserted += 1

    conn.commit()
    conn.close()

    print(f"[OK] pod_sku_pack_engine_v56 inserted={inserted}")
if __name__ == "__main__":
    main()
