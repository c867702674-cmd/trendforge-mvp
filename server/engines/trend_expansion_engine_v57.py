#!/usr/bin/env python3
import os, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

PREFIXES = [
    "minimalist",
    "retro",
    "vintage",
    "cute",
    "funny",
    "gift",
    "graphic"
]

SUFFIXES = [
    "shirt",
    "hoodie",
    "mug",
    "poster",
    "sticker",
    "svg"
]

def utc():
    return datetime.now(timezone.utc).isoformat()

def score_term(prefix, base, suffix):
    score = 50.0
    if prefix in ("retro", "minimalist", "gift"):
        score += 10
    if suffix in ("shirt", "mug", "poster"):
        score += 12
    if len(base.split()) <= 4:
        score += 8
    return round(score, 2)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT DISTINCT term FROM ai_trend_scorecards ORDER BY trend_power_score DESC LIMIT 80"
    ).fetchall()

    conn.execute("DELETE FROM trend_expansion_v57")
    inserted = 0

    for r in rows:
        base_term = str(r["term"] or "").strip()
        if not base_term:
            continue

        for p in PREFIXES:
            for s in SUFFIXES:
                expanded = f"{p} {base_term} {s}".strip()
                sc = score_term(p, base_term, s)
                conn.execute(
                    """
                    INSERT INTO trend_expansion_v57
                    (base_term, expanded_term, expansion_type, score, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (base_term, expanded, "prefix_suffix", sc, utc())
                )
                inserted += 1

    conn.commit()
    print(f"[OK] trend_expansion_engine_v57 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
