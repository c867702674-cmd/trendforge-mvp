
#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def make_title(term):
    return f"{term.title()} | POD Trend Launch Edition"

def make_bullets(term):
    return [
        f"Built around trend keyword: {term}",
        "Optimized for POD testing and rapid launch",
        "Suitable for shirts, mugs, hoodies, and posters",
        "Designed for ecommerce click-through and conversions",
        "Ready for seller review and publishing workflow",
    ]

def make_desc(term):
    return (
        f"This listing draft is generated from TrendForge opportunity data for '{term}'. "
        f"It is designed for quick POD deployment, niche testing, and marketplace validation."
    )

def make_tags(term):
    toks = [t.strip().lower() for t in term.split() if t.strip()]
    base = toks[:5]
    extra = ["pod trend", "gift idea", "launch test", "print on demand"]
    out = []
    for x in base + extra:
        if x not in out:
            out.append(x)
    return out[:10]

def make_prompt(term):
    return (
        f"POD product image mockup for '{term}', clean ecommerce style, white background, "
        f"high contrast, commercial layout, print-ready, thumbnail friendly"
    )

def main():
    conn = connect()
    rows = conn.execute("""
        SELECT term, opportunity_score
        FROM seller_opportunity_feed
        ORDER BY opportunity_score DESC
        LIMIT 100
    """).fetchall()

    conn.execute("DELETE FROM listing_auto_drafts")
    inserted = 0

    for r in rows:
        term = str(r["term"] or "").strip()
        score = float(r["opportunity_score"] or 0)
        title = make_title(term)
        bullets = make_bullets(term)
        desc = make_desc(term)
        tags = make_tags(term)
        prompt = make_prompt(term)

        conn.execute(
            """INSERT INTO listing_auto_drafts
            (term, listing_title, bullet_points_json, description, seo_tags_json, image_prompt, draft_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                term,
                title,
                json.dumps(bullets, ensure_ascii=False),
                desc,
                json.dumps(tags, ensure_ascii=False),
                prompt,
                score,
                json.dumps({"opportunity_score": score}, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] listing_auto_generator_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
