#!/usr/bin/env python3
import os, sqlite3, datetime

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

def simulate_push(channel, rule):
    if channel == "feishu_vip":
        return "VIP Feishu push simulated"
    if channel == "feishu_main":
        return "Main Feishu push simulated"
    if channel == "email_digest":
        return "Email digest simulated"
    return "Unknown channel"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM execution_jobs_v93")

    rows = conn.execute(
        '''
        SELECT id, rule_code, target_channel, execute_at
        FROM automation_jobs_v92
        ORDER BY id ASC
        '''
    ).fetchall()

    inserted = 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for r in rows:
        log = simulate_push(r["target_channel"], r["rule_code"])
        conn.execute(
            '''
            INSERT INTO execution_jobs_v93
            (automation_job_id, rule_code, target_channel, execution_status, executed_at, execution_log)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (r["id"], r["rule_code"], r["target_channel"], "DONE", now, log)
        )
        inserted += 1

    conn.execute("DELETE FROM execution_dashboard_v93")

    jobs = conn.execute(
        '''
        SELECT id, rule_code, target_channel, execution_status, executed_at, execution_log
        FROM execution_jobs_v93
        ORDER BY id ASC
        '''
    ).fetchall()

    for j in jobs:
        conn.execute(
            '''
            INSERT INTO execution_dashboard_v93
            (job_id, rule_code, target_channel, execution_status, executed_at, execution_log)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (j["id"], j["rule_code"], j["target_channel"], j["execution_status"], j["executed_at"], j["execution_log"])
        )

    conn.commit()
    conn.close()
    print(f"[OK] execution_engine_v93 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
