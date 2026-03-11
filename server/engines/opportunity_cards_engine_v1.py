#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def titleize(term):
    return " ".join([w.capitalize() for w in str(term).split()])

def make_direction(term):
    tl = str(term).lower()
    if "cat" in tl:
        return "Minimal line art cat + playful slogan"
    if "dog" in tl:
        return "Cute pet illustration + giftable layout"
    if "teacher" in tl:
        return "Teacher appreciation gift style"
    if "nurse" in tl:
        return "Night shift humor + clean typography"
    if "retro" in tl:
        return "Retro distressed typography"
    return "Clean POD commercial style"

def make_products(term):
    tl = str(term).lower()
    products = ["T-shirt", "Hoodie", "Mug"]
    if "decor" in tl or "poster" in tl:
        products = ["Poster", "Canvas", "Mug"]
    if "gift" in tl:
        products = ["Mug", "Tote Bag", "T-shirt"]
    return products

def make_listing_title(term):
    t = titleize(term)
    return f"{t} Gift Idea | POD Trend Launch"

def make_prompt(term):
    return f"POD product mockup for '{term}', commercial ecommerce style, clean background, high contrast, thumbnail friendly, print-ready"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT p.term,
               COALESCE(p.profit_score,0) AS profit_score,
               COALESCE(r.rank_score,0) AS rank_score
        FROM pod_niche_profits p
        LEFT JOIN ai_trend_rankings r ON r.term = p.term
        ORDER BY p.profit_score DESC, r.rank_score DESC
        LIMIT 100
        """
    ).fetchall()

    conn.execute("DELETE FROM opportunity_cards")
    inserted = 0

    for r in rows:
        term = str(r["term"] or "").strip()
        opp = round(float(r["profit_score"] or 0) * 0.6 + float(r["rank_score"] or 0) * 0.4, 2)
        card_title = f"🔥 {titleize(term)}"
        card_subtitle = f"DO_NOW 爆款机会 · Score {opp}"
        direction = make_direction(term)
        products = make_products(term)
        rec_title = make_listing_title(term)
        image_prompt = make_prompt(term)

        payload = {
            "term": term,
            "profit_score": float(r["profit_score"] or 0),
            "rank_score": float(r["rank_score"] or 0)
        }

        conn.execute(
            """
            INSERT INTO opportunity_cards
            (term, card_title, card_subtitle, opportunity_score, design_direction,
             recommended_products_json, recommended_title, image_prompt, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                card_title,
                card_subtitle,
                opp,
                direction,
                json.dumps(products, ensure_ascii=False),
                rec_title,
                image_prompt,
                json.dumps(payload, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] opportunity_cards_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
