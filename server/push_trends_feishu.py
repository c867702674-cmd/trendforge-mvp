#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge Push Engine V3 (Final)
- Feishu multi-group webhooks
- group_main: digest (1 message)
- group_vip: detail (N messages)
- cooldown by channel+trend_id in push_log
- feedback boost score supported (feedback_boost_score * FEEDBACK_BOOST_WEIGHT)
- robust schema drift handling (auto ensure push_log columns)

Usage:
  set -a; source /root/trendforge-mvp/.env.feishu; set +a
  cd /root/trendforge-mvp/server
  python push_trends_feishu.py --dry-run 1
  python push_trends_feishu.py --dry-run 0
  python push_trends_feishu.py --ignore-cooldown 1 --dry-run 0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import urllib.request

TZ_UTC = timezone.utc


def now_utc_iso() -> str:
    return datetime.now(TZ_UTC).strftime("%Y-%m-%d %H:%M:%S")


def eprint(*a: Any) -> None:
    print(*a, file=sys.stderr)


def env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return v


def env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except Exception:
        return default


def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(float(v))
    except Exception:
        return default


def parse_json_env(name: str, default: Any) -> Any:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return json.loads(raw)
    except Exception:
        # allow single quotes JSON-ish
        try:
            return json.loads(raw.replace("'", '"'))
        except Exception as e:
            raise ValueError(f"Invalid JSON in env {name}: {e}\nraw={raw!r}") from e


def row_get(r: sqlite3.Row, key: str, default: Any = None) -> Any:
    try:
        return r[key]
    except Exception:
        return default


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None


def column_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    try:
        cur = conn.execute(f"PRAGMA table_info({table});")
        for rr in cur.fetchall():
            if rr[1] == col:
                return True
    except Exception:
        return False
    return False


