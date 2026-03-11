#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def audience_for(score):
    if score >= 1500:
        return "group_main,group_vip"
    if score >= 800:
        return "group_vip"
    return "group_main"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT e.term, e.pack_title, e.pack_score, e.task_list_json, e.listing_title, s.alert_level
        FROM execution_pack_distributions e
        LEFT JOIN seller_alerts s ON s.term = e.term
        ORDER BY e.pack_score DESC, e.id ASC
        LIMIT 100
        """
    ).fetchall()

    conn.execute("DELETE FROM push_ready_payloads")
    inserted = 0

    for r in rows:
        term = str(r["term"] or "").strip()
        score = float(r["pack_score"] or 0)
        body = {
            "pack_title": r["pack_title"] or "",
            "listing_title": r["listing_title"] or "",
            "task_list_json": json.loads(r["task_list_json"] or "[]"),
            "alert_level": r["alert_level"] or "WATCH"
        }
        conn.execute(
            """
            INSERT INTO push_ready_payloads
            (term, payload_type, priority_score, audience, title, body_json, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                "execution_pack",
                score,
                audience_for(score),
                f"Push Ready · {term}",
                json.dumps(body, ensure_ascii=False),
                json.dumps({"source":"execution_pack_distributions","score":score}, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] push_ready_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
