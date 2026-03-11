import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

COLOR_MAP = {
    "shirt": "Use high-contrast POD-friendly colors, readable from thumbnail view",
    "mug": "Use giftable warm palette with clean contrast and simple focal point",
    "poster": "Use tasteful decor palette, neutral base with elegant accent colors"
}

COMP_MAP = {
    "shirt": "Centered composition, clear focal hierarchy, print-safe margins",
    "mug": "Front-facing readable layout, balanced print area, simple hero focus",
    "poster": "Wall-art layout, breathing space, premium framed-poster composition"
}

COPY_MAP = {
    "shirt": "Keep visual message bold, fast to understand, POD-commercial style",
    "mug": "Emphasize giftability, daily use mood, clean consumer appeal",
    "poster": "Emphasize decor value, aesthetic mood, printable wall-art positioning"
}

PROD_MAP = {
    "shirt": "Deliver 1 hero design + 1 clean mockup + 1 detail shot suggestion",
    "mug": "Deliver 1 hero design + 1 desk scene + 1 isolated ecommerce mockup",
    "poster": "Deliver 1 framed wall mockup + 1 white-bg product view + 1 detail crop"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM mockup_pack_v98"
    ).fetchall()

    inserted = 0

    for r in rows:
        product_type = r["product_type"]

        conn.execute(
            """
            INSERT INTO image_brief_v99
            (mockup_id, source_term, product_type, hero_brief, color_brief, composition_brief, copy_brief, production_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                product_type,
                f"Create a commercial hero image for {r['source_term']} optimized for {product_type}",
                COLOR_MAP.get(product_type, "Use clean commercial colors"),
                COMP_MAP.get(product_type, "Use clean ecommerce composition"),
                COPY_MAP.get(product_type, "Keep message clear and commercial"),
                PROD_MAP.get(product_type, "Deliver hero + mockup pack"),
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] image_brief_v99 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
