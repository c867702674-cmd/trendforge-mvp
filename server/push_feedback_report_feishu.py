#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge VIP Feedback Weekly Report (A1.6+ + A1.7 minimal hit-rate)

Includes:
- Current window stats (last N days)
- Previous window stats (previous N days) for WoW deltas
- New feedback samples in current window
- TOP3 by sales_7d_estimate (fallback hit)
- A1.7: DO_NOW hit-rate (minimal): hit/pushed within window using existing columns:
    last_action_level='DO_NOW' AND last_pushed_at>=since
    AND feedback_json not empty => hit

NOTE (minimal approach limitation):
- last_pushed_at stores only last push time; if a trend was pushed earlier but overwritten by a later push,
  it may affect denominator. This is acceptable for "minimal change" stage.

Usage:
  python3 /root/trendforge-mvp/server/push_feedback_report_feishu.py --days 7
  python3 ... --days 7 --dry-run 1
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import requests
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_DB_PATH = "/root/trendforge-mvp/server/trendforge.db"
DB_PATH = os.getenv("TRENDFORGE_DB_PATH", DEFAULT_DB_PATH)
WEB_URL = os.getenv("TRENDFORGE_WEB_URL", "https://trendforgepro.com").rstrip("/")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def getenv_str(key: str, default: str = "") -> str:
    v = os.getenv(key)
    return default if v is None else str(v).strip()


def getenv_json(key: str) -> Optional[dict]:
    raw = getenv_str(key, "")
    if not raw:
        return None
    return json.loads(raw)


def load_webhooks() -> Dict[str, str]:
    hooks = getenv_json("FEISHU_WEBHOOKS_JSON")
    if isinstance(hooks, dict) and hooks:
        return {str(k).strip(): str(v).strip() for k, v in hooks.items() if k and v}
    single = getenv_str("FEISHU_WEBHOOK", "")
    if single:
        return {"group_default": single}
    raise RuntimeError("No webhook found. Set FEISHU_WEBHOOKS_JSON or FEISHU_WEBHOOK.")


def load_group_config(webhooks: Dict[str, str]) -> Dict[str, dict]:
    cfg = getenv_json("FEISHU_GROUP_CONFIG_JSON") or {}
    out: Dict[str, dict] = {}
    for gid in webhooks.keys():
        c = cfg.get(gid, {}) if isinstance(cfg.get(gid, {}), dict) else {}
        out[gid] = {"name": str(c.get("name", gid))}
    return out


def is_vip_group(group_id: str, group_name: str) -> bool:
    gid = (group_id or "").lower()
    gname = (group_name or "").lower()
    return ("vip" in gid) or ("vip" in gname)


def db_connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def parse_iso(dt_str: str) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def safe_json_loads(s: str) -> Optional[dict]:
    if not s:
        return None
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def feishu_post(webhook: str, payload: dict) -> Tuple[bool, int, Any]:
    r = requests.post(webhook, json=payload, timeout=12)
    try:
        data = r.json()
    except Exception:
        data = r.text
    ok = (r.status_code == 200) and isinstance(data, dict) and data.get("code") == 0
    return ok, r.status_code, data


