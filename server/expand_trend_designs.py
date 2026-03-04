#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timezone
import random

DB_PATH="/root/trendforge-mvp/server/trendforge.db"

TEMPLATES=[
"{trend} shirt",
"{trend} hoodie",
"{trend} vintage shirt",
"{trend} retro shirt",
"{trend} typography shirt",
"{trend} line art shirt",
"{trend} sunset shirt",
"{trend} dad shirt",
"{trend} mom shirt",
"{trend} gift shirt",
"{trend} retro sunset",
"{trend} vintage typography",
"{trend} minimal line art",
"{trend} retro logo",
"{trend} vintage logo",
"{trend} club logo",
"{trend} badge design",
"{trend} graphic tee",
"{trend} retro badge",
"{trend} vintage patch"
]


def now():

    return datetime.now(timezone.utc).isoformat()


def connect():

    conn=sqlite3.connect(DB_PATH)

    conn.row_factory=sqlite3.Row

    return conn


def fetch_trends(conn):

    sql="""
    SELECT id,term
    FROM trends
    WHERE action_level IN ('DO_NOW','DOING')
    ORDER BY hit_score DESC
    LIMIT 20
    """

    return conn.execute(sql).fetchall()


def idea_exists(conn,trend_id,idea):

    r=conn.execute(
        "SELECT id FROM design_ideas WHERE trend_id=? AND idea=?",
        (trend_id,idea)
    ).fetchone()

    return r is not None


def generate_ideas(term):

    ideas=[]

    for t in TEMPLATES:

        ideas.append(t.replace("{trend}",term))

    return ideas


def insert_idea(conn,trend_id,idea):

    conn.execute(
        """
        INSERT INTO design_ideas(
            trend_id,
            idea,
            created_at
        )
        VALUES(?,?,?)
        """,
        (trend_id,idea,now())
    )


def main():

    conn=connect()

    trends=fetch_trends(conn)

    total=0

    for t in trends:

        trend_id=t["id"]

        term=t["term"]

        ideas=generate_ideas(term)

        for idea in ideas:

            if idea_exists(conn,trend_id,idea):

                continue

            insert_idea(conn,trend_id,idea)

            total+=1

            print(
                f"[IDEA] {idea}"
            )

    conn.commit()

    print(
        f"[DONE] generated={total}"
    )


if __name__=="__main__":

    main()