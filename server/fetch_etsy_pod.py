#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fetch_etsy_pod.py (D1 版：真实 payload_json / 规则解释 / 证据)
- 不依赖 Etsy OAuth（只用 Etsy Open API 的 x-api-key）
- 采集：关键词在 Etsy active listings 的 total_count + 示例 listing（id/title/url）
- 写入：etsy_term_metrics（用于 prev_count）
- 写入：trends（term/growth/hit_score/action_level/payload_json 等）
"""

import os
import json
import time
import math
import sqlite3
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv


DB_DEFAULT = "server/trendforge.db"


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_now_iso() -> str:
    # 与你系统里其它脚本一致：UTC ISO
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> None:
    # 你可以把 Etsy 配置放在 .env.etsy；没有也不报错
    load_dotenv(".env.etsy")
    load_dotenv("/root/trendforge-mvp/.env.etsy", override=False)
    # 兼容你现有的 .env.feishu（如果你把 DB path 放那）
    load_dotenv(".env.feishu")
    load_dotenv("/root/trendforge-mvp/.env.feishu", override=False)


def db_connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # 历史指标表：用于 prev_count（例如取 24h 前）
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS etsy_term_metrics (
          term TEXT NOT NULL,
          ts TEXT NOT NULL,           -- UTC hour bucket，例如 2026-02-28T02:00:00Z
          count INTEGER NOT NULL,
          source TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          PRIMARY KEY (term, ts)
        );
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_etsy_metrics_term ON etsy_term_metrics(term);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_etsy_metrics_ts ON etsy_term_metrics(ts);")

    conn.commit()


def hour_bucket_iso(t: dt.datetime) -> str:
    t = t.astimezone(dt.timezone.utc)
    t2 = t.replace(minute=0, second=0, microsecond=0)
    return t2.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_prev_count(conn: sqlite3.Connection, term: str, lookback_hours: int) -> Optional[int]:
    """
    取 <= now-lookback 的最近一条 count，作为 prev_count
    """
    if lookback_hours <= 0:
        return None
    target = utc_now() - dt.timedelta(hours=lookback_hours)
    target_iso = hour_bucket_iso(target)

    cur = conn.cursor()
    cur.execute(
        """
        SELECT count
        FROM etsy_term_metrics
        WHERE term = ?
          AND ts <= ?
        ORDER BY ts DESC
        LIMIT 1
        """,
        (term, target_iso),
    )
    row = cur.fetchone()
    return int(row["count"]) if row else None


def upsert_metric(conn: sqlite3.Connection, term: str, ts: str, count: int, source: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO etsy_term_metrics (term, ts, count, source, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(term, ts) DO UPDATE SET
          count=excluded.count,
          source=excluded.source,
          updated_at=excluded.updated_at
        """,
        (term, ts, int(count), source, utc_now_iso()),
    )
    conn.commit()


def table_has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r["name"] for r in cur.fetchall()]
    return col in cols


def insert_trend(conn: sqlite3.Connection, row: Dict[str, Any]) -> None:
    """
    兼容你 trends 表可能有/没有的列：动态构造 INSERT
    你已说明必有：term/growth/hit_score/action_level/payload_json
    """
    # 允许字段（按你项目常见字段）
    candidates = [
        "created_at",
        "term",
        "growth",
        "hit_score",
        "action_level",
        "payload_json",
        "country",
        "category",
        "reason",
    ]

    cols: List[str] = []
    vals: List[Any] = []
    for c in candidates:
        if c in row and table_has_column(conn, "trends", c):
            cols.append(c)
            vals.append(row[c])

    if not cols:
        raise RuntimeError("trends 表列检查失败：没有可写入列")

    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO trends ({','.join(cols)}) VALUES ({placeholders});"

    cur = conn.cursor()
    cur.execute(sql, tuple(vals))
    conn.commit()


# -------------------------
# Etsy Open API
# -------------------------
def etsy_headers(api_key: str) -> Dict[str, str]:
    # Etsy Open API v3 常用 header 是 x-api-key
    return {
        "x-api-key": api_key,
        "accept": "application/json",
        "user-agent": "TrendForge/1.0 (+https://trendforge.local)",
    }


