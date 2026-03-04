#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timezone
import random

DB_PATH="/root/trendforge-mvp/server/trendforge.db"

STYLE_TEMPLATES=[
"minimalist {idea}, vintage color palette, bold retro typography, vector tshirt design, transparent background",
"retro style {idea}, sunset gradient colors, distressed texture, vintage tshirt graphic, transparent background",
"clean line art {idea}, minimal design, bold outline, vector illustration, tshirt print ready",
"vintage badge style {idea}, retro color palette, bold typography, vector graphic, transparent background",
"minimal typography {idea}, modern retro font, vector tshirt design, print ready"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def fetch_design_ideas(conn):

    sql="""
    SELECT id,idea
    FROM design_ideas
    ORDER BY id DESC
    LIMIT 100
    """

    return conn.execute(sql).fetchall()

def prompt_exists(conn,idea_id):

    r=conn.execute(
        "SELECT id FROM design_prompts WHERE idea_id=? LIMIT 1",
        (idea_id,)
    ).fetchone()

    return r is not None

def generate_prompt(idea):

    template=random.choice(STYLE_TEMPLATES)

    return template.replace("{idea}",idea)

def insert_prompt(conn,idea_id,prompt):

    conn.execute(
        """
        INSERT INTO design_prompts(
            idea_id,
            prompt,
            created_at
        )
        VALUES(?,?,?)
        """,
        (
            idea_id,
            prompt,
            now()
        )
    )

def main():

    conn=connect()

    ideas=fetch_design_ideas(conn)

    total=0

    for i in ideas:

        idea_id=i["id"]

        idea=i["idea"]

        if prompt_exists(conn,idea_id):
            continue

        prompt=generate_prompt(idea)

        insert_prompt(conn,idea_id,prompt)

        total+=1

        print(f"[PROMPT] {prompt}")

    conn.commit()

    print(f"[DONE] prompts_generated={total}")

if __name__=="__main__":
    main()
