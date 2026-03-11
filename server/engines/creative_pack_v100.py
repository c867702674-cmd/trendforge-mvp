import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

TAGLINE_MAP = {
    "shirt": "Fast-read POD graphic direction for commercial click-through",
    "mug": "Giftable consumer-friendly creative direction for ecommerce conversion",
    "poster": "Decor-oriented visual concept for printable wall-art positioning"
}

VISUAL_MAP = {
    "shirt": "Focus on a bold centered hero graphic, thumbnail readability, POD-ready composition",
    "mug": "Focus on clear print zone, warm gifting mood, simple commercial composition",
    "poster": "Focus on premium wall-art layout, tasteful spacing, interior-friendly design language"
}

CHECKLIST_MAP = {
    "shirt": "1. Generate artwork 2. Review thumbnail readability 3. Prepare hero mockup 4. Prepare detail crop 5. Final listing upload",
    "mug": "1. Generate artwork 2. Review handle-safe print layout 3. Prepare hero mug mockup 4. Prepare desk scene 5. Final listing upload",
    "poster": "1. Generate artwork 2. Review frame-safe composition 3. Prepare wall mockup 4. Prepare white background product shot 5. Final listing upload"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, hero_brief, production_note FROM image_brief_v99"
    ).fetchall()

    inserted = 0

    for r in rows:
        term = r["source_term"]
        product_type = r["product_type"]

        title_idea = f"{term} | {product_type} creative pack"
        tagline = TAGLINE_MAP.get(product_type, "Commercial creative execution pack")
        visual_direction = VISUAL_MAP.get(product_type, "Clean ecommerce design direction")
        prompt_pack = f"Use MJ prompt + negative prompt + mockup prompt for {term}"
        mockup_pack = f"Hero / Scene / White BG / Detail pack for {product_type}"
        production_checklist = CHECKLIST_MAP.get(product_type, "Artwork → Mockup → Upload")

        conn.execute(
            """
            INSERT INTO creative_pack_v100
            (brief_id, source_term, product_type, title_idea, tagline, visual_direction, prompt_pack, mockup_pack, production_checklist, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                title_idea,
                tagline,
                visual_direction,
                prompt_pack,
                mockup_pack,
                production_checklist,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] creative_pack_v100 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