def ensure_push_log_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS push_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      channel TEXT,
      webhook_token TEXT,
      message_hash TEXT,
      sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      channel_name TEXT,
      ok INTEGER,
      http_status INTEGER,
      feishu_code INTEGER,
      feishu_msg TEXT,
      feishu_body TEXT,
      error TEXT,
      trend_id INTEGER,
      created_at TEXT
    );
    """
    )
    # add missing columns (best-effort)
    for col, ddl in [
        ("trend_id", "ALTER TABLE push_log ADD COLUMN trend_id INTEGER;"),
        ("channel", "ALTER TABLE push_log ADD COLUMN channel TEXT;"),
        ("channel_name", "ALTER TABLE push_log ADD COLUMN channel_name TEXT;"),
        ("webhook_token", "ALTER TABLE push_log ADD COLUMN webhook_token TEXT;"),
        ("message_hash", "ALTER TABLE push_log ADD COLUMN message_hash TEXT;"),
        ("sent_at", "ALTER TABLE push_log ADD COLUMN sent_at DATETIME;"),
        ("ok", "ALTER TABLE push_log ADD COLUMN ok INTEGER;"),
        ("http_status", "ALTER TABLE push_log ADD COLUMN http_status INTEGER;"),
        ("feishu_code", "ALTER TABLE push_log ADD COLUMN feishu_code INTEGER;"),
        ("feishu_msg", "ALTER TABLE push_log ADD COLUMN feishu_msg TEXT;"),
        ("feishu_body", "ALTER TABLE push_log ADD COLUMN feishu_body TEXT;"),
        ("error", "ALTER TABLE push_log ADD COLUMN error TEXT;"),
        ("created_at", "ALTER TABLE push_log ADD COLUMN created_at TEXT;"),
    ]:
        if not column_exists(conn, "push_log", col):
            try:
                conn.execute(ddl)
            except Exception:
                pass
    conn.commit()


@dataclass
class GroupCfg:
    key: str
    name: str
    tier: str  # main/vip
    mode: str  # digest/detail
    max_push: int
    cooldown_hours: int
    levels: List[str]
    template: str  # header color template


def load_groups(webhooks: Dict[str, str], cfg_json: Optional[Dict[str, Any]]) -> List[GroupCfg]:
    # defaults
    defaults: Dict[str, Dict[str, Any]] = {
        "group_main": {
            "name": "北美POD趋势指南（通用群）",
            "tier": "main",
            "mode": "digest",
            "max_push": 5,
            "cooldown_hours": 72,
            "levels": ["DO_NOW", "WATCH"],
            "template": "orange",
        },
        "group_vip": {
            "name": "北美POD趋势VIP群",
            "tier": "vip",
            "mode": "detail",
            "max_push": 3,
            "cooldown_hours": 120,
            "levels": ["DO_NOW"],
            "template": "purple",
        },
    }
    cfg_json = cfg_json or {}
    out: List[GroupCfg] = []
    for k, _url in webhooks.items():
        c = defaults.get(
            k,
            {
                "name": k,
                "tier": "main",
                "mode": "detail",
                "max_push": 5,
                "cooldown_hours": 72,
                "levels": ["DO_NOW"],
                "template": "blue",
            },
        )
        c2 = dict(c)
        if k in cfg_json:
            for kk, vv in (cfg_json.get(k) or {}).items():
                c2[kk] = vv
        out.append(
            GroupCfg(
                key=k,
                name=str(c2.get("name", k)),
                tier=str(c2.get("tier", "main")),
                mode=str(c2.get("mode", "detail")),
                max_push=int(c2.get("max_push", 5)),
                cooldown_hours=int(c2.get("cooldown_hours", 72)),
                levels=list(c2.get("levels", ["DO_NOW"])),
                template=str(c2.get("template", "orange")),
            )
        )
    # stable order
    out.sort(key=lambda x: (0 if x.key == "group_main" else 1, x.key))
    return out


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def http_post_json(url: str, payload: Dict[str, Any], timeout: int = 15) -> Tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.getcode(), body


def fetch_design_ideas(conn: sqlite3.Connection, trend_id: int, limit: int = 8) -> List[str]:
    if not table_exists(conn, "design_ideas"):
        return []
    rows = conn.execute(
        "SELECT idea FROM design_ideas WHERE trend_id=? ORDER BY id DESC LIMIT ?;",
        (trend_id, limit),
    ).fetchall()
    out: List[str] = []
    for r in rows:
        v = r[0] if not isinstance(r, sqlite3.Row) else (r["idea"] if "idea" in r.keys() else None)
        if v:
            out.append(str(v))
    return out


def fetch_mj_prompt(conn: sqlite3.Connection, trend_id: int) -> Optional[str]:
    # prefer design_prompts joined via idea_id if available
    if table_exists(conn, "design_prompts") and table_exists(conn, "design_ideas"):
        r = conn.execute(
            """
        SELECT dp.prompt
        FROM design_prompts dp
        JOIN design_ideas di ON di.id = dp.idea_id
        WHERE di.trend_id=?
        ORDER BY dp.id DESC
        LIMIT 1;
        """,
            (trend_id,),
        ).fetchone()
        if r:
            return str(r[0])
    # fallback: trends.payload_json.mj_prompt if exists
    try:
        r2 = conn.execute(
            "SELECT json_extract(payload_json,'$.mj_prompt') FROM trends WHERE id=?;",
            (trend_id,),
        ).fetchone()
        if r2 and r2[0]:
            return str(r2[0])
    except Exception:
        pass
    return None


def parse_source_from_payload(payload_json: Any) -> str:
    try:
        if not payload_json:
            return "unknown"
        j = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
        if isinstance(j, dict) and j.get("source"):
            return str(j.get("source"))
    except Exception:
        pass
    return "unknown"


def pick_candidates(conn: sqlite3.Connection, levels: List[str]) -> List[sqlite3.Row]:
    q = """
    SELECT id, term, country, category,
           COALESCE(hit_score, 0) AS hit_score,
           COALESCE(growth, 0) AS growth,
           COALESCE(action_level, '') AS action_level,
           COALESCE(date, substr(COALESCE(created_at,''),1,10)) AS date,
           COALESCE(created_at, '') AS created_at,
           COALESCE(payload_json, '') AS payload_json,
           COALESCE(feedback_boost_score, 0) AS feedback_boost_score
    FROM trends
    WHERE term IS NOT NULL AND trim(term) != ''
      AND COALESCE(action_level,'') IN ({})
    ;
    """.format(
        ",".join(["?"] * len(levels))
    )
    return conn.execute(q, tuple(levels)).fetchall()


def pushed_recently(conn: sqlite3.Connection, channel: str, trend_id: int, cooldown_hours: int, ignore: bool) -> bool:
    if ignore:
        return False
    if not table_exists(conn, "push_log") or not column_exists(conn, "push_log", "sent_at"):
        return False
    since = datetime.now(TZ_UTC) - timedelta(hours=cooldown_hours)
    r = conn.execute(
        "SELECT 1 FROM push_log WHERE channel=? AND trend_id=? AND sent_at >= ? LIMIT 1;",
        (channel, trend_id, since.strftime("%Y-%m-%d %H:%M:%S")),
    ).fetchone()
    return r is not None


def calc_final(hit_score: float, boost_score: float, boost_weight: float) -> float:
    return float(hit_score) + float(boost_score) * float(boost_weight)


def fmt_metric_line(country: str, category: str, hit: float, growth: float) -> str:
    return f"`{country}` · `{category}` · hit `{int(hit)}` · growth `{growth:.1f}`"


def _button(text: str, url: str, style: str = "default") -> Dict[str, Any]:
    return {
        "tag": "button",
        "text": {"tag": "plain_text", "content": text},
        "type": style,
        "url": url,
    }


def build_detail_card(
    trend: sqlite3.Row,
    group: GroupCfg,
    web: str,
    boost_weight: float,
    ideas: List[str],
    mj_prompt: Optional[str],
) -> Dict[str, Any]:
    tid = int(row_get(trend, "id", 0))
    term = str(row_get(trend, "term", "")).strip()
    country = str(row_get(trend, "country", "US") or "US")
    category = str(row_get(trend, "category", "POD") or "POD")
    hit = float(row_get(trend, "hit_score", 0) or 0)
    growth = float(row_get(trend, "growth", 0) or 0)
    lvl = str(row_get(trend, "action_level", "") or "").strip() or "WATCH"
    boost = float(row_get(trend, "feedback_boost_score", 0) or 0)
    final = calc_final(hit, boost, boost_weight)
    src = parse_source_from_payload(row_get(trend, "payload_json", ""))

    header_title = f"🔥 {lvl} · #{tid} · {group.name}"
    detail_url = f"{web.rstrip('/')}/?trend_id={tid}"

    # 占位：未来接“复制上架”
    amazon_url = f"{web.rstrip('/')}/listing/amazon?trend_id={tid}"
    etsy_url = f"{web.rstrip('/')}/listing/etsy?trend_id={tid}"

    ideas_md = "\n".join([f"• {x}" for x in ideas[:8]]) if ideas else "• （暂无扩散词，下一步接 A3 扩散引擎）"
    prompt_md = (mj_prompt or "").strip() or "（暂无 MJ Prompt，先跑 A4 生成 prompt）"

    card: Dict[str, Any] = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": header_title},
            "template": group.template,
        },
        "elements": [
            {"tag": "markdown", "content": f"## **{term}**\n{fmt_metric_line(country, category, hit, growth)}"},
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"📈 **final**\n`{final:.0f}`"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"👍 **boost**\n`{boost:.0f}`"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"🧊 **cooldown**\n`{group.cooldown_hours}h`"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"🎛️ **tier/mode**\n`{group.tier}/{group.mode}`"}},
                ],
            },
            {"tag": "hr"},
            {"tag": "markdown", "content": f"### 🎯 Design Ideas\n{ideas_md}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": "### 🤖 MJ Prompt"},
            {"tag": "markdown", "content": f"```text\n{prompt_md}\n```"},
            {
                "tag": "action",
                "actions": [
                    _button("打开 TrendForge 详情", detail_url, "primary"),
                    _button("一键上架 Amazon（占位）", amazon_url, "default"),
                    _button("一键上架 Etsy（占位）", etsy_url, "default"),
                ],
            },
            {
                "tag": "note",
                "elements": [
                    {"tag": "plain_text", "content": f"source: {src}"},
                    {"tag": "plain_text", "content": f"sent: {now_utc_iso()} UTC"},
                ],
            },
        ],
    }
    return {"msg_type": "interactive", "card": card}


def build_digest_card(
    trends: List[sqlite3.Row],
    group: GroupCfg,
    web: str,
    boost_weight: float,
) -> Dict[str, Any]:
    items: List[str] = []
    for t in trends:
        tid = int(row_get(t, "id", 0))
        term = str(row_get(t, "term", "")).strip()
        lvl = str(row_get(t, "action_level", "") or "").strip() or "WATCH"
        hit = float(row_get(t, "hit_score", 0) or 0)
        boost = float(row_get(t, "feedback_boost_score", 0) or 0)
        final = calc_final(hit, boost, boost_weight)
        url = f"{web.rstrip('/')}/?trend_id={tid}"
        badge = "🔥" if lvl == "DO_NOW" else "👀"
        items.append(f"{badge} **#{tid} {term}** · `final {final:.0f}` · [打开]({url})")

    md = "\n".join([f"{i+1}. {items[i]}" for i in range(len(items))]) if items else "（本轮无可推送条目）"
    header_title = f"🧾 DIGEST · {group.name}"
    list_url = f"{web.rstrip('/')}/"

    card: Dict[str, Any] = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": header_title}, "template": group.template},
        "elements": [
            {"tag": "markdown", "content": f"### 今日可执行清单（Top {len(items)}）\n{md}"},
            {"tag": "action", "actions": [_button("打开 TrendForge 列表", list_url, "primary")]},
            {
                "tag": "note",
                "elements": [
                    {"tag": "plain_text", "content": f"sent: {now_utc_iso()} UTC"},
                    {"tag": "plain_text", "content": f"mode: digest · cooldown: {group.cooldown_hours}h"},
                ],
            },
        ],
    }
    return {"msg_type": "interactive", "card": card}


def log_push(
    conn: sqlite3.Connection,
    channel: str,
    channel_name: str,
    webhook_url: str,
    message_hash: str,
    ok: int,
    http_status: int,
    feishu_code: Optional[int],
    feishu_msg: Optional[str],
    feishu_body: str,
    error: Optional[str],
    trend_id: Optional[int],
) -> None:
    token = webhook_url.rsplit("/", 1)[-1] if webhook_url else ""
    conn.execute(
        """INSERT INTO push_log
           (channel, channel_name, webhook_token, message_hash, sent_at, ok, http_status, feishu_code, feishu_msg, feishu_body, error, trend_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            channel,
            channel_name,
            token,
            message_hash,
            now_utc_iso(),
            int(ok),
            int(http_status),
            int(feishu_code) if feishu_code is not None else None,
            feishu_msg,
            (feishu_body or "")[:20000],
            error,
            int(trend_id) if trend_id is not None else None,
            now_utc_iso(),
        ),
    )
    conn.commit()


