#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge Push Engine V4.1 (V3 Final + A3 Expansion Integration)
- 保留 V3 全量能力：
  - Feishu multi-group webhooks (FEISHU_WEBHOOKS_JSON)
  - group_main: digest (1 message)
  - group_vip: detail (N messages)
  - cooldown by channel+trend_id in push_log
  - feedback boost score supported (feedback_boost_score * FEEDBACK_BOOST_WEIGHT)
  - robust schema drift handling (auto ensure push_log columns)
  - --dry-run / --ignore-cooldown / --only-group / --limit
- 新增 A3（趋势扩散引擎）接入：
  - VIP detail 模式：若 design_ideas/design_prompts 不存在或为空，可自动扩散生成并落库（可开关）
  - VIP 卡片展示：Design Ideas + MJ Prompt（来自 design_prompts 优先，其次 trends.payload_json.mj_prompt）

Env:
  TRENDFORGE_DB=/root/trendforge-mvp/server/trendforge.db
  TRENDFORGE_WEB_URL=https://trendforgepro.com
  FEISHU_WEBHOOKS_JSON='{"group_main":"...","group_vip":"..."}'
  FEISHU_GROUP_CONFIG_JSON='{"group_vip":{"max_push":3,"cooldown_hours":120,"levels":["DO_NOW"]}}'
  FEEDBACK_BOOST_WEIGHT=10

A3 Env:
  VIP_AUTO_EXPAND=1          # 1=VIP 自动扩散补齐（默认开）
  VIP_AUTO_EXPAND_N=12       # 自动扩散生成数量
  VIP_SHOW_IDEAS=8           # VIP 卡片展示 ideas 数量（默认 8）
  VIP_SHOW_PROMPTS=1         # VIP 卡片展示 MJ prompt 条数（默认 1）

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


def env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return v.strip().lower() not in ("0", "false", "no", "off")


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


