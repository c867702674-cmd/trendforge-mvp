import sqlite3
import re

DB='/root/trendforge-mvp/server/trendforge.db'

def slug(s):
    return re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')

def build_title(term, product_type):
    if product_type == "shirt":
        return f"{term.title()}, Minimalist POD Graphic Tee"
    if product_type == "mug":
        return f"{term.title()}, Giftable POD Coffee Cup"
    if product_type == "poster":
        return f"{term.title()}, Printable Wall Art Decor"
    return f"{term.title()}, POD Listing"

def build_bullets(term, product_type):
    bullets = [
        f"Theme: {term.title()}",
        f"Product: {product_type.title()}",
        "Style: commercial POD ready",
        "Audience: general ecommerce buyer",
        "Use as listing draft, then manually review trademark and platform policy"
    ]
    return " | ".join(bullets)

def build_tags(term, product_type):
    parts = [p.strip() for p in term.split() if p.strip()]
    extra = [product_type, "pod", "gift idea", "trending design"]
    tags = parts + extra
    return ", ".join(tags[:13])

def build_description(term, product_type):
    return (
        f"This {product_type} listing pack is built around the theme '{term.title()}'. "
        f"It is positioned as a commercial POD concept for sellers. "
        f"Use this as a marketplace-ready foundation, then manually refine sizing, "
        f"materials, production details, and compliance checks before publishing."
    )

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM creative_pack_v100"
    ).fetchall()

    inserted = 0

    for i, r in enumerate(rows, start=1):
        term = r["source_term"]
        product_type = r["product_type"]

        listing_title = build_title(term, product_type)
        listing_bullets = build_bullets(term, product_type)
        listing_tags = build_tags(term, product_type)
        listing_description = build_description(term, product_type)
        sku = f"TF-V101-{product_type.upper()}-{slug(term)[:28]}-{i:04d}"
        listing_note = "Ready for listing draft use; operator should do final compliance review"

        conn.execute(
            """
            INSERT INTO listing_pack_v101
            (creative_id, source_term, product_type, listing_title, listing_bullets, listing_tags, listing_description, sku, listing_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                listing_title,
                listing_bullets,
                listing_tags,
                listing_description,
                sku,
                listing_note,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] listing_pack_v101 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