def pick_for_group(
    conn: sqlite3.Connection,
    group: GroupCfg,
    all_cands: List[sqlite3.Row],
    boost_weight: float,
    ignore_cooldown: bool,
) -> List[sqlite3.Row]:
    filtered: List[Tuple[float, sqlite3.Row]] = []
    for r in all_cands:
        lvl = str(row_get(r, "action_level", "") or "").strip()
        if lvl not in group.levels:
            continue
        tid = int(row_get(r, "id", 0))
        if tid <= 0:
            continue
        if pushed_recently(conn, group.key, tid, group.cooldown_hours, ignore_cooldown):
            continue
        hit = float(row_get(r, "hit_score", 0) or 0)
        boost = float(row_get(r, "feedback_boost_score", 0) or 0)
        final = calc_final(hit, boost, boost_weight)
        filtered.append((final, r))

    filtered.sort(key=lambda x: x[0], reverse=True)
    return [r for _final, r in filtered[: group.max_push]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=env_str("TRENDFORGE_DB", "/root/trendforge-mvp/server/trendforge.db"))
    ap.add_argument("--dry-run", type=int, default=0)
    ap.add_argument("--only-group", default="")
    ap.add_argument("--ignore-cooldown", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="override max_push for all groups (0=use group cfg)")
    args = ap.parse_args()

    web = env_str("TRENDFORGE_WEB_URL", env_str("WEB_URL", "https://trendforgepro.com")) or "https://trendforgepro.com"
    boost_weight = env_float("FEEDBACK_BOOST_WEIGHT", 10.0)

    webhooks = parse_json_env("FEISHU_WEBHOOKS_JSON", {})
    if not isinstance(webhooks, dict) or not webhooks:
        eprint("[FATAL] FEISHU_WEBHOOKS_JSON missing or invalid.")
        return 2

    group_cfg_json = parse_json_env("FEISHU_GROUP_CONFIG_JSON", {})
    groups = load_groups(webhooks, group_cfg_json)

    if args.only_group:
        groups = [g for g in groups if g.key == args.only_group]
        if not groups:
            eprint(f"[FATAL] only-group={args.only_group} not found in FEISHU_WEBHOOKS_JSON.")
            return 2

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ensure_push_log_schema(conn)

    all_levels = sorted({lvl for g in groups for lvl in g.levels})
    cands = pick_candidates(conn, all_levels)

    print(f"[INFO] db={args.db}")
    print(f"[INFO] web={web}")
    print(f"[INFO] groups={[g.key for g in groups]}")
    print(f"[INFO] boost_weight={boost_weight} dry_run={bool(args.dry_run)} ignore_cooldown={bool(args.ignore_cooldown)}")
    print(f"[INFO] candidates={len(cands)}")

    pushed_total = 0
    failed_total = 0

    for g0 in groups:
        g = g0
        if args.limit and args.limit > 0:
            g = GroupCfg(**{**g.__dict__, "max_push": args.limit})

        picked = pick_for_group(conn, g, cands, boost_weight, bool(args.ignore_cooldown))
        print(
            f"\n[GROUP] {g.key} ({g.name}) tier={g.tier} mode={g.mode} levels={g.levels} "
            f"limit={g.max_push} cooldown_hours={g.cooldown_hours} picked={len(picked)}"
        )
        if not picked:
            continue

        url = webhooks[g.key]

        if g.mode == "digest":
            payload = build_digest_card(picked, g, web, boost_weight)
            mh = sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            if args.dry_run:
                print(f"[DRY] send digest to {g.key} message_hash={mh} items={len(picked)}")
                continue
            try:
                http_status, body = http_post_json(url, payload)
                fei_code = None
                fei_msg = None
                try:
                    bj = json.loads(body)
                    fei_code = bj.get("code") if isinstance(bj, dict) else None
                    fei_msg = bj.get("msg") if isinstance(bj, dict) else None
                except Exception:
                    pass
                ok = 1 if (http_status == 200 and (fei_code in (0, None))) else 0
                for t in picked:
                    log_push(conn, g.key, g.name, url, mh, ok, http_status, fei_code, fei_msg, body, None, int(row_get(t, "id", 0)))
                pushed_total += len(picked) if ok else 0
                failed_total += 0 if ok else len(picked)
                print(f"[DONE] {g.key} digest sent ok={ok} http={http_status}")
            except Exception as e:
                for t in picked:
                    log_push(conn, g.key, g.name, url, mh, 0, 0, None, None, "", str(e), int(row_get(t, "id", 0)))
                failed_total += len(picked)
                eprint(f"[ERROR] {g.key} digest send failed: {e}")
            continue

        # detail mode
        for t in picked:
            tid = int(row_get(t, "id", 0))
            ideas = fetch_design_ideas(conn, tid, limit=8)
            mj = fetch_mj_prompt(conn, tid)
            payload = build_detail_card(t, g, web, boost_weight, ideas, mj)
            mh = sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True))

            hit = float(row_get(t, "hit_score", 0) or 0)
            boost = float(row_get(t, "feedback_boost_score", 0) or 0)
            final = calc_final(hit, boost, boost_weight)
            print(
                f"[PICK] {g.key} id={tid} level={row_get(t,'action_level','')} final={final:.0f} "
                f"boost={boost:.0f} term={row_get(t,'term','')}"
            )

            if args.dry_run:
                continue

            try:
                http_status, body = http_post_json(url, payload)
                fei_code = None
                fei_msg = None
                try:
                    bj = json.loads(body)
                    fei_code = bj.get("code") if isinstance(bj, dict) else None
                    fei_msg = bj.get("msg") if isinstance(bj, dict) else None
                except Exception:
                    pass
                ok = 1 if (http_status == 200 and (fei_code in (0, None))) else 0
                log_push(conn, g.key, g.name, url, mh, ok, http_status, fei_code, fei_msg, body, None, tid)
                if ok:
                    pushed_total += 1
                else:
                    failed_total += 1
                time.sleep(0.2)
            except Exception as e:
                log_push(conn, g.key, g.name, url, mh, 0, 0, None, None, "", str(e), tid)
                failed_total += 1
                eprint(f"[ERROR] {g.key} send failed id={tid}: {e}")

    print(f"\n[DONE] pushed_total={pushed_total} failed_total={failed_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())