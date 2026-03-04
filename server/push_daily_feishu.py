import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta, timezone

DB_PATH = os.getenv("TRENDFORGE_DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
WEB_URL = os.getenv("TRENDFORGE_WEB_URL", "https://trendforgepro.com").rstrip("/")

def now_utc():
    return datetime.now(timezone.utc)

def feishu_post(payload):
    if not FEISHU_WEBHOOK:
        raise RuntimeError("FEISHU_WEBHOOK is empty")
    r = requests.post(FEISHU_WEBHOOK, json=payload, timeout=12)
    try:
        data = r.json()
    except Exception:
        data = None
    ok = (r.status_code == 200) and isinstance(data, dict) and data.get("code") == 0
    return ok, r.status_code, data

def q1(conn, sql, args=()):
    cur = conn.execute(sql, args)
    row = cur.fetchone()
    return (row[0] if row and row[0] is not None else 0)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    since = now_utc() - timedelta(hours=24)
    since_iso = since.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # counts by action_level
    do_now = q1(conn, "SELECT COUNT(1) FROM trends WHERE action_level='DO_NOW'")
    doing  = q1(conn, "SELECT COUNT(1) FROM trends WHERE action_level='DOING'")
    watch  = q1(conn, "SELECT COUNT(1) FROM trends WHERE action_level='WATCH'")

    # new in 24h (created_at is TEXT)
    new_24h = q1(conn, "SELECT COUNT(1) FROM trends WHERE created_at >= ?", (since_iso,))

    # ready in DO_NOW (execution exists in payload_json)
    ready_do_now = q1(conn, """
        SELECT COUNT(1)
        FROM trends
        WHERE action_level='DO_NOW'
          AND payload_json LIKE '%"execution"%'
    """)

    top = conn.execute("""
        SELECT id, term, hit_score, growth
        FROM trends
        WHERE action_level='DO_NOW'
        ORDER BY hit_score DESC, id DESC
        LIMIT 10
    """).fetchall()

    top_lines = []
    for r in top:
        top_lines.append(f"- #{r['id']} **{r['term']}**  (hit {r['hit_score']}, growth {r['growth']})")

    md = (
        f"**今日概览（近24h）**\n"
        f"- DO_NOW：**{do_now}**（READY：**{ready_do_now}**）\n"
        f"- DOING：**{doing}**\n"
        f"- WATCH：**{watch}**\n"
        f"- 新增趋势：**{new_24h}**\n\n"
        f"**Top DO_NOW（可直接上架）**\n"
        + ("\n".join(top_lines) if top_lines else "- （暂无）")
    )

    card = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": "blue",
                "title": {"tag": "plain_text", "content": "📌 TrendForge 每日趋势日报"}
            },
            "elements": [
                {"tag": "markdown", "content": md},
                {"tag": "hr"},
                {"tag": "action", "actions": [
                    {"tag":"button","text":{"tag":"plain_text","content":"打开 TrendForge"},"type":"primary","url": f"{WEB_URL}/"}
                ]}
            ]
        }
    }

    ok, status, data = feishu_post(card)
    if ok:
        print("[OK] daily report sent")
    else:
        print(f"[ERR] daily report send failed: http={status} resp={data}")

    conn.close()

if __name__ == "__main__":
    main()