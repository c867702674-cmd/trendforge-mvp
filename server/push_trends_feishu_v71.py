
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
import requests

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
RAW_WEBHOOKS = os.getenv("FEISHU_WEBHOOKS_JSON", "{}")

def load_webhooks():
    return json.loads(RAW_WEBHOOKS)

def fetch_trends(conn):
    cur = conn.cursor()
    cur.execute("""
    SELECT id, term, hit_score
    FROM trends
    WHERE action_level='DO_NOW'
    ORDER BY hit_score DESC
    LIMIT 5
    """)
    return cur.fetchall()

def fetch_design_ideas(conn, trend_id):
    cur = conn.cursor()
    cur.execute("""
    SELECT idea
    FROM design_ideas
    WHERE trend_id=?
    LIMIT 5
    """, (trend_id,))
    return [r[0] for r in cur.fetchall()]

def fetch_prompts(conn, trend_id):
    cur = conn.cursor()
    cur.execute("""
    SELECT prompt
    FROM design_prompts
    WHERE idea_id IN (
        SELECT id FROM design_ideas WHERE trend_id=? LIMIT 5
    )
    LIMIT 2
    """, (trend_id,))
    return [r[0] for r in cur.fetchall()]

def build_card(term, score, ideas, prompts):
    idea_text = "\n".join([f"{i+1}. {x}" for i,x in enumerate(ideas)])
    prompt_text = "\n".join(prompts)

    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "elements": [
                {"tag":"div","text":{"tag":"lark_md","content":f"🔥 **Trend**\n{term}"}},
                {"tag":"div","text":{"tag":"lark_md","content":f"📈 **Score:** {score}"}},
                {"tag":"div","text":{"tag":"lark_md","content":f"🎨 **Design Ideas**\n{idea_text}"}},
                {"tag":"div","text":{"tag":"lark_md","content":f"🧠 **MJ Prompt**\n{prompt_text}"}},
            ]
        }
    }

def send(webhook, payload):
    requests.post(webhook, json=payload, timeout=10)

def main():
    conn = sqlite3.connect(DB_PATH)
    webhooks = load_webhooks()

    trends = fetch_trends(conn)

    for trend_id, term, score in trends:
        ideas = fetch_design_ideas(conn, trend_id)
        prompts = fetch_prompts(conn, trend_id)
        card = build_card(term, score, ideas, prompts)

        if "group_vip" in webhooks:
            send(webhooks["group_vip"], card)

    print("Feishu Push V7.1 done")

if __name__ == "__main__":
    main()
