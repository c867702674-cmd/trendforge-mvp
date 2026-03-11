#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, datetime

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

RULES = [
    ("rule_do_now_vip", "DO_NOW -> VIP Push", "feishu_vip", "DO_NOW"),
    ("rule_watch_main", "WATCH -> Main Push", "feishu_main", "WATCH"),
    ("rule_ignore_email", "IGNORE -> Email Digest", "email_digest", "IGNORE"),
]

def pick_rule(push_title: str, target_channel: str):
    title = (push_title or "").upper()
    if "[DO_NOW]" in title and target_channel == "feishu_vip":
        return "rule_do_now_vip"
    if "[WATCH]" in title and target_channel == "feishu_main":
        return "rule_watch_main"
    return "rule_ignore_email"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM automation_rules_v92")
    for code, name, channel, action in RULES:
        conn.execute(
            '''
            INSERT INTO automation_rules_v92
            (rule_code, rule_name, target_channel, trigger_action_level, is_enabled)
            VALUES (?, ?, ?, ?, 1)
            ''',
            (code, name, channel, action)
        )

    conn.execute("DELETE FROM automation_jobs_v92")
    rows = conn.execute(
        '''
        SELECT id, target_channel, push_title, scheduled_at
        FROM push_dashboard_v91
        ORDER BY queue_id ASC
        '''
    ).fetchall()

    inserted = 0
    for r in rows:
        rule_code = pick_rule(r["push_title"], r["target_channel"])
        execute_at = r["scheduled_at"]
        result_note = f"Auto route via {rule_code}"
        conn.execute(
            '''
            INSERT INTO automation_jobs_v92
            (push_dashboard_id, rule_code, target_channel, job_status, execute_at, result_note)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (r["id"], rule_code, r["target_channel"], "PENDING", execute_at, result_note)
        )
        inserted += 1

    conn.execute("DELETE FROM automation_dashboard_v92")
    jobs = conn.execute(
        '''
        SELECT id, rule_code, target_channel, job_status, execute_at, result_note
        FROM automation_jobs_v92
        ORDER BY id ASC
        '''
    ).fetchall()

    for j in jobs:
        conn.execute(
            '''
            INSERT INTO automation_dashboard_v92
            (job_id, rule_code, target_channel, job_status, execute_at, result_note)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (j["id"], j["rule_code"], j["target_channel"], j["job_status"], j["execute_at"], j["result_note"])
        )

    conn.commit()
    conn.close()
    print(f"[OK] automation_hub_v92 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
