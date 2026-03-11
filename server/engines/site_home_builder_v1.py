#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone
DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DOCS = "/root/trendforge-mvp/server/docs"
def utc(): return datetime.now(timezone.utc).isoformat()
def read_json(name):
    path = os.path.join(DOCS, name)
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except Exception: return {}
def main():
    conn = sqlite3.connect(DB_PATH)
    saas = read_json("saas_dashboard_v50.json")
    push = read_json("push_control_v41.json")
    subs = read_json("subscription_api_v32.json")
    sched = read_json("push_scheduler_v42.json")
    payload = {
        "generated_at": utc(),
        "hero": {"title": "TrendForge", "subtitle": "AI 趋势评分 + 卖家机会流 + 自动推送系统"},
        "summary": {
            "top_items": len(saas.get("top_items", [])),
            "do_now": saas.get("summary", {}).get("do_now", 0),
            "push_total": push.get("summary", {}).get("total", 0),
            "push_ok": push.get("summary", {}).get("ok", 0),
            "subscriptions": len(subs.get("subscriptions", [])),
            "scheduler_logs": sched.get("count", 0)
        },
        "top_items": saas.get("top_items", [])[:12],
        "push_summary": push.get("summary", {})
    }
    conn.execute("DELETE FROM site_home_snapshots")
    conn.execute("INSERT INTO site_home_snapshots (snapshot_name, payload_json, created_at) VALUES (?, ?, ?)",
                 ("latest", json.dumps(payload, ensure_ascii=False), utc()))
    conn.commit()
    print(f"[OK] site_home_builder_v1 wrote snapshot db={DB_PATH}")
    conn.close()
if __name__ == "__main__":
    main()
