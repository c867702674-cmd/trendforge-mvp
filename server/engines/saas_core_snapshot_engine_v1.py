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

    dashboard = read_json(os.path.join(DOCS_DIR, "seller_dashboard_v28_api.json"))
    listings = read_json(os.path.join(DOCS_DIR, "listing_auto_generator_api.json"))
    profits = read_json(os.path.join(DOCS_DIR, "pod_niche_profit_api.json"))
    ranking = read_json(os.path.join(DOCS_DIR, "ai_trend_ranking_api.json"))

    payload = {
        "generated_at": utc(),
        "top_opportunities": dashboard.get("top_opportunities", [])[:10],
        "top_listings": listings.get("items", [])[:10],
        "top_profits": profits.get("items", [])[:10],
        "top_rankings": ranking.get("items", [])[:10],
        "counts": {
            "opportunities": len(dashboard.get("top_opportunities", [])),
            "listings": len(listings.get("items", [])),
            "profits": len(profits.get("items", [])),
            "rankings": len(ranking.get("items", [])),
        }
    }

    conn.execute("DELETE FROM saas_core_snapshots")
    conn.execute(
        "INSERT INTO saas_core_snapshots (snapshot_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("latest", json.dumps(payload, ensure_ascii=False), utc())
    )
    conn.commit()
    print(f"[OK] saas_core_snapshot_engine_v1 wrote snapshot db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
