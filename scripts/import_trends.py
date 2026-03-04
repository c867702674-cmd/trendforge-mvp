import os
import sys
import json
from datetime import date

# 让脚本能找到 server 包
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from server.db import insert_trend

DATA_PATH = os.path.join(BASE_DIR, "data", "trends_sample.json")


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(DATA_PATH)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    inserted = 0
    today = date.today().isoformat()

    for item in items:
        insert_trend(
            date=item.get("date", today),
            term=item.get("term"),
            country=item.get("country"),
            category=item.get("category"),
            growth=item.get("growth"),
            hit_score=item.get("hit_score"),
            action_level=item.get("action_level"),
            risk_level=item.get("risk_level"),
            reason=item.get("reason"),
            payload_json=json.dumps(item, ensure_ascii=False),
        )
        inserted += 1

    print(f"[TrendForge] OK inserted={inserted}")


if __name__ == "__main__":
    main()