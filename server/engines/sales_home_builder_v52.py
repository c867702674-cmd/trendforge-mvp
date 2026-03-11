#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DOCS = "/root/trendforge-mvp/server/docs"

def utc():
    return datetime.now(timezone.utc).isoformat()

def read_json(name):
    path = os.path.join(DOCS, name)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def main():
    conn = sqlite3.connect(DB_PATH)

    site_home = read_json("site_home_v51.json")
    v50 = read_json("saas_dashboard_v50.json")
    push = read_json("push_control_v41.json")

    payload = {
        "generated_at": utc(),
        "hero": {
            "title": "TrendForge",
            "subtitle": "为中国亚马逊 / Etsy POD 卖家打造的 AI 趋势情报系统",
            "tagline": "发现趋势 → 判断价值 → 生成执行方案 → 自动推送"
        },
        "pricing": [
            {
                "plan": "Free",
                "price_usd": "$0 / month",
                "price_cny": "¥0 / 月",
                "features": ["基础看板", "少量趋势浏览", "适合体验"]
            },
            {
                "plan": "Starter",
                "price_usd": "$19 / month",
                "price_cny": "¥139 / 月",
                "features": ["更多趋势数据", "基础 AI 评分", "适合小团队测试"]
            },
            {
                "plan": "Pro",
                "price_usd": "$39 / month",
                "price_cny": "¥279 / 月",
                "features": ["完整 AI 趋势评分", "执行包", "飞书推送", "适合核心卖家"]
            }
        ],
        "summary": {
            "top_items": len(v50.get("top_items", [])),
            "do_now": v50.get("summary", {}).get("do_now", 0),
            "push_total": push.get("summary", {}).get("total", 0),
            "push_ok": push.get("summary", {}).get("ok", 0)
        },
        "top_items": v50.get("top_items", [])[:8],
        "site_runtime": site_home.get("push_summary", {})
    }

    conn.execute("DELETE FROM sales_home_snapshots")
    conn.execute(
        "INSERT INTO sales_home_snapshots (snapshot_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("latest", json.dumps(payload, ensure_ascii=False), utc())
    )
    conn.commit()
    print(f"[OK] sales_home_builder_v52 wrote snapshot db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
