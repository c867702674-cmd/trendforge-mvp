#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, json, datetime, urllib.request, urllib.error

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

FEISHU_WEBHOOKS = {
    "feishu_main": os.getenv("FEISHU_MAIN_WEBHOOK", "").strip(),
    "feishu_vip": os.getenv("FEISHU_VIP_WEBHOOK", "").strip(),
}

def choose_channel(action_level: str) -> str:
    return "feishu_vip" if action_level == "DO_NOW" else "feishu_main"

def build_card(term: str, action: str, product: str, score: float, growth: float, url: str):
    title = f"TrendForge {action} | {product}"
    summary = f"{term} | score {score} | growth {growth}"
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue" if action == "WATCH" else "green"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**趋势词**：{term}"}},
                {"tag": "div", "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**动作**\n{action}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**产品**\n{product}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**评分**\n{score}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**增长**\n{growth}"}},
                ]},
                {"tag": "action", "actions": [
                    {"tag": "button", "text": {"tag": "plain_text", "content": "查看趋势源"}, "type": "primary", "url": url}
                ]}
            ]
        }
    }
    return title, summary, payload

def post_webhook(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("DELETE FROM feishu_card_jobs_v95")

    rows = conn.execute(
        '''
        SELECT id, source_term, action_level, product_type, trend_score, growth_rate, source_url
        FROM trend_data_v89
        WHERE action_level IN ('DO_NOW', 'WATCH')
        ORDER BY trend_score DESC, id ASC
        LIMIT 12
        '''
    ).fetchall()

    inserted = 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for r in rows:
        channel = choose_channel(r["action_level"])
        title, summary, payload = build_card(
            r["source_term"], r["action_level"], r["product_type"],
            r["trend_score"], r["growth_rate"], r["source_url"]
        )
        webhook = FEISHU_WEBHOOKS.get(channel, "")
        status = "SKIPPED"
        response_text = "webhook missing"

        if webhook:
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

        conn.execute(
            '''
            INSERT INTO feishu_card_jobs_v95
            (trend_id, source_term, action_level, product_type, target_channel, card_title, card_summary, card_json, send_status, response_text, sent_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                r["id"], r["source_term"], r["action_level"], r["product_type"], channel,
                title, summary, json.dumps(payload, ensure_ascii=False),
                status, response_text[:1000], now
            )
        )
        inserted += 1

    conn.execute("DELETE FROM feishu_card_dashboard_v95")
    jobs = conn.execute(
        '''
        SELECT id, target_channel, card_title, send_status, response_text, sent_at
        FROM feishu_card_jobs_v95
        ORDER BY id ASC
        '''
    ).fetchall()

    for j in jobs:
        conn.execute(
            '''
            INSERT INTO feishu_card_dashboard_v95
            (job_id, target_channel, card_title, send_status, response_text, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (j["id"], j["target_channel"], j["card_title"], j["send_status"], j["response_text"], j["sent_at"])
        )

    conn.commit()
    conn.close()
    print(f"[OK] feishu_card_v95 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
