#!/usr/bin/env python3
import os, sqlite3, json

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUT1 = "/root/trendforge-mvp/server/docs/ai_trend_score_v50.json"
OUT2 = "/root/trendforge-mvp/server/docs/saas_dashboard_v50.json"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT term, trend_power_score, profit_score, competition_score,
               design_difficulty, viral_probability, decision_level,
               design_direction, product_ideas_json
        FROM ai_trend_scorecards
        ORDER BY trend_power_score DESC, id ASC
        LIMIT 80
    """).fetchall()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["product_ideas_json"] = json.loads(d["product_ideas_json"] or "[]")
        except Exception:
            d["product_ideas_json"] = []
        items.append(d)

    score_data = {"items": items, "count": len(items)}

    dashboard = {
        "summary": {
            "total": len(items),
            "do_now": sum(1 for x in items if x["decision_level"] == "DO_NOW"),
            "fast_follow": sum(1 for x in items if x["decision_level"] == "FAST_FOLLOW"),
            "watch": sum(1 for x in items if x["decision_level"] == "WATCH"),
            "avoid": sum(1 for x in items if x["decision_level"] == "AVOID"),
        },
        "top_items": items[:20]
    }

    os.makedirs(os.path.dirname(OUT1), exist_ok=True)
    with open(OUT1, "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)
    with open(OUT2, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    print(f"[OK] ai_trend_score_api_v50 wrote={OUT1} items={len(items)}")
    print(f"[OK] saas_dashboard_v50 wrote={OUT2} top_items={len(dashboard['top_items'])}")
    conn.close()

if __name__ == "__main__":
    main()