# -------------------------
# A3 tables + auto expand
# -------------------------
def ensure_a3_tables(conn: sqlite3.Connection) -> None:
    # 这两个表你项目里本来就规划要有，这里确保存在（存在则跳过）
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS design_ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_id INTEGER NOT NULL,
            idea TEXT NOT NULL
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS design_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            prompt TEXT NOT NULL
        );
        """
    )
    conn.commit()


def a3_has_ideas(conn: sqlite3.Connection, trend_id: int) -> bool:
    if not table_exists(conn, "design_ideas"):
        return False
    r = conn.execute("SELECT 1 FROM design_ideas WHERE trend_id=? LIMIT 1;", (trend_id,)).fetchone()
    return r is not None


def a3_try_auto_expand(conn: sqlite3.Connection, trend_id: int, term: str, n: int) -> bool:
    """
    best-effort 自动扩散：
    1) 如果 expansion_engine.py 可 import，则调用其生成逻辑并写入 design_ideas/design_prompts
    2) 否则做一个 fallback 规则生成（也会写库）
    返回：是否成功生成（或已存在则返回 True）
    """
    ensure_a3_tables(conn)

    if a3_has_ideas(conn, trend_id):
        return True

    term = (term or "").strip()
    if not term:
        return False

    # 1) 优先使用 expansion_engine（你 A3 已新增该文件时）
    try:
        from expansion_engine import generate_design_ideas, _seed_from  # type: ignore

        seed = _seed_from(term, trend_id=trend_id)  # type: ignore
        expansions = generate_design_ideas(term=term, n=n, seed=seed)  # type: ignore

        for item in expansions:
            cur = conn.execute("INSERT INTO design_ideas (trend_id, idea) VALUES (?, ?)", (trend_id, item.idea))
            idea_id = int(cur.lastrowid)
            conn.execute("INSERT INTO design_prompts (idea_id, prompt) VALUES (?, ?)", (idea_id, item.prompt))
        conn.commit()
        return True
    except Exception:
        pass

    # 2) fallback：保证 VIP 卡片不空
    styles = ["minimalist line art", "retro sunset", "vintage distressed", "cute kawaii", "bold cartoon", "sticker style"]
    moods = ["funny", "wholesome", "cozy", "aesthetic", "adventure", "minimal"]
    formats = ["t-shirt design", "sticker design", "poster illustration", "mug wrap design"]

    seed = abs(hash(f"{trend_id}:{term}")) % (2**31 - 1)
    rng = seed

    def pick(arr: List[str]) -> str:
        nonlocal rng
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        return arr[rng % len(arr)]

    for _ in range(max(1, n)):
        style = pick(styles)
        mood = pick(moods)
        fmt = pick(formats)
        idea = f"{style} {mood} {term}".strip()
        prompt = f"{fmt}, {term}, {style}, {mood}, vector, clean lines, center composition, print-ready, no text, no watermark"
        cur = conn.execute("INSERT INTO design_ideas (trend_id, idea) VALUES (?, ?)", (trend_id, idea))
        idea_id = int(cur.lastrowid)
        conn.execute("INSERT INTO design_prompts (idea_id, prompt) VALUES (?, ?)", (idea_id, prompt))
    conn.commit()
    return True


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


def fetch_mj_prompts(conn: sqlite3.Connection, trend_id: int, limit: int = 1) -> List[str]:
    """
    优先从 design_prompts join design_ideas 获取
    """
    out: List[str] = []

    if table_exists(conn, "design_prompts") and table_exists(conn, "design_ideas"):
        rows = conn.execute(
            """
            SELECT dp.prompt
            FROM design_prompts dp
            JOIN design_ideas di ON di.id = dp.idea_id
            WHERE di.trend_id=?
            ORDER BY dp.id DESC
            LIMIT ?;
            """,
            (trend_id, limit),
        ).fetchall()
        for r in rows:
            if r and r[0]:
                out.append(str(r[0]))

    # fallback: trends.payload_json.mj_prompt
    if not out:
        try:
            r2 = conn.execute(
                "SELECT json_extract(payload_json,'$.mj_prompt') FROM trends WHERE id=?;",
                (trend_id,),
            ).fetchone()
            if r2 and r2[0]:
                out.append(str(r2[0]))
        except Exception:
            pass

    return out


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
    mj_prompts: List[str],
    show_ideas: int,
    show_prompts: int,
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

    ideas = ideas[: max(1, show_ideas)]
    ideas_md = "\n".join([f"• {x}" for x in ideas]) if ideas else "• （暂无扩散词）"

    mj_prompts = [p.strip() for p in mj_prompts if p and p.strip()]
    mj_prompts = mj_prompts[: max(1, show_prompts)]
    if not mj_prompts:
        prompt_md = "（暂无 MJ Prompt）"
    elif len(mj_prompts) == 1:
        prompt_md = mj_prompts[0]
    else:
        prompt_md = "\n".join([f"[{i+1}] {p}" for i, p in enumerate(mj_prompts)])

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
            {"tag": "markdown", "content": f"### 🎯 Design Ideas (Top {len(ideas)})\n{ideas_md}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"### 🤖 MJ Prompt (Top {len(mj_prompts) if mj_prompts else 0})"},
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

    # A3 configs
    vip_auto_expand = env_bool("VIP_AUTO_EXPAND", True)
    vip_auto_expand_n = env_int("VIP_AUTO_EXPAND_N", 12)
    vip_show_ideas = env_int("VIP_SHOW_IDEAS", 8)
    vip_show_prompts = env_int("VIP_SHOW_PROMPTS", 1)

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
    ensure_a3_tables(conn)

    all_levels = sorted({lvl for g in groups for lvl in g.levels})
    cands = pick_candidates(conn, all_levels)

    print(f"[INFO] db={args.db}")
    print(f"[INFO] web={web}")
    print(f"[INFO] groups={[g.key for g in groups]}")
    print(f"[INFO] boost_weight={boost_weight} dry_run={bool(args.dry_run)} ignore_cooldown={bool(args.ignore_cooldown)}")
    print(f"[INFO] candidates={len(cands)}")
    print(f"[INFO] A3 vip_auto_expand={vip_auto_expand} vip_auto_expand_n={vip_auto_expand_n} show_ideas={vip_show_ideas} show_prompts={vip_show_prompts}")

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
            term = str(row_get(t, "term", "")).strip()

            # A3: VIP 自动补齐扩散（仅 detail 模式建议开启）
            if vip_auto_expand:
                try:
                    a3_try_auto_expand(conn, tid, term, vip_auto_expand_n)
                except Exception as _e:
                    # 不影响推送，最多卡片少 ideas
                    pass

            ideas = fetch_design_ideas(conn, tid, limit=vip_show_ideas)
            mj_prompts = fetch_mj_prompts(conn, tid, limit=vip_show_prompts)

            payload = build_detail_card(t, g, web, boost_weight, ideas, mj_prompts, vip_show_ideas, vip_show_prompts)
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