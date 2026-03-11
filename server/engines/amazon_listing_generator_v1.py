#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
SEARCH_TERMS_LIMIT = int(os.getenv("AMAZON_SEARCH_TERMS_LIMIT", "180"))

def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_columns(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts);").fetchall()]
    for col, ddl in [
        ("amazon_title", "ALTER TABLE listing_drafts ADD COLUMN amazon_title TEXT"),
        ("amazon_bullets_json", "ALTER TABLE listing_drafts ADD COLUMN amazon_bullets_json TEXT"),
        ("amazon_description", "ALTER TABLE listing_drafts ADD COLUMN amazon_description TEXT"),
        ("amazon_search_terms", "ALTER TABLE listing_drafts ADD COLUMN amazon_search_terms TEXT"),
    ]:
        if col not in cols:
            conn.execute(ddl)
    conn.commit()

def build_amazon_title(base_title, product, term):
    title = f"{base_title} {product} Trend Gift".strip()
    return title[:180]

def build_bullets(term, product, tags):
    return [
        f"Built from the POD trend '{term}' for fast Amazon listing execution.",
        f"Ideal for {product} shoppers looking for trend-driven graphic products.",
        "Structured for quick testing in Merch, POD, and related marketplaces.",
        "Includes niche and keyword context for stronger listing positioning.",
        f"Can be adapted into multiple variations for {product} and seasonal launches.",
    ]

def build_description(term, product, title):
    return (
        f"This Amazon listing draft is based on the trend '{term}'. "
        f"It is designed for POD sellers who want to move quickly from trend discovery to publish-ready execution. "
        f"Use '{title}' as a starting point for testing {product} variations and validating buyer intent."
    )

def build_search_terms(term, tags):
    parts = [term] + list(tags)
    seen, out = set(), []
    for p in parts:
        p = str(p).strip().lower()
        if p and p not in seen:
            seen.add(p); out.append(p)
    txt = " ".join(out)
    return txt[:SEARCH_TERMS_LIMIT]

def main():
    conn = connect(); ensure_columns(conn)
    rows = conn.execute("""
        SELECT id, title, tags_json, payload_json
        FROM listing_drafts
        ORDER BY id ASC
    """).fetchall()
    updated = 0
    for r in rows:
        try:
            tags = json.loads(r["tags_json"] or "[]")
        except Exception:
            tags = []
        try:
            payload = json.loads(r["payload_json"] or "{}")
        except Exception:
            payload = {}
        term = str(payload.get("term") or "")
        product = str(payload.get("product_type") or "product")
        base_title = str(r["title"] or "")
        amz_title = build_amazon_title(base_title, product, term)
        bullets = build_bullets(term, product, tags if isinstance(tags, list) else [])
        desc = build_description(term, product, amz_title)
        search_terms = build_search_terms(term, tags if isinstance(tags, list) else [])
        conn.execute("""UPDATE listing_drafts
                        SET amazon_title=?, amazon_bullets_json=?, amazon_description=?, amazon_search_terms=?
                        WHERE id=?""",
                     (amz_title, json.dumps(bullets, ensure_ascii=False), desc, search_terms, int(r["id"])))
        updated += 1
    conn.commit()
    print(f"[OK] amazon_listing_generator_v1 updated={updated} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
