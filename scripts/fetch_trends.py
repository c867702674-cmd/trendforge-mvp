import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

from pytrends.request import TrendReq
from rapidfuzz import fuzz

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
SEEDS_PATH = BASE_DIR / "seeds.txt"
BLOCKLIST_PATH = BASE_DIR / "blocklist.txt"
WHITELIST_HINTS_PATH = BASE_DIR / "whitelist_hints.txt"

US_GEO = "US"
TZ_SGT = timezone(timedelta(hours=8))  # Singapore/China time


def now_sgt() -> datetime:
    return datetime.now(TZ_SGT)


def load_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def normalize_term(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def is_blocked(term: str, blocklist: List[str], fuzzy_threshold: int = 92) -> Tuple[bool, str]:
    """
    Return (blocked, reason).
    - Contains match
    - Fuzzy match (token_set_ratio) to catch variations
    """
    t = normalize_term(term)
    for b in blocklist:
        b_norm = normalize_term(b)
        if not b_norm:
            continue
        if b_norm in t:
            return True, f"contains:{b}"
        if fuzz.token_set_ratio(t, b_norm) >= fuzzy_threshold:
            return True, f"fuzzy:{b}"
    return False, ""


def classify_type(term: str) -> str:
    t = normalize_term(term)
    if any(k in t for k in ["pattern", "seamless", "tileable", "quilt", "patchwork"]):
        return "结构图形"
    if any(k in t for k in ["decor", "wall art", "shower curtain", "pillow", "blanket", "doormat"]):
        return "家居风格"
    if any(k in t for k in ["outfit", "hoodie", "sweatshirt", "t-shirt", "tee"]):
        return "服饰穿搭"
    if "gift" in t:
        return "送礼场景"
    if any(k in t for k in ["aesthetic", "style", "vibe", "core"]):
        return "审美风格"
    return "其他"


def score_term(term: str, growth: float, whitelist_hints: List[str]) -> float:
    """
    Simple MVP scoring:
    - growth weight
    - bonus if contains whitelist hints
    - slight penalties for too short/too long
    """
    t = normalize_term(term)
    score = 0.0
    score += float(growth or 0.0) * 1.0

    for h in whitelist_hints:
        h_norm = normalize_term(h)
        if h_norm and h_norm in t:
            score += 8.0

    n = len(t)
    if n < 4:
        score -= 10
    if n > 40:
        score -= 8

    if any(k in t for k in ["pattern", "seamless", "tileable", "vector", "minimal", "vintage", "rustic", "boho"]):
        score += 6.0

    return score


def fetch_related_rising(pytrends: TrendReq, seed: str) -> List[Dict]:
    """
    Returns: [{term, growth, source_seed}]
    growth:
      Breakout -> 500
      number -> that number
    """
    pytrends.build_payload([seed], geo=US_GEO, timeframe="now 7-d")
    related = pytrends.related_queries()

    items: List[Dict] = []
    if seed not in related:
        return items
    rising_df = related[seed].get("rising")
    if rising_df is None:
        return items

    for _, row in rising_df.iterrows():
        term = str(row.get("query", "")).strip()
        val = row.get("value", 0)
        if isinstance(val, str) and val.lower().strip() == "breakout":
            growth = 500.0
        else:
            try:
                growth = float(val)
            except Exception:
                growth = 0.0

        if term:
            items.append({"term": term, "growth": growth, "source": f"gtrends:{seed}"})
    return items


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    seeds = load_lines(SEEDS_PATH)
    blocklist = load_lines(BLOCKLIST_PATH)
    whitelist_hints = load_lines(WHITELIST_HINTS_PATH)

    # tz=480 => UTC+8 minutes offset for TrendsReq (pytrends expects minutes)
    pytrends = TrendReq(hl="en-US", tz=480)

    raw: List[Dict] = []
    for seed in seeds:
        try:
            raw.extend(fetch_related_rising(pytrends, seed))
        except Exception:
            # pytrends can be flaky; skip seed
            continue

    # de-duplicate by normalized term; keep max growth
    dedup: Dict[str, Dict] = {}
    for it in raw:
        key = normalize_term(it["term"])
        if key not in dedup or (it.get("growth", 0) or 0) > (dedup[key].get("growth", 0) or 0):
            dedup[key] = it

    candidates: List[Dict] = []
    for key, it in dedup.items():
        term = it["term"]
        blocked, _reason = is_blocked(term, blocklist)
        if blocked:
            continue

        ttype = classify_type(term)
        score = score_term(term, it.get("growth", 0.0), whitelist_hints)

        # quick risk heuristic (very rough; AI will do final risk)
        risk = "低"
        t = normalize_term(term)
        if any(x in t for x in ["logo", "disney", "marvel", "nfl", "nba", "mlb", "nhl"]):
            risk = "高"
        elif any(x in t for x in ["university", "college", "team"]):
            risk = "中"

        candidates.append({
            "term": term,
            "growth": it.get("growth", 0.0),
            "type": ttype,
            "risk": risk,
            "score": round(score, 2),
            "source": it.get("source", "gtrends"),
        })

    top = sorted(candidates, key=lambda x: x["score"], reverse=True)[:10]

    date_str = now_sgt().strftime("%Y-%m-%d")
    out = {
        "date": date_str,
        "geo": "US",
        "count_raw": len(raw),
        "count_candidates": len(candidates),
        "top10": top
    }

    out_path = OUTPUT_DIR / f"daily_trends_{date_str}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()