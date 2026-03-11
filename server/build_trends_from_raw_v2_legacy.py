#!/usr/bin/env python3
# TrendForge Growth Engine v2

import sqlite3
import json
import argparse
from datetime import datetime, timedelta, timezone

DB_PATH = "/root/trendforge-mvp/server/trendforge.db"

# POD关键词
POD_KEYWORDS = [
    "shirt","tshirt","tee","hoodie",
    "retro","vintage","typography",
    "line art","minimal","dog","cat",
    "golf","pickleball","camping",
    "sunset","mom","dad"
]

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def today_date():
    return datetime.now(timezone.utc).date().isoformat()


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_pod_term(term):

    t = term.lower()

    for k in POD_KEYWORDS:
        if k in t:
            return True

    return False


def fetch_terms(conn, source, country, since):

    sql = """
    SELECT
        term,
        COUNT(*) as captures,
        MAX(value) as max_value
    FROM raw_events
    WHERE source=? AND country=? AND captured_at>=?
    GROUP BY term
    """

    rows = conn.execute(sql,(source,country,since)).fetchall()

    return rows


def compute_growth(captures):

    # 简化版 growth
    if captures <=1:
        return 0

    return captures * 0.5


def compute_score(max_value,captures,growth):

    return int(
        max_value * 0.4 +
        captures * 10 +
        growth * 50
    )


def action_level(score):

    if score >=120:
        return "DO_NOW"

    if score >=80:
        return "DOING"

    if score >=40:
        return "WATCH"

    return "IGNORE"


def upsert_trend(conn,term,hit,level,payload):

    now = now_iso()
    today = today_date()

    row = conn.execute(
        "SELECT id FROM trends WHERE term=? LIMIT 1",
        (term,)
    ).fetchone()

    if row:

        conn.execute("""
        UPDATE trends
        SET
            hit_score=?,
            action_level=?,
            payload_json=?,
            updated_at=?
        WHERE id=?
        """,
        (hit,level,json.dumps(payload),now,row["id"]))

        return "UPDATE"

    conn.execute("""
    INSERT INTO trends(
        date,
        created_at,
        updated_at,
        term,
        country,
        category,
        hit_score,
        action_level,
        payload_json
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,
    (
        today,
        now,
        now,
        term,
        "US",
        "POD",
        hit,
        level,
        json.dumps(payload)
    ))

    return "INSERT"



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--days",type=int,default=7)
    parser.add_argument("--source",default="gtrends")
    parser.add_argument("--country",default="US")
    parser.add_argument("--limit",type=int,default=200)
    parser.add_argument("--dry-run",type=int,default=1)

    args = parser.parse_args()

    since = (
        datetime.now(timezone.utc)
        - timedelta(days=args.days)
    ).isoformat()

    conn = connect()

    rows = fetch_terms(
        conn,
        args.source,
        args.country,
        since
    )

    inserted=0
    updated=0
    ignored=0

    for r in rows:

        term=r["term"]

        if not is_pod_term(term):

            ignored+=1
            continue

        captures=r["captures"]
        max_value=r["max_value"] or 0

        growth=compute_growth(captures)

        score=compute_score(max_value,captures,growth)

        level=action_level(score)

        if level=="IGNORE":

            ignored+=1
            continue

        payload={
            "source":args.source,
            "captures":captures,
            "max_value":max_value,
            "growth":growth
        }

        if args.dry_run:

            print(
                f"[DRY] {term} "
                f"hit={score} "
                f"lvl={level} "
                f"captures={captures}"
            )

            continue

        mode=upsert_trend(
            conn,
            term,
            score,
            level,
            payload
        )

        if mode=="INSERT":
            inserted+=1
        else:
            updated+=1


    if not args.dry_run:
        conn.commit()

    print(
        f"[DONE] inserted={inserted} "
        f"updated={updated} "
        f"ignored={ignored}"
    )


if __name__=="__main__":
    main()