def fetch_feedback_rows(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, term, country, category, hit_score, growth,
               execution_feedback_json, execution_feedback_updated_at
        FROM trends
        WHERE execution_feedback_json IS NOT NULL AND execution_feedback_json <> ''
        ORDER BY id DESC
        """
    ).fetchall()


def _normalize_item(r: sqlite3.Row) -> Optional[Dict[str, Any]]:
    fb = safe_json_loads(r["execution_feedback_json"] or "")
    if not fb:
        return None

    updated_at = parse_iso(r["execution_feedback_updated_at"] or "")
    if not updated_at:
        updated_at = parse_iso((fb or {}).get("updated_at", ""))

    if not updated_at:
        return None

    uploaded = fb.get("uploaded")
    if uploaded is False:
        return None

    platform = (fb.get("platform") or "").strip() or "Unknown"
    d1 = fb.get("days_to_first_sale")
    s7 = fb.get("sales_7d_estimate")

    return {
        "id": int(r["id"]),
        "term": r["term"] or "",
        "country": r["country"] or "",
        "category": r["category"] or "",
        "hit": int(r["hit_score"] or 0),
        "growth": float(r["growth"] or 0.0),
        "platform": platform,
        "days_to_first_sale": d1 if isinstance(d1, int) else None,
        "sales_7d_estimate": s7 if isinstance(s7, int) else None,
        "updated_at": updated_at,
    }


def _agg(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    count = len(items)
    platform_counts: Dict[str, int] = {}
    for it in items:
        platform_counts[it["platform"]] = platform_counts.get(it["platform"], 0) + 1

    d1_vals = [it["days_to_first_sale"] for it in items if isinstance(it["days_to_first_sale"], int)]
    s7_vals = [it["sales_7d_estimate"] for it in items if isinstance(it["sales_7d_estimate"], int)]

    avg_d1 = round(sum(d1_vals) / len(d1_vals), 2) if d1_vals else None
    avg_s7 = round(sum(s7_vals) / len(s7_vals), 2) if s7_vals else None

    def score(it: Dict[str, Any]) -> Tuple[int, int]:
        s7 = it["sales_7d_estimate"] if isinstance(it["sales_7d_estimate"], int) else -1
        hit = it["hit"] if isinstance(it["hit"], int) else 0
        return (s7, hit)

    top3 = sorted(items, key=score, reverse=True)[:3]
    return {"count": count, "platform_counts": platform_counts, "avg_d1": avg_d1, "avg_s7": avg_s7, "top3": top3}


def compute_report(rows: List[sqlite3.Row], days: int) -> Dict[str, Any]:
    now = now_utc()
    cur_start = now - timedelta(days=days)
    prev_start = now - timedelta(days=days * 2)
    prev_end = cur_start

    normalized = []
    for r in rows:
        it = _normalize_item(r)
        if it:
            normalized.append(it)

    cur_items = [it for it in normalized if it["updated_at"] >= cur_start]
    prev_items = [it for it in normalized if prev_start <= it["updated_at"] < prev_end]

    cur_agg = _agg(cur_items)
    prev_agg = _agg(prev_items)

    cur_ids = {it["id"] for it in cur_items}
    prev_ids = {it["id"] for it in prev_items}
    new_ids = cur_ids - prev_ids
    new_items = [it for it in cur_items if it["id"] in new_ids]
    new_items = sorted(new_items, key=lambda x: x["updated_at"], reverse=True)[:5]

    return {
        "days": days,
        "cur_start": cur_start,
        "prev_start": prev_start,
        "prev_end": prev_end,
        "cur_items": cur_items,
        "prev_items": prev_items,
        "cur": cur_agg,
        "prev": prev_agg,
        "new_items": new_items,
    }


def compute_hit_rate(conn: sqlite3.Connection, since_dt: datetime) -> dict:
    """
    A1.7 minimal hit-rate based on existing columns:
      denominator: pushed DO_NOW within window (last_action_level='DO_NOW' and last_pushed_at>=since)
      numerator  : denominator AND feedback exists (execution_feedback_json not empty)

    Note:
      last_pushed_at is the latest push timestamp; minimal approach accepted.
    """
    since = iso_z(since_dt)

    cur = conn.execute(
        """
        SELECT COUNT(DISTINCT id) AS cnt
        FROM trends
        WHERE last_action_level = 'DO_NOW'
          AND last_pushed_at IS NOT NULL
          AND last_pushed_at >= ?
        """,
        (since,),
    ).fetchone()
    pushed = int(cur["cnt"] or 0)

    cur = conn.execute(
        """
        SELECT COUNT(DISTINCT id) AS cnt
        FROM trends
        WHERE last_action_level = 'DO_NOW'
          AND last_pushed_at IS NOT NULL
          AND last_pushed_at >= ?
          AND execution_feedback_json IS NOT NULL
          AND execution_feedback_json <> ''
        """,
        (since,),
    ).fetchone()
    hit = int(cur["cnt"] or 0)

    rate = round(hit / pushed * 100, 1) if pushed > 0 else 0.0
    return {"pushed": pushed, "hit": hit, "rate": rate}


def _fmt_delta(cur: Optional[float], prev: Optional[float], is_good_if_lower: bool = False) -> str:
    if cur is None and prev is None:
        return "—"
    if prev is None:
        return "（新增）"
    if cur is None:
        return "（缺失）"
    delta = cur - prev
    sign = "+" if delta > 0 else ""
    if delta == 0:
        return "（持平）"
    if is_good_if_lower:
        emoji = "🟢" if delta < 0 else "🟠"
    else:
        emoji = "🟢" if delta > 0 else "🟠"
    return f"{emoji}（{sign}{round(delta,2)}）"


def build_card(report: Dict[str, Any], hit_rate: Dict[str, Any]) -> dict:
    days = report["days"]
    cur = report["cur"]
    prev = report["prev"]
    cur_count = cur["count"]
    header = f"📊 VIP 回流周报（近 {days} 天）"

    if cur_count == 0:
        body = (
            f"本周期暂无回流记录。\n\n"
            f"你可以用 `write_execution_feedback.py` 先回填 1-2 条（内测阶段推荐），"
            f"周报会自动开始积累环比与命中率。"
        )
        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {"template": "blue", "title": {"tag": "plain_text", "content": header}},
                "elements": [{"tag": "markdown", "content": body}],
            },
        }

    plat_parts = [f"{k} {v}" for k, v in sorted(cur["platform_counts"].items(), key=lambda x: x[1], reverse=True)]
    plat_line = " · ".join(plat_parts) if plat_parts else "Unknown"

    lines: List[str] = []
    # A1.7: hit-rate line
    lines.append(f"🎯 **DO_NOW 回流命中率**：{hit_rate['rate']}%（{hit_rate['hit']}/{hit_rate['pushed']}）")
    lines.append(f"✅ **回流样本数**：{cur_count} {_fmt_delta(float(cur_count), float(prev['count']))}")

    if cur["avg_d1"] is not None:
        lines.append(f"⏱ **平均首单**：{cur['avg_d1']} 天 {_fmt_delta(cur['avg_d1'], prev['avg_d1'], is_good_if_lower=True)}")
    else:
        lines.append("⏱ **平均首单**：—")

    if cur["avg_s7"] is not None:
        lines.append(f"📈 **平均7天销量≈**：{cur['avg_s7']} {_fmt_delta(cur['avg_s7'], prev['avg_s7'])}")
    else:
        lines.append("📈 **平均7天销量≈**：—")

    lines.append(f"🛍 **平台分布**：{plat_line}")

    # New items
    new_items = report["new_items"]
    new_lines = []
    if new_items:
        for it in new_items:
            url = f"{WEB_URL}/#/trend/{it['id']}"
            meta = []
            if isinstance(it["days_to_first_sale"], int):
                meta.append(f"首单{it['days_to_first_sale']}天")
            if isinstance(it["sales_7d_estimate"], int):
                meta.append(f"7天≈{it['sales_7d_estimate']}")
            meta.append(it["platform"])
            new_lines.append(f"➕ [{it['term']}]({url})（" + " · ".join(meta) + "）")
    else:
        new_lines.append("（本周期暂无新增回流样本）")

    # TOP3
    top3 = cur["top3"]
    top_lines = []
    for i, it in enumerate(top3, start=1):
        url = f"{WEB_URL}/#/trend/{it['id']}"
        meta = []
        if isinstance(it["days_to_first_sale"], int):
            meta.append(f"首单{it['days_to_first_sale']}天")
        if isinstance(it["sales_7d_estimate"], int):
            meta.append(f"7天≈{it['sales_7d_estimate']}")
        meta.append(it["platform"])
        top_lines.append(f"{i}️⃣ [{it['term']}]({url})（" + " · ".join(meta) + "）")

    content = (
        "\n".join(lines)
        + "\n\n**➕ 本周期新增回流**\n"
        + "\n".join(new_lines)
        + "\n\n**🏆 TOP 3 回流趋势**\n"
        + "\n".join(top_lines)
        + "\n\n提示：回流数据可用 `write_execution_feedback.py` 手动回填（内测阶段推荐）。"
    )

    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {"template": "blue", "title": {"tag": "plain_text", "content": header}},
            "elements": [{"tag": "markdown", "content": content}],
        },
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7, help="lookback window")
    p.add_argument("--dry-run", type=int, default=0, help="1=do not send")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    days = max(1, args.days)
    dry_run = bool(args.dry_run)

    webhooks = load_webhooks()
    group_cfg = load_group_config(webhooks)

    vip_targets = []
    for gid, hook in webhooks.items():
        name = group_cfg.get(gid, {}).get("name", gid)
        if is_vip_group(gid, name):
            vip_targets.append((gid, name, hook))

    if not vip_targets:
        print("[WARN] No VIP group detected. Ensure VIP webhook id/name contains 'vip'.")
        return 0

    conn = db_connect(DB_PATH)
    try:
        rows = fetch_feedback_rows(conn)
        report = compute_report(rows, days)

        since_dt = now_utc() - timedelta(days=days)
        hit_rate = compute_hit_rate(conn, since_dt)
    finally:
        conn.close()

    card = build_card(report, hit_rate)

    print(
        f"[INFO] vip_targets={len(vip_targets)} days={days} dry_run={dry_run} "
        f"cur_feedback={report['cur']['count']} prev_feedback={report['prev']['count']} "
        f"do_now_pushed={hit_rate['pushed']} do_now_hit={hit_rate['hit']} rate={hit_rate['rate']}%"
    )

    if dry_run:
        print("[DONE] dry-run only, no send.")
        return 0

    ok_all = True
    for gid, name, hook in vip_targets:
        ok, status, data = feishu_post(hook, card)
        if ok:
            print(f"[OK] sent report to {gid} ({name})")
        else:
            ok_all = False
            print(f"[ERR] send report failed group={gid} http={status} resp={data}")

    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())