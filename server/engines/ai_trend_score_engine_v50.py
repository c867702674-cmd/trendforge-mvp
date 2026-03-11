#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))

def titleize(term):
    return " ".join([w.capitalize() for w in str(term).split()])

def design_direction(term):
    tl = str(term).lower()
    if "cat" in tl:
        return "minimal line cat + slogan / retro cat parody / cute giftable cat art"
    if "dog" in tl:
        return "cute dog illustration + meme typography + gift style layout"
    if "teacher" in tl:
        return "teacher appreciation gift + clean typography + school icon combo"
    if "nurse" in tl:
        return "night shift humor + medical icon + clean POD typography"
    if "retro" in tl:
        return "retro distressed typography + sunset palette + vintage badge"
    if "baseball" in tl or "sports" in tl:
        return "fan gift layout + bold typography + event-driven quick launch style"
    return "clean commercial POD style + typography + giftable niche direction"

def product_ideas(term):
    tl = str(term).lower()
    items = ["T-shirt", "Hoodie", "Mug"]
    if "gift" in tl:
        items = ["Mug", "Tote Bag", "T-shirt"]
    if "art" in tl or "line" in tl:
        items = ["Poster", "Mug", "T-shirt"]
    if "baseball" in tl or "sports" in tl:
        items = ["T-shirt", "Hoodie", "Sticker"]
    return items

def decision_level(score):
    if score >= 80:
        return "DO_NOW"
    if score >= 65:
        return "FAST_FOLLOW"
    if score >= 45:
        return "WATCH"
    return "AVOID"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
          COALESCE(p.term, r.term, c.term) AS term,
          COALESCE(p.profit_score, 0) AS profit_score_raw,
          COALESCE(r.rank_score, 0) AS rank_score_raw,
          COALESCE(c.opportunity_score, 0) AS opportunity_score_raw
        FROM pod_niche_profits p
        LEFT JOIN ai_trend_rankings r ON r.term = p.term
        LEFT JOIN opportunity_cards c ON c.term = p.term
        ORDER BY p.profit_score DESC, r.rank_score DESC
        LIMIT 150
    """).fetchall()

    conn.execute("DELETE FROM ai_trend_scorecards")

    inserted = 0
    for r in rows:
        term = str(r["term"] or "").strip()
        if not term:
            continue

        profit_raw = float(r["profit_score_raw"] or 0)
        rank_raw = float(r["rank_score_raw"] or 0)
        opp_raw = float(r["opportunity_score_raw"] or 0)

        profit_score = clamp(round(profit_raw / 800.0, 2))
        competition_score = clamp(round(100 - (rank_raw / 1200.0), 2))
        design_difficulty = clamp(35 if len(term.split()) <= 3 else 55)
        viral_probability = clamp(round((opp_raw / 900.0) + (rank_raw / 2500.0), 2))
        trend_power_score = clamp(round(
            profit_score * 0.38 +
            competition_score * 0.18 +
            (100 - design_difficulty) * 0.12 +
            viral_probability * 0.32
        , 2))

        lvl = decision_level(trend_power_score)
        direction = design_direction(term)
        ideas = product_ideas(term)

        payload = {
            "term": term,
            "profit_score_raw": profit_raw,
            "rank_score_raw": rank_raw,
            "opportunity_score_raw": opp_raw
        }

        conn.execute(
            """
            INSERT INTO ai_trend_scorecards
            (term, trend_power_score, profit_score, competition_score, design_difficulty,
             viral_probability, decision_level, design_direction, product_ideas_json, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                trend_power_score,
                profit_score,
                competition_score,
                design_difficulty,
                viral_probability,
                lvl,
                direction,
                json.dumps(ideas, ensure_ascii=False),
                json.dumps(payload, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] ai_trend_score_engine_v50 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
