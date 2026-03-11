#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def table_exists(conn, name):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,)
    ).fetchone()
    return row is not None

def main():
    conn = connect()

    if not table_exists(conn, "ai_trend_brain"):
        print("[WARN] ai_trend_brain table missing. Skip ranking.")
        conn.close()
        return

    if not table_exists(conn, "niche_opportunities"):
        print("[WARN] niche_opportunities table missing. Skip ranking.")
        conn.close()
        return

    board_exists = table_exists(conn, "ai_opportunity_board")
    global_exists = table_exists(conn, "global_trend_signals")

    rows = conn.execute("""
        SELECT
            t.id AS trend_id,
            t.term,
            COALESCE(b.brain_score, 0) AS brain_score,
            COALESCE(n.niche_score, 0) AS niche_score,
            COALESCE(o.final_score, 0) AS board_score
        FROM trends t
        LEFT JOIN ai_trend_brain b ON b.trend_id = t.id
        LEFT JOIN niche_opportunities n ON n.trend_id = t.id
        LEFT JOIN ai_opportunity_board o ON o.trend_id = t.id
        ORDER BY b.brain_score DESC, t.id ASC
        LIMIT 200
    """).fetchall() if board_exists else conn.execute("""
        SELECT
            t.id AS trend_id,
            t.term,
            COALESCE(b.brain_score, 0) AS brain_score,
            COALESCE(n.niche_score, 0) AS niche_score,
            0 AS board_score
        FROM trends t
        LEFT JOIN ai_trend_brain b ON b.trend_id = t.id
        LEFT JOIN niche_opportunities n ON n.trend_id = t.id
        ORDER BY b.brain_score DESC, t.id ASC
        LIMIT 200
    """).fetchall()

    conn.execute("DELETE FROM ai_trend_rankings")

    inserted = 0
    for r in rows:
        term = str(r["term"] or "")
        source_count = 0
        if global_exists:
            sc = conn.execute(
                "SELECT COUNT(DISTINCT source) AS c FROM global_trend_signals WHERE term=?",
                (term,)
            ).fetchone()
            source_count = float(sc["c"] or 0) if sc else 0

        brain = float(r["brain_score"] or 0)
        niche = float(r["niche_score"] or 0)
        board = float(r["board_score"] or 0)

        rank_score = round(brain * 0.4 + niche * 0.25 + board * 0.25 + source_count * 8.0, 2)

        conn.execute(
            """INSERT INTO ai_trend_rankings
            (trend_id, term, brain_score, niche_score, board_score, source_count, rank_score, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                int(r["trend_id"]),
                term,
                brain,
                niche,
                board,
                source_count,
                rank_score,
                json.dumps({
                    "brain_score": brain,
                    "niche_score": niche,
                    "board_score": board,
                    "source_count": source_count
                }, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] ai_trend_ranking_engine_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
