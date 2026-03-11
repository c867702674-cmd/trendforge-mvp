#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import os
import json
import math
import sqlite3
from datetime import datetime, timezone

# =========================
# 强制使用主数据库路径
# =========================
DB_PATH = "/root/trendforge-mvp/server/trendforge.db"


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def log(level, msg):
    print(f"[{level}] {msg}", flush=True)


def build_one(conn, date, country, category):

    rows = conn.execute(
        """
        SELECT term,
               MAX(COALESCE(score,0)) AS max_score,
               COUNT(DISTINCT source) AS src_cnt
        FROM raw_trends
        WHERE date=? AND country=?
        GROUP BY term
        ORDER BY max_score DESC
        """,
        (date, country),
    ).fetchall()

    inserted = 0

    for term, max_score, src_cnt in rows:

        hit = float(max_score or 0)

        if src_cnt > 1:
            hit += (src_cnt - 1) * 30

        hit += math.log1p(hit)

        if hit > 500:
            level = "DO_NOW"
        elif hit > 200:
            level = "WATCH"
        else:
            level = "IGNORE"

        payload = {
            "date": date,
            "country": country,
            "category": category,
            "max_score": max_score,
            "src_cnt": src_cnt,
        }

        conn.execute(
            """
            INSERT INTO trends
            (date,country,category,term,hit_score,action_level,source,created_at,payload_json)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(date,country,category,term) DO UPDATE SET
            hit_score=excluded.hit_score,
            action_level=excluded.action_level,
            payload_json=excluded.payload_json
            """,
            (
                date,
                country,
                category,
                term,
                hit,
                level,
                "raw_trends",
                utc_now_iso(),
                json.dumps(payload),
            ),
        )

        inserted += 1

    conn.commit()

    return inserted, len(rows)


def main():

    date = os.getenv("DATE") or today()
    country = os.getenv("COUNTRY", "US")
    category = os.getenv("CATEGORY", "POD")

    log("INFO", f"db={DB_PATH}")
    log("INFO", f"build_trends_from_raw date={date} country={country} category={category}")

    conn = sqlite3.connect(DB_PATH)

    inserted, grouped = build_one(conn, date, country, category)

    log("OK", f"build_trends_from_raw date={date} inserted={inserted} grouped={grouped}")

    conn.close()


if __name__ == "__main__":
    main()