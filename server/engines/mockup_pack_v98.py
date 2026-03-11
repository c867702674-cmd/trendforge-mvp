import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

HERO_MAP = {
    "shirt": "Front flat lay hero image, centered design, white background, ecommerce-ready",
    "mug": "White ceramic mug hero image, 45-degree angle, clean desk lighting, ecommerce-ready",
    "poster": "Framed poster hero image, straight-on wall shot, modern minimal interior"
}

SCENE_MAP = {
    "shirt": "Lifestyle shirt scene, casual indoor setting, soft natural light",
    "mug": "Giftable mug scene on desk, coffee setup, warm lifestyle atmosphere",
    "poster": "Modern interior wall decor scene, styled room, soft daylight"
}

WHITE_BG_MAP = {
    "shirt": "Pure white background product shot, front-only, no props",
    "mug": "Pure white background mug shot, isolated product, no props",
    "poster": "Pure white background framed poster shot, isolated product"
}

DETAIL_MAP = {
    "shirt": "Fabric close-up, print detail close-up, collar / texture detail",
    "mug": "Handle close-up, print detail close-up, ceramic texture detail",
    "poster": "Frame corner close-up, paper texture detail, print detail close-up"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM mj_prompt_v97"
    ).fetchall()

    inserted = 0

    for r in rows:
        product_type = r["product_type"]

        conn.execute(
            """
            INSERT INTO mockup_pack_v98
            (prompt_id, source_term, product_type, hero_mockup, scene_mockup, white_bg_mockup, detail_mockup, mockup_pack_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                product_type,
                HERO_MAP.get(product_type, "Hero mockup"),
                SCENE_MAP.get(product_type, "Scene mockup"),
                WHITE_BG_MAP.get(product_type, "White background mockup"),
                DETAIL_MAP.get(product_type, "Detail mockup"),
                "Use 4-image pack: hero / scene / white-bg / detail",
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] mockup_pack_v98 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
