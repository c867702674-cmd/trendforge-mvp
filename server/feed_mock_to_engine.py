# server/feed_mock_to_engine.py
# -*- coding: utf-8 -*-

import json
import sqlite3
import datetime as dt
from typing import Any, Dict, List, Optional

from trend_engine import TrendEngine, TrendItem, write_scores_to_trends


DB_PATH_DEFAULT = "server/trendforge.db"
COUNTRY_DEFAULT = "US"
CATEGORY_DEFAULT = "POD"


def utc_now_iso() -> str:
    """Timezone-aware UTC now in ISO8601 with Z."""
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_minus(hours: int) -> str:
    """UTC ISO string for now - hours."""
    t = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    return t.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_json_loads(s: Optional[str]) -> Dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def extract_items_from_trends_payload(
    conn: sqlite3.Connection,
    since_iso: str,
    limit_rows: int = 200,
) -> List[TrendItem]:
    """
    尝试从已有 trends.payload_json 里提取 evidence/sample 来构造 TrendItem。
    兼容：
      payload_json.evidence = [{title, shop_id, item_id, url}, ...]
      payload_json.sample   = [{title, tags, listing_id, shop_id, url}, ...]
    找不到就返回空列表。
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT payload_json
        FROM trends
        WHERE date >= ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (since_iso, limit_rows),
    )
    rows = cur.fetchall()

    items: List[TrendItem] = []
    for (payload_json,) in rows:
        p = safe_json_loads(payload_json)

        ev = p.get("evidence")
        if isinstance(ev, list):
            for e in ev:
                if not isinstance(e, dict):
                    continue
                title = (e.get("title") or "").strip()
                if not title:
                    continue
                items.append(
                    TrendItem(
                        title=title,
                        tags=[],
                        shop_id=e.get("shop_id"),
                        item_id=e.get("item_id") or e.get("listing_id"),
                        url=e.get("url"),
                        raw=e,
                    )
                )

        smp = p.get("sample")
        if isinstance(smp, list):
            for s in smp:
                if not isinstance(s, dict):
                    continue
                title = (s.get("title") or "").strip()
                if not title:
                    continue
                tags = s.get("tags") if isinstance(s.get("tags"), list) else []
                items.append(
                    TrendItem(
                        title=title,
                        tags=tags,
                        shop_id=s.get("shop_id"),
                        item_id=s.get("listing_id") or s.get("item_id"),
                        url=s.get("url"),
                        raw=s,
                    )
                )

    return items


def built_in_fallback_items() -> List[TrendItem]:
    """
    兜底 mock：保证 2-gram 能跑出分数（含重复、含小爆发）。
    仅用于验证链路，不代表真实趋势。
    """
    titles = [
        "Funny pickleball mom shirt for women",
        "Pickleball mom sweatshirt gift",
        "Retro pickleball dad tee",
        "Custom name teacher shirt gift",
        "Teacher life shirt funny",
        "Nurse life sweatshirt funny gift",
        "Nurse life tee for women",
        "Dog mom shirt vintage",
        "Dog mom sweatshirt gift",
        "Graduation 2026 gift shirt",
        "Graduation party shirt custom name",
        "Memorial shirt in loving memory",
        "In loving memory custom shirt",
        "Wedding welcome sign template",
        "Wedding welcome sign printable",
        "Nursery wall art boho",
        "Boho nursery wall art set",
        "Embroidered hoodie custom name",
        "Custom embroidered hoodie gift",
        "Funny sweatshirt for men",
    ]

    # 让某些主题“更热”一点：重复添加（用来触发 2-gram 的 min_mentions）
    boosted = titles + titles[:8] + titles[:5]

    items: List[TrendItem] = []
    for i, t in enumerate(boosted, start=1):
        items.append(
            TrendItem(
                title=t,
                tags=[],
                shop_id=(1000 + (i % 7)),
                item_id=i,
                url=None,
            )
        )
    return items


def main() -> None:
    fetched_at = utc_now_iso()

    # 以当前时间为锚点的滚动窗口（不要求整点）
    w1 = iso_minus(1)
    w3 = iso_minus(3)
    w6 = iso_minus(6)
    w24 = iso_minus(24)

    conn = sqlite3.connect(DB_PATH_DEFAULT)
    conn.row_factory = sqlite3.Row

    # 调试模式：放宽 6h mentions 门槛，确保 mock 能产出 scores
    engine = TrendEngine(
        top_k=30,
        min_mentions_6h=2,
    )

    # 尝试从已有 trends 里提取“证据/样本”作为输入（若为空则走内置 fallback）
    items_1h = extract_items_from_trends_payload(conn, w1)
    items_3h = extract_items_from_trends_payload(conn, w3)
    items_6h = extract_items_from_trends_payload(conn, w6)
    items_24h = extract_items_from_trends_payload(conn, w24)

    if len(items_24h) == 0:
        base = built_in_fallback_items()
        # 让窗口有差异：最近窗口用更多“热”数据
        items_1h = base[:18] + base[:12]
        items_3h = base[:20] + base[:10]
        items_6h = base[:22]
        items_24h = base[:20]
        source = "mock_builtin"
        print("[mock] No usable payloads found in trends table, using built-in fallback items.")
    else:
        source = "mock_from_db"
        print(f"[mock] Using items extracted from existing trends.payload_json. items_24h={len(items_24h)}")

    scores = engine.score(
        source=source,
        fetched_at=fetched_at,
        items_1h=items_1h,
        items_3h=items_3h,
        items_6h=items_6h,
        items_24h=items_24h,
        conn=conn,  # enable novelty first_seen state
    )

    inserted = write_scores_to_trends(
        conn,
        fetched_at=fetched_at,
        country=COUNTRY_DEFAULT,
        category=CATEGORY_DEFAULT,
        source=source,
        scores=scores,
    )

    print(f"[mock] done. scores={len(scores)} trends_inserted={inserted}")
    if scores:
        print("[mock] top 5 terms:")
        for s in scores[:5]:
            print(f"  - {s.term} | hit={s.hit_score} | {s.action_level} | growth={s.growth}")

    conn.close()


if __name__ == "__main__":
    main()