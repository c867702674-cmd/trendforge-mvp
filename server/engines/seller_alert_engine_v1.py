#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def level_of(score):
    if score >= 1500:
        return "HOT"
    if score >= 800:
        return "DO_NOW"
    if score >= 300:
        return "WATCH"
    return "LOW"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, card_title, card_subtitle, opportunity_score, design_direction, recommended_title
        FROM opportunity_cards
        ORDER BY opportunity_score DESC, id ASC
        LIMIT 100
        """
    ).fetchall()

    conn.execute("DELETE FROM seller_alerts")
    inserted = 0

    for r in rows:
        term = str(r["term"] or "").strip()
        score = float(r["opportunity_score"] or 0)
        level = level_of(score)
        title = f"[{level}] {term}"
        text = f"{r['card_subtitle'] or ''} | 推荐设计: {r['design_direction'] or '-'} | 推荐标题: {r['recommended_title'] or '-'}"

        conn.execute(
            """
            INSERT INTO seller_alerts
            (term, alert_level, alert_title, alert_text, alert_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                level,
                title,
                text,
                score,
                json.dumps({
                    "card_title": r["card_title"],
                    "card_subtitle": r["card_subtitle"],
                    "design_direction": r["design_direction"],
                    "recommended_title": r["recommended_title"]
                }, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] seller_alert_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
