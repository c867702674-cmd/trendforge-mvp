#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import sqlite3
from datetime import datetime

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_IN = "risk_ip_scan_results_v58"
TABLE_OUT = "listing_candidates_v59"

PRODUCT_TYPES = [
    "shirt", "hoodie", "sweatshirt", "mug", "poster", "tote", "sticker"
]

STYLE_WORDS = [
    "minimalist", "retro", "vintage", "line art", "boho",
    "cute", "funny", "distressed", "bold", "graphic"
]

AUDIENCE_WORDS = [
    "mom", "dad", "kids", "women", "men", "teacher",
    "nurse", "coach", "family", "friends"
]

def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def title_case(text: str) -> str:
    return " ".join(x.capitalize() for x in clean_spaces(text).split())

def detect_product_type(text: str) -> str:
    t = (text or "").lower()
    for p in PRODUCT_TYPES:
        if re.search(rf"\b{re.escape(p)}\b", t):
            return p
    return "shirt"

def remove_product_type(text: str) -> str:
    t = clean_spaces(text.lower())
    for p in PRODUCT_TYPES:
        t = re.sub(rf"\b{re.escape(p)}\b", "", t)
    return clean_spaces(t)

def detect_style_hint(text: str) -> str:
    t = (text or "").lower()
    hits = [w for w in STYLE_WORDS if w in t]
    if hits:
        return ", ".join(hits[:2])
    if "winter" in t:
        return "minimalist, sporty"
    if "city" in t or "state" in t or "hometown" in t:
        return "retro, vintage"
    return "minimalist, clean"

def detect_audience_hint(text: str) -> str:
    t = (text or "").lower()
    hits = [w for w in AUDIENCE_WORDS if re.search(rf"\b{re.escape(w)}\b", t)]
    return ", ".join(hits[:2]) if hits else "general"

def make_title(core: str, product_type: str) -> str:
    core_tc = title_case(core)
    if product_type == "shirt":
        return f"{core_tc} Shirt, Minimalist POD Graphic Tee"
    if product_type == "hoodie":
        return f"{core_tc} Hoodie, Cozy POD Graphic Sweatshirt"
    if product_type == "sweatshirt":
        return f"{core_tc} Sweatshirt, Casual POD Graphic Top"
    if product_type == "mug":
        return f"{core_tc} Mug, Giftable POD Coffee Cup"
    if product_type == "poster":
        return f"{core_tc} Poster, Printable Wall Art Decor"
    if product_type == "tote":
        return f"{core_tc} Tote Bag, Everyday POD Carryall"
    if product_type == "sticker":
        return f"{core_tc} Sticker, Cute Waterproof Decal"
    return f"{core_tc} {title_case(product_type)}"

def make_tags(core: str, product_type: str, style_hint: str, audience_hint: str) -> str:
    tags = []
    core_words = [w for w in core.lower().split() if w]
    tags.extend(core_words[:5])
    tags.append(product_type)
    tags.extend([x.strip() for x in style_hint.split(",") if x.strip()])
    if audience_hint and audience_hint != "general":
        tags.extend([x.strip() for x in audience_hint.split(",") if x.strip()])
    tags.extend(["pod", "gift idea", "trending design"])
    seen = []
    for t in tags:
        t = clean_spaces(t.lower())
        if t and t not in seen:
            seen.append(t)
    return ", ".join(seen[:13])

def make_bullets(core: str, product_type: str, style_hint: str, audience_hint: str) -> str:
    bullets = [
        f"Theme: {title_case(core)}",
        f"Product: {title_case(product_type)}",
        f"Style: {style_hint}",
        f"Audience: {audience_hint}",
        "Use for POD listing draft, then manually review trademark and marketplace policy.",
    ]
    return "\n".join(f"- {b}" for b in bullets)

def make_description(core: str, product_type: str, style_hint: str, audience_hint: str) -> str:
    core_tc = title_case(core)
    base = (
        f"This {product_type} listing draft is built around the theme '{core_tc}'. "
        f"It is positioned as a {style_hint} design concept for POD sellers. "
        f"The target audience is {audience_hint}. "
        "Use this as a marketplace-ready draft foundation, then manually refine sizing, materials, production details, "
        "and compliance checks before publishing."
    )
    return base

def make_prompt(core: str, product_type: str, style_hint: str) -> str:
    return (
        f"{core}, {product_type} design, {style_hint}, clean composition, commercial POD style, "
        "centered artwork, high contrast, print-ready, no mockup, transparent background"
    )

def make_sku(core: str, product_type: str, idx: int) -> str:
    raw = re.sub(r"[^a-z0-9]+", "-", core.lower()).strip("-")
    raw = raw[:24]
    return f"TF-V59-{product_type[:3].upper()}-{raw.upper()}-{idx:04d}"

def calc_listing_score(risk_level: str, safe_term: str, source_score: float) -> float:
    score = float(source_score or 0)
    length_bonus = min(len(safe_term.split()) * 2, 12)
    risk_penalty = 0 if risk_level == "SAFE" else 15
    return round(score + length_bonus - risk_penalty, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(f"""
        SELECT
            source_term,
            candidate_term,
            safe_term,
            risk_level,
            source_score,
            source_payload_json
        FROM {TABLE_IN}
        WHERE risk_level IN ('SAFE', 'REVIEW')
        ORDER BY
            CASE risk_level WHEN 'SAFE' THEN 1 ELSE 2 END,
            source_score DESC,
            id DESC
        LIMIT 200
    """).fetchall()

    conn.execute(f"DELETE FROM {TABLE_OUT}")

    inserted = 0
    for idx, r in enumerate(rows, start=1):
        safe_term = clean_spaces(r["safe_term"] or r["candidate_term"] or "")
        if not safe_term:
            continue

        product_type = detect_product_type(safe_term)
        core = remove_product_type(safe_term)
        if not core:
            core = safe_term

        style_hint = detect_style_hint(safe_term)
        audience_hint = detect_audience_hint(safe_term)

        title_en = make_title(core, product_type)
        tags_en = make_tags(core, product_type, style_hint, audience_hint)
        bullets_en = make_bullets(core, product_type, style_hint, audience_hint)
        description_en = make_description(core, product_type, style_hint, audience_hint)
        design_prompt_en = make_prompt(core, product_type, style_hint)
        sku_code = make_sku(core, product_type, idx)
        listing_score = calc_listing_score(r["risk_level"], safe_term, r["source_score"] or 0)

        conn.execute(f"""
            INSERT INTO {TABLE_OUT} (
                source_term,
                candidate_term,
                safe_term,
                risk_level,
                product_type,
                style_hint,
                audience_hint,
                title_en,
                tags_en,
                bullets_en,
                description_en,
                design_prompt_en,
                sku_code,
                listing_score,
                source_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["source_term"],
            r["candidate_term"],
            safe_term,
            r["risk_level"],
            product_type,
            style_hint,
            audience_hint,
            title_en,
            tags_en,
            bullets_en,
            description_en,
            design_prompt_en,
            sku_code,
            listing_score,
            r["source_payload_json"],
        ))
        inserted += 1

    conn.commit()
    conn.close()

    print(f"[OK] listing_generator_v59 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