def etsy_search_active_listings(
    api_key: str,
    keywords: str,
    limit: int = 10,
    offset: int = 0,
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    返回：
    - total_count（尽量从 API 返回的 count/total 字段拿）
    - 示例 listings：id/title/url
    """
    # Etsy v3 application 常见 endpoint（公开搜索类）
    # 注意：Etsy 可能会调整字段名；这里做容错。
    url = "https://openapi.etsy.com/v3/application/listings/active"
    params = {
        "keywords": keywords,
        "limit": limit,
        "offset": offset,
        "sort_on": "score",
        "sort_order": "desc",
    }

    r = requests.get(url, headers=etsy_headers(api_key), params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    # 容错：不同版本字段可能是 count / total / total_count
    total = data.get("count")
    if total is None:
        total = data.get("total")
    if total is None:
        total = data.get("total_count")
    if total is None:
        # 最差情况下：用 results 长度代替
        total = len(data.get("results") or [])

    results = data.get("results") or []
    listings: List[Dict[str, Any]] = []
    for it in results[:limit]:
        listing_id = it.get("listing_id") or it.get("id")
        title = it.get("title") or ""
        # v3 listing 里常见是 url 或 listing_url；也可能没有
        link = it.get("url") or it.get("listing_url") or ""
        if listing_id is None:
            continue
        listings.append(
            {
                "listing_id": listing_id,
                "title": title,
                "url": link,
            }
        )

    return int(total), listings


# -------------------------
# Scoring / Rules
# -------------------------
def calc_growth_pct(count: int, prev: Optional[int]) -> float:
    if prev is None:
        return 0.0
    base = max(1, int(prev))
    return (float(count) - float(prev)) / float(base) * 100.0


def calc_hit_score(count: int, growth_pct: float) -> int:
    """
    0~100：可解释的简单打分（先够用，后面你可以替换成更复杂）
    """
    # 规模：log1p(count) -> 0..?
    scale = math.log1p(max(0, count))  # 0~约 13
    # 增长：growth_pct 做一个温和映射
    g = max(0.0, growth_pct)

    score = scale * 10.0 + min(60.0, g / 5.0)  # 增长每 5% 加 1 分，封顶 60
    return int(max(0, min(100, round(score))))


def decide_action_level(count: int, growth_pct: float, hit_score: int, rules: Dict[str, Any]) -> str:
    dn = (rules.get("do_now") or {}) if isinstance(rules, dict) else {}
    min_count = int(dn.get("min_count", 60))
    min_growth = float(dn.get("min_growth", 10.0))
    min_hit = int(dn.get("min_hit", 60))

    if count >= min_count and growth_pct >= min_growth and hit_score >= min_hit:
        return "DO_NOW"
    return "WATCH"


def build_do_now_package(term: str, count: int, prev: Optional[int], growth_pct: float, hit: int) -> Dict[str, Any]:
    """
    给推送侧用的 do_now：标题模板、标签、上新动作、MJ prompt
    先提供一套固定模板（后面你接入 LLM 再升级）
    """
    why = []
    if prev is not None:
        why.append(f"24h 内 listings 规模从 {prev} → {count}（+{growth_pct:.1f}%）")
    else:
        why.append(f"当前 listings 规模：{count}（暂无 24h 前基线）")
    why.append(f"hit_score={hit}（规模+增速综合）")

    how = {
        "title_templates": [
            f"{term} Shirt | Trendy Minimal Design | Gift for {term.title()} Lovers",
            f"{term} Tee | Minimal Icon Style | Unisex Comfort Colors",
        ],
        "tags": [
            term,
            f"{term} shirt",
            "minimal design",
            "minimal icon",
            "trendy tee",
            "gift idea",
            "unisex tee",
            "comfort colors",
            "pod",
            "etsy seo",
        ],
        "variants": [
            "先做 1 个主图风格（minimal icon）+ 1 个备选（retro typography）",
            "标题含关键词 + 2 个长尾；上架后 24h 观察收藏与加购",
            "先上 3 个颜色、2 个尺码区间；有数据再扩色扩码",
        ],
        "image_prompts": [
            {
                "style": "mj",
                "prompt": f"minimal icon design of '{term}', clean vector style, bold simple silhouette, centered composition, high contrast, no text, print-ready, flat colors, t-shirt graphic",
            }
        ],
    }

    return {
        "why": why,
        "how": how,
        "risk": [
            "避免使用受版权保护的 IP/商标词；若含品牌/赛事名需二次核查",
            "若增长来自短期热点，建议少量上新先测试转化再扩量",
        ],
    }


def main() -> int:
    load_env()

    db_path = os.getenv("TRENDFORGE_DB", DB_DEFAULT)
    api_key = (os.getenv("ETSY_API_KEY") or os.getenv("ETSY_CLIENT_ID") or "").strip()

    if not api_key:
        raise RuntimeError("缺少 ETSY_API_KEY（或 ETSY_CLIENT_ID）。请在 .env.etsy 配置。")

    # 你可以在 .env.etsy 配：ETSY_SEED_TERMS=..., ...
    seed_raw = (os.getenv("ETSY_SEED_TERMS") or "").strip()
    if seed_raw:
        seeds = [s.strip() for s in seed_raw.split(",") if s.strip()]
    else:
        # 默认给一组 POD 常见方向（你后面可以替换成来自 GoogleTrends / EtsyHot / 站内搜索词）
        seeds = [
            "minimal icon",
            "retro golf typography",
            "pickleball typography",
            "minimal line art cat",
            "cowboy western",
            "coquette bow",
        ]

    # 参数
    market_country = (os.getenv("MARKET_COUNTRY") or "US").strip()
    category = (os.getenv("MARKET_CATEGORY") or "POD").strip()

    lookback_hours = int(os.getenv("ETSY_PREV_LOOKBACK_HOURS", "24"))
    sample_n = int(os.getenv("ETSY_SAMPLE_LISTINGS", "8"))

    # C2 规则阈值（写入 payload_json.rules.do_now）
    rules = {
        "do_now": {
            "min_count": int(os.getenv("DO_NOW_MIN_COUNT", "60")),
            "min_growth": float(os.getenv("DO_NOW_MIN_GROWTH", "10.0")),
            "min_hit": int(os.getenv("DO_NOW_MIN_HIT", "60")),
            "window_hours": lookback_hours,
            "source": "etsy_active_listings_total_count",
        }
    }

    conn = db_connect(db_path)
    try:
        ensure_tables(conn)

        ts_bucket = hour_bucket_iso(utc_now())
        pushed = 0

        for term in seeds:
            # 1) 拉 Etsy 数据（total_count + 示例 listings）
            try:
                total_count, listings = etsy_search_active_listings(
                    api_key=api_key,
                    keywords=term,
                    limit=sample_n,
                    offset=0,
                )
            except Exception as e:
                print(f"[etsy] term={term} fetch_error={repr(e)}")
                continue

            # 2) 写入 metrics，用于 prev_count
            upsert_metric(conn, term, ts_bucket, total_count, source="etsy_openapi_v3")

            prev = get_prev_count(conn, term, lookback_hours=lookback_hours)
            growth_pct = calc_growth_pct(total_count, prev)
            hit_score = calc_hit_score(total_count, growth_pct)
            action_level = decide_action_level(total_count, growth_pct, hit_score, rules=rules)

            # 3) 证据（用于卡片里的 evidence）
            ev_titles = [x.get("title", "") for x in listings if x.get("title")]
            ev_ids = [x.get("listing_id") for x in listings if x.get("listing_id")]
            ev_urls = [x.get("url", "") for x in listings if x.get("url")]

            evidence = {
                "listing_ids": ev_ids[:10],
                "titles": ev_titles[:10],
                "urls": ev_urls[:10],
                "sample_size": len(listings),
            }

            # 4) do_now 包（先固定模板，后面你要接 LLM 再升级）
            do_now_pkg = build_do_now_package(term, total_count, prev, growth_pct, hit_score)

            payload = {
                "source": "etsy_openapi_v3",
                "term": term,
                "ts_bucket": ts_bucket,
                "count": total_count,
                "prev_count": prev,
                "growth_pct": round(growth_pct, 2),
                "rules": rules,
                "evidence": evidence,
            }

            # 只有 DO_NOW 才写 do_now（WATCH 不需要）
            if action_level == "DO_NOW":
                payload["do_now"] = do_now_pkg

            # 5) 写入 trends（你的 push 卡片会从 payload_json 取）
            reason = f"etsy_count={total_count}, prev={prev}, growth={growth_pct:.1f}%, hit={hit_score}"

            insert_trend(
                conn,
                {
                    "created_at": utc_now_iso(),
                    "term": term,
                    # 你 trends.growth 原来就是数值：这里用 growth_pct（更可解释）
                    "growth": round(growth_pct, 2),
                    "hit_score": hit_score,
                    "action_level": action_level,
                    "payload_json": json.dumps(payload, ensure_ascii=False),
                    "country": market_country,
                    "category": category,
                    "reason": reason,
                },
            )

            pushed += 1
            print(f"[ok] term={term} action={action_level} count={total_count} prev={prev} growth={growth_pct:.1f}% hit={hit_score}")

            # 轻微限速，避免触发 QPS
            time.sleep(float(os.getenv("ETSY_SLEEP_SEC", "0.2")))

        print(f"[done] wrote trends={pushed} ts={ts_bucket} lookback={lookback_hours}h")
        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())