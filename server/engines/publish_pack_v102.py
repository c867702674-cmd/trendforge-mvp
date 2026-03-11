import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

SUBTITLE_MAP = {
    "shirt": "Commercial POD shirt draft ready for operator review and publish flow",
    "mug": "Giftable mug draft ready for operator review and publish flow",
    "poster": "Printable wall-art draft ready for operator review and publish flow"
}

CHECKLIST_MAP = {
    "shirt": "1. Review title 2. Review tags 3. Check artwork placement 4. Confirm mockup quality 5. Confirm platform policy 6. Publish",
    "mug": "1. Review title 2. Review tags 3. Check mug print zone 4. Confirm mockup quality 5. Confirm platform policy 6. Publish",
    "poster": "1. Review title 2. Review tags 3. Check framed composition 4. Confirm mockup quality 5. Confirm platform policy 6. Publish"
}

MARKETPLACE_NOTE_MAP = {
    "shirt": "Best suited for Etsy / Shopify POD apparel workflow",
    "mug": "Best suited for Etsy / Shopify giftable mug workflow",
    "poster": "Best suited for Etsy / Shopify printable wall decor workflow"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, listing_title, sku FROM listing_pack_v101"
    ).fetchall()

    inserted = 0

    for r in rows:
        term = r["source_term"]
        product_type = r["product_type"]

        publish_title = r["listing_title"]
        publish_subtitle = SUBTITLE_MAP.get(product_type, "Publish-ready draft")
        publish_checklist = CHECKLIST_MAP.get(product_type, "Review and publish")
        marketplace_note = MARKETPLACE_NOTE_MAP.get(product_type, "General POD marketplace workflow")
        final_publish_pack = f"{publish_title} | SKU={r['sku']} | Ready for final operator publish flow"
        operator_action = "Operator should complete final QA and push listing live"

        conn.execute(
            """
            INSERT INTO publish_pack_v102
            (listing_id, source_term, product_type, publish_title, publish_subtitle, publish_checklist, marketplace_note, final_publish_pack, operator_action, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                publish_title,
                publish_subtitle,
                publish_checklist,
                marketplace_note,
                final_publish_pack,
                operator_action,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] publish_pack_v102 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
