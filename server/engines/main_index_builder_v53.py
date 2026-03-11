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

    sales = read_json("sales_home_v52.json")
    v50 = read_json("saas_dashboard_v50.json")
    push = read_json("push_control_v41.json")

    payload = {
        "generated_at": utc(),
        "hero": sales.get("hero", {
            "title": "TrendForge",
            "subtitle": "AI 趋势评分 + POD 卖家执行系统",
            "tagline": "发现趋势 → 判断价值 → 输出执行包 → 自动推送"
        }),
        "pricing": sales.get("pricing", []),
        "summary": {
            "top_items": len(v50.get("top_items", [])),
            "do_now": v50.get("summary", {}).get("do_now", 0),
            "push_total": push.get("summary", {}).get("total", 0),
            "push_ok": push.get("summary", {}).get("ok", 0)
        },
        "top_items": v50.get("top_items", [])[:10]
    }

    conn.execute("DELETE FROM main_index_snapshots")
    conn.execute(
        "INSERT INTO main_index_snapshots (snapshot_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("latest", json.dumps(payload, ensure_ascii=False), utc())
    )
    conn.commit()
    print(f"[OK] main_index_builder_v53 wrote snapshot db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
