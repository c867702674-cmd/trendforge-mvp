import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple

from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

# allow importing server/db.py
sys.path.append(str(BASE_DIR / "server"))
from db import upsert_trend, init_db  # noqa: E402


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.zhizengzeng.com/v1").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest").strip()

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


def load_latest_json() -> Path:
    files = sorted(OUTPUT_DIR.glob("daily_trends_*.json"))
    if not files:
        raise FileNotFoundError("No daily_trends_*.json found. Run scripts/fetch_trends.py first.")
    return files[-1]


def pick_items(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ["items", "rising", "trends", "data", "top10"]:
        v = doc.get(key)
        if isinstance(v, list) and v:
            return v
    for v in doc.values():
        if isinstance(v, list) and v:
            return v
    return []


def extract_term_type_growth(item: Dict[str, Any]) -> Tuple[str, str, float]:
    term = str(item.get("term") or item.get("query") or item.get("title") or "").strip()
    ttype = str(item.get("type") or item.get("category") or "rising").strip()
    growth = item.get("growth") or item.get("value") or item.get("score") or 0
    try:
        growth_f = float(growth)
    except Exception:
        growth_f = 0.0
    return term, ttype, growth_f


def extract_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    # remove code fences if any
    if text.startswith("```"):
        text = text.strip("`")
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def ai_score(term: str, growth: float) -> Dict[str, Any]:
    prompt = f"""
You are an Amazon seller opportunity analyst (US market). Evaluate a trending keyword and return strict JSON only.

Keyword: {term}
Growth: {growth}

Rules:
- If it implies brand/team/logo/celebrity/movie/game IP, set risk_level=HIGH and action_level=IGNORE.
- Action levels: DO_NOW, FAST_TEST, IGNORE.
- hit_score: integer 0-100.
- reason: <= 140 characters.

Return JSON only:
{{
  "hit_score": 0,
  "action_level": "DO_NOW",
  "risk_level": "LOW",
  "reason": "..."
}}
"""
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Return STRICT JSON only. No markdown."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    content = resp.choices[0].message.content or ""
    data = extract_json(content)

    # normalize
    hs = int(data.get("hit_score", 0) or 0)
    hs = max(0, min(100, hs))
    action = str(data.get("action_level", "IGNORE")).upper()
    if action not in ["DO_NOW", "FAST_TEST", "IGNORE"]:
        action = "IGNORE"
    risk = str(data.get("risk_level", "LOW")).upper()
    if risk not in ["LOW", "MEDIUM", "HIGH"]:
        risk = "LOW"
    reason = str(data.get("reason", "") or "").strip()[:140]

    return {"hit_score": hs, "action_level": action, "risk_level": risk, "reason": reason}


def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY env var.")

    init_db()

    json_path = load_latest_json()
    print(f"Importing + scoring from: {json_path.name}")

    doc = json.loads(json_path.read_text(encoding="utf-8"))
    items = pick_items(doc)
    if not items:
        raise RuntimeError("No items found in trends JSON.")

    extracted: List[Tuple[str, str, float, Dict[str, Any]]] = []
    for it in items:
        term, ttype, growth = extract_term_type_growth(it)
        if term:
            extracted.append((term, ttype, growth, it))

    # Top 50 by growth
    extracted.sort(key=lambda x: x[2], reverse=True)
    top50 = extracted[:50]

    today = datetime.now().strftime("%Y-%m-%d")
    inserted = 0

    for term, ttype, growth, raw in top50:
        try:
            scored = ai_score(term, growth)
        except Exception as e:
            print(f"[SKIP AI ERROR] {term} -> {e}")
            continue

        upsert_trend(
            date=today,
            term=term,
            country="US",
            category=ttype or "general",
            growth=growth,
            hit_score=scored["hit_score"],
            action_level=scored["action_level"],
            risk_level=scored["risk_level"],
            reason=scored["reason"],
            payload_json=json.dumps(raw, ensure_ascii=False),
        )
        inserted += 1
        time.sleep(0.2)  # 轻微限速，稳定点

    print(f"Done. Inserted {inserted} scored trends into DB.")


if __name__ == "__main__":
    main()