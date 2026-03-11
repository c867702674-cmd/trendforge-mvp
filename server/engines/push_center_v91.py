#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, datetime

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

CHANNELS = [
    ("feishu_main", "Feishu Main"),
    ("feishu_vip", "Feishu VIP"),
    ("email_digest", "Email Digest"),
]

def choose_channel(action_level: str) -> str:
    if action_level == "DO_NOW":
        return "feishu_vip"
    if action_level == "WATCH":
        return "feishu_main"
    return "email_digest"

def push_title(term: str, action: str) -> str:
    return f"[{action}] {term}"

def push_body(term: str, product_type: str, action: str) -> str:
    return f"Trend: {term}\\nProduct: {product_type}\\nAction: {action}\\nUse this trend in TrendForge pipeline."

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM push_channels_v91")
    for code, name in CHANNELS:
        conn.execute(
            "INSERT INTO push_channels_v91 (channel_code, channel_name, is_enabled) VALUES (?, ?, 1)",
            (code, name),
        )

    conn.execute("DELETE FROM push_queue_v91")
    rows = conn.execute(
        '''
        SELECT id, source_term, action_level, product_type
        FROM trend_data_v89
        ORDER BY trend_score DESC, id DESC
        LIMIT 50
        '''
    ).fetchall()

    inserted = 0
    now = datetime.datetime.now()
    for idx, r in enumerate(rows, start=1):
        channel = choose_channel(r["action_level"])
        status = "QUEUED"
        scheduled_at = (now + datetime.timedelta(minutes=idx)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            '''
            INSERT INTO push_queue_v91
            (trend_id, source_term, action_level, product_type, target_channel, push_status, push_title, push_body, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                r["id"], r["source_term"], r["action_level"], r["product_type"], channel,
                status, push_title(r["source_term"], r["action_level"]),
                push_body(r["source_term"], r["product_type"], r["action_level"]),
                scheduled_at
            )
        )
        inserted += 1

    conn.execute("DELETE FROM push_dashboard_v91")
    qrows = conn.execute(
        '''
        SELECT id, target_channel, push_status, push_title, push_body, scheduled_at
        FROM push_queue_v91
        ORDER BY id ASC
        '''
    ).fetchall()

    for q in qrows:
        conn.execute(
            '''
            INSERT INTO push_dashboard_v91
            (queue_id, target_channel, push_status, push_title, push_body, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (q["id"], q["target_channel"], q["push_status"], q["push_title"], q["push_body"], q["scheduled_at"])
        )

    conn.commit()
    conn.close()
    print(f"[OK] push_center_v91 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
