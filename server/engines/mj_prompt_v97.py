import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

STYLE_MAP = {
    "shirt": "clean typography t-shirt design, centered composition, commercial POD style, print-ready, isolated artwork",
    "mug": "clean giftable mug graphic, centered composition, commercial POD style, print-ready, isolated artwork",
    "poster": "minimal wall art poster design, elegant composition, printable decor style, isolated artwork"
}

NEGATIVE = "no watermark, no logo, no brand name, no signature, no mockup, no extra limbs, no blurry details, no messy background"

MOCKUP_MAP = {
    "shirt": "realistic t-shirt mockup, ecommerce product display, folded or front flat lay, clean lighting, white background",
    "mug": "white ceramic mug mockup on clean desk scene, ecommerce lighting, realistic product showcase",
    "poster": "minimal poster mockup in modern interior, framed wall art scene, soft natural lighting, ecommerce presentation"
}

def build_prompt(term, product_type):
    style = STYLE_MAP.get(product_type, "commercial POD design, isolated artwork")
    return f"{term}, {style}, high contrast, transparent background style, no mockup --ar 1:1 --v 6"

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM trend_data_v89"
    ).fetchall()

    inserted = 0

    for r in rows:
        term = r["source_term"]
        product_type = r["product_type"]
        style_hint = STYLE_MAP.get(product_type, "commercial POD design")

        mj_prompt = build_prompt(term, product_type)
        negative_prompt = NEGATIVE
        mockup_prompt = MOCKUP_MAP.get(product_type, "ecommerce product mockup")

        conn.execute(
            """
            INSERT INTO mj_prompt_v97
            (trend_id, source_term, product_type, style_hint, mj_prompt, negative_prompt, mockup_prompt, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                style_hint,
                mj_prompt,
                negative_prompt,
                mockup_prompt,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] mj_prompt_v97 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
