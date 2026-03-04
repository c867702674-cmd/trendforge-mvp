import os, sys, json, time
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from pytrends.request import TrendReq
from server.db import insert_trend

COUNTRY = "US"

def main():
    pytrends = TrendReq(hl="en-US", tz=0)
    today = date.today().isoformat()
    now = datetime.utcnow().isoformat()

    inserted = 0

    try:
        # ✅ 更稳定的接口（不需要 pn）
        terms = pytrends.today_searches(pn="US")
    except Exception as e:
        print("[gtrends] fetch failed:", e)
        return

    for rank, term in enumerate(terms[:20], start=1):
        hit_score = max(0, 100 - rank * 3)
        action_level = "DO_NOW" if rank <= 5 else "FAST_TEST"

        payload = {
            "source": "gtrends_today",
            "rank": rank,
            "fetched_at": now,
        }

        insert_trend(
            date=today,
            term=term,
            country=COUNTRY,
            category="gtrends",
            growth=None,
            hit_score=hit_score,
            action_level=action_level,
            risk_level=None,
            reason="Google Trends today_searches rank-based",
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        inserted += 1

        time.sleep(0.3)

    print(f"[gtrends] OK inserted={inserted}")

if __name__ == "__main__":
    main()