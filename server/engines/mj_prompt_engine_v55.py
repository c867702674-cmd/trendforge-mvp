#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def choose_style(term: str, title: str) -> str:
    t = f"{term} {title}".lower()
    if "retro" in t or "vintage" in t:
        return "retro vintage distressed poster style"
    if "cat" in t or "dog" in t:
        return "cute commercial character illustration"
    if "teacher" in t or "nurse" in t:
        return "clean appreciation typography with icons"
    if "baseball" in t or "sports" in t:
        return "bold fan graphic with event energy"
    if "minimal" in t or "line" in t:
        return "minimal clean line art"
    return "clean commercial POD typography illustration"

def choose_ratio(term: str, product: str) -> str:
    x = f"{term} {product}".lower()
    if "poster" in x:
        return "2:3"
    if "mug" in x:
        return "3:2"
    return "1:1"

def choose_sku_hint(title: str, tags) -> str:
    x = f"{title} {' '.join(tags)}".lower()
    if "mug" in x:
        return "mug"
    if "hoodie" in x:
        return "hoodie"
    if "poster" in x:
        return "poster"
    if "sticker" in x:
        return "sticker"
    return "tshirt"

def build_prompts(term: str, style: str, sku_hint: str, title: str):
    core_subject = f"{term}, {style}, POD design for {sku_hint}"
    mj = (
        f"{core_subject}, clean composition, centered layout, white background, "
        f"print ready, commercial giftable style, crisp vector feeling, high contrast details"
    )
    sdxl = (
        f"{core_subject}, clean centered composition, isolated on white background, "
        f"professional POD artwork, readable typography balance, polished commercial design"
    )
    negative = "low quality, blurry, watermark, mockup, extra fingers, background clutter, photo frame, 3d render"
    subject = title if title else term
    return subject, mj, sdxl, negative

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT a.term, a.platform, a.title, a.tags_json
        FROM ai_listing_drafts a
        ORDER BY a.id ASC
        LIMIT 120
        """
    ).fetchall()

    conn.execute("DELETE FROM mj_prompt_drafts_v55")
    inserted = 0

    for r in rows:
        term = str(r["term"] or "").strip()
        if not term:
            continue
        try:
            tags = json.loads(r["tags_json"] or "[]")
        except Exception:
            tags = []

        title = str(r["title"] or "").strip()
        style = choose_style(term, title)
        sku_hint = choose_sku_hint(title, tags)
        aspect = choose_ratio(term, sku_hint)
        subject, mj, sdxl, negative = build_prompts(term, style, sku_hint, title)
        mj = f"{mj} --ar {aspect}"

        payload = {"title": title, "tags": tags}

        conn.execute(
            """
            INSERT INTO mj_prompt_drafts_v55
            (term, platform, style_name, subject_line, mj_prompt, sdxl_prompt, negative_prompt,
             aspect_ratio, sku_hint, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                r["platform"] or "amazon",
                style,
                subject,
                mj,
                sdxl,
                negative,
                aspect,
                sku_hint,
                json.dumps(payload, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] mj_prompt_engine_v55 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
