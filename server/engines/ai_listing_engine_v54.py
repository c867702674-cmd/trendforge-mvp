#!/usr/bin/env python3
import os, sqlite3, json, re
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def clean_term(term: str) -> str:
    term = re.sub(r"\s+", " ", str(term or "")).strip()
    return term[:80]

def title_case(s: str) -> str:
    return " ".join(w.capitalize() for w in s.split())

def infer_product(term: str) -> str:
    tl = term.lower()
    if "gift" in tl:
        return "Gift Mug"
    if "cat" in tl or "dog" in tl:
        return "Graphic Tee"
    if "teacher" in tl or "nurse" in tl:
        return "Appreciation Shirt"
    if "baseball" in tl or "sports" in tl:
        return "Fan Shirt"
    return "Graphic Tee"

def infer_style(term: str) -> str:
    tl = term.lower()
    if "retro" in tl:
        return "retro vintage distressed"
    if "minimal" in tl or "line" in tl:
        return "minimal clean line art"
    if "cat" in tl or "dog" in tl:
        return "cute giftable illustration"
    return "clean commercial typography"

def make_title(term: str, product: str) -> str:
    base = title_case(term)
    if product == "Gift Mug":
        return f"{base} {product} Funny Trend Gift"
    if product == "Fan Shirt":
        return f"{base} {product} Trend Graphic Fan Apparel"
    return f"{base} {product} Trend Graphic Design"

def bullets(term: str, product: str, style: str):
    base = title_case(term)
    return [
        f"Commercial POD direction for {base} with {style} styling.",
        f"Built for fast listing tests on Amazon, Etsy, and Shopify style catalogs.",
        f"Giftable niche positioning with strong trend relevance and clean buyer intent.",
        f"Suitable for {product.lower()} launches, seasonal tests, and quick iteration.",
        f"Use this draft as a base and refine keywords, compliance, and image style before publishing."
    ]

def description(term: str, product: str, style: str) -> str:
    base = title_case(term)
    return (
        f"This listing draft is generated for the trend term '{base}'. "
        f"It is positioned as a {product.lower()} with a {style} direction, "
        f"intended for rapid POD validation. Before publishing, review trademark, "
        f"event-name, and platform policy risk, then adjust keywords and artwork."
    )

def tags(term: str, product: str):
    parts = [p for p in re.split(r"[^a-zA-Z0-9]+", term.lower()) if p]
    seed = parts[:5]
    prod = product.lower().replace(" ", "")
    extra = ["pod", "gift", prod]
    tags = []
    for t in seed + extra:
        if t and t not in tags:
            tags.append(t[:20])
    return tags[:10]

def design_prompt(term: str, style: str, product: str) -> str:
    return f"{style}, {term}, white background, print ready, POD design for {product.lower()}, clean composition"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT s.term, s.decision_level, s.design_direction
        FROM ai_trend_scorecards s
        ORDER BY s.trend_power_score DESC, s.id ASC
        LIMIT 120
    """).fetchall()

    conn.execute("DELETE FROM ai_listing_drafts")

    inserted = 0
    for r in rows:
        term = clean_term(r["term"])
        if not term:
            continue

        product = infer_product(term)
        style = infer_style(term)
        title = make_title(term, product)
        b = bullets(term, product, style)
        desc = description(term, product, style)
        tg = tags(term, product)
        prompt = design_prompt(term, style, product)

        payload = {
            "decision_level": r["decision_level"],
            "design_direction": r["design_direction"],
            "product": product,
            "style": style
        }

        conn.execute(
            """
            INSERT INTO ai_listing_drafts
            (term, platform, title, bullet_1, bullet_2, bullet_3, bullet_4, bullet_5,
             description, tags_json, design_prompt, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term, "amazon", title, b[0], b[1], b[2], b[3], b[4],
                desc, json.dumps(tg, ensure_ascii=False), prompt,
                json.dumps(payload, ensure_ascii=False), utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] ai_listing_engine_v54 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
