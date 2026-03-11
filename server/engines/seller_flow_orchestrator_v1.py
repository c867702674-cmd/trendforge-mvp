#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DOCS_DIR = "/root/trendforge-mvp/server/docs"

def utc():
    return datetime.now(timezone.utc).isoformat()

def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cards = read_json(os.path.join(DOCS_DIR, "opportunity_cards_v33.json"))
    alerts = read_json(os.path.join(DOCS_DIR, "seller_alerts_v34.json"))
    dashboard = read_json(os.path.join(DOCS_DIR, "seller_dashboard_v28_api.json"))
    subs = read_json(os.path.join(DOCS_DIR, "subscription_api_v32.json"))

    payload = {
        "generated_at": utc(),
        "cards": cards.get("items", [])[:12],
        "alerts": alerts.get("items", [])[:12],
        "dashboard": {
            "top_opportunities": dashboard.get("top_opportunities", [])[:8],
            "top_listings": dashboard.get("top_listings", [])[:8],
            "top_profits": dashboard.get("top_profits", [])[:8],
        },
        "subscription": subs.get("subscriptions", [])[:3],
        "counts": {
            "cards": len(cards.get("items", [])),
            "alerts": len(alerts.get("items", [])),
            "opportunities": len(dashboard.get("top_opportunities", [])),
            "listings": len(dashboard.get("top_listings", [])),
            "profits": len(dashboard.get("top_profits", [])),
            "subscriptions": len(subs.get("subscriptions", [])),
        }
    }

    conn.execute("DELETE FROM seller_flow_snapshots")
    conn.execute(
        "INSERT INTO seller_flow_snapshots (flow_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("latest", json.dumps(payload, ensure_ascii=False), utc())
    )
    conn.commit()
    print(f"[OK] seller_flow_orchestrator_v1 wrote snapshot db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
