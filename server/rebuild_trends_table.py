#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "trendforge.db")


def utc_date():
    return datetime.utcnow().strftime("%Y-%m-%d")


def utc_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        country TEXT DEFAULT 'US',
        category TEXT DEFAULT 'POD',
        term TEXT,
        growth REAL DEFAULT 0,
        hit_score REAL DEFAULT 0,
        feedback_boost_score REAL DEFAULT 0,
        action_level TEXT,
        payload_json TEXT
    );
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_trends_term ON trends(term);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trends_date ON trends(date);")

    conn.commit()


def seed_mock(conn):

    items = [
        ("retro golf typography",520,"DO_NOW"),
        ("minimalist line art cat",320,"DO_NOW"),
        ("funny cat meme",228,"DO_NOW"),
        ("costco gift card recall",1300,"WATCH"),
        ("kate middleton bafta outfit",1050,"WATCH"),
    ]

    for term,score,level in items:

        payload = {
            "term":term,
            "score":score,
            "growth":score,
            "source":"rebuild_seed",
            "updated_at":utc_iso()
        }

        conn.execute(
            """
            INSERT INTO trends
            (date,country,category,term,growth,hit_score,feedback_boost_score,action_level,payload_json)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                utc_date(),
                "US",
                "POD",
                term,
                float(score),
                float(score),
                0,
                level,
                json.dumps(payload)
            )
        )

    conn.commit()


def main():

    conn = sqlite3.connect(DB_PATH)

    ensure_table(conn)

    cnt = conn.execute("select count(*) from trends").fetchone()[0]

    if cnt > 0:
        print("trends already exists rows=",cnt)
        return

    seed_mock(conn)

    cnt = conn.execute("select count(*) from trends").fetchone()[0]

    print("trends rebuilt rows=",cnt)


if __name__ == "__main__":
    main()