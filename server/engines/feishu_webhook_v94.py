#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, json, datetime, urllib.request, urllib.error

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

FEISHU_WEBHOOKS = {
    "feishu_main": os.getenv("FEISHU_MAIN_WEBHOOK", "").strip(),
    "feishu_vip": os.getenv("FEISHU_VIP_WEBHOOK", "").strip(),
}

def build_payload(target_channel: str, execution_log: str, rule_code: str) -> dict:
    title = f"TrendForge {target_channel} 推送"
    content = f"规则：{rule_code}\n执行日志：{execution_log}"
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content}
                }
            ]
        }
    }

def post_webhook(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM feishu_push_logs_v94")

    rows = conn.execute(
        '''
        SELECT id, rule_code, target_channel, execution_log
        FROM execution_jobs_v93
        ORDER BY id ASC
        '''
    ).fetchall()

    inserted = 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for r in rows:
        channel = r["target_channel"]
        webhook = FEISHU_WEBHOOKS.get(channel, "")
        status = "SKIPPED"
        response_text = "channel not supported or webhook missing"

        if channel in ("feishu_main", "feishu_vip") and webhook:
            payload = build_payload(channel, r["execution_log"], r["rule_code"])
            try:
                response_text = post_webhook(webhook, payload)
                status = "PUSHED"
            except urllib.error.HTTPError as e:
                status = "FAILED"
                try:
                    response_text = e.read().decode("utf-8", errors="ignore")
                except Exception:
                    response_text = str(e)
            except Exception as e:
                status = "FAILED"
                response_text = str(e)
        elif channel == "email_digest":
            status = "SKIPPED"
            response_text = "email channel reserved for later version"

        conn.execute(
            '''
            INSERT INTO feishu_push_logs_v94
            (execution_job_id, target_channel, webhook_url, push_status, response_text, pushed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (r["id"], channel, webhook, status, response_text[:1000], now)
        )
        inserted += 1

    conn.execute("DELETE FROM feishu_push_dashboard_v94")
    logs = conn.execute(
        '''
        SELECT execution_job_id, target_channel, push_status, response_text, pushed_at
        FROM feishu_push_logs_v94
        ORDER BY id ASC
        '''
    ).fetchall()

    for log in logs:
        conn.execute(
            '''
            INSERT INTO feishu_push_dashboard_v94
            (execution_job_id, target_channel, push_status, response_text, pushed_at)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (log["execution_job_id"], log["target_channel"], log["push_status"], log["response_text"], log["pushed_at"])
        )

    conn.commit()
    conn.close()
    print(f"[OK] feishu_webhook_v94 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
