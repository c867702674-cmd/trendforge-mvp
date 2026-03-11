#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""TrendForge - Feishu Push Engine V7
---------------------------------
Digest (group_main):
  - Top DO_NOW trends (term + hit_score)

Detail (group_vip):
  - Trend + Top design ideas (from design_ideas)
  - + MJ prompts (from design_prompts) for top ideas

DB tables used:
  - trends
  - design_ideas
  - design_prompts
  - push_log

Env:
  DB_PATH
  FEISHU_WEBHOOKS_JSON   {"group_main":"https://...","group_vip":"https://..."}
  COUNTRY                optional, default no filter
  MAIN_TOP_N             default 8
  VIP_TOP_N              default 3
  VIP_IDEAS_PER_TREND    default 8
  VIP_PROMPTS_PER_TREND  default 3
  PUSH_COOLDOWN_MIN      default 240 (minutes)
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import urllib.request

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
COUNTRY = os.getenv("COUNTRY", "").strip()
MAIN_TOP_N = int(os.getenv("MAIN_TOP_N", "8"))
VIP_TOP_N = int(os.getenv("VIP_TOP_N", "3"))
VIP_IDEAS_PER_TREND = int(os.getenv("VIP_IDEAS_PER_TREND", "8"))
VIP_PROMPTS_PER_TREND = int(os.getenv("VIP_PROMPTS_PER_TREND", "3"))
PUSH_COOLDOWN_MIN = int(os.getenv("PUSH_COOLDOWN_MIN", "240"))

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def utc_now_iso() -> str:
    return utc_now().isoformat()

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_webhooks() -> Dict[str, str]:
    raw = os.getenv("FEISHU_WEBHOOKS_JSON", "").strip()
    if not raw:
        raise RuntimeError("FEISHU_WEBHOOKS_JSON is empty")
    return json.loads(raw)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def in_cooldown(conn: sqlite3.Connection, channel: str, msg_hash: str) -> bool:
    cur = conn.cursor()
    cutoff = utc_now() - timedelta(minutes=PUSH_COOLDOWN_MIN)
    cur.execute(
        """SELECT 1 FROM push_log
           WHERE channel=? AND message_hash=? AND sent_at >= ?
           LIMIT 1""",
        (channel, msg_hash, cutoff.isoformat())
    )
    return cur.fetchone() is not None

def log_push(conn: sqlite3.Connection, channel: str, trend_id: int, msg_hash: str, ok: int, http_status: int, error: str):
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO push_log(channel, trend_id, message_hash, sent_at, ok, http_status, error)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (channel, trend_id, msg_hash, utc_now_iso(), ok, http_status, error)
    )
    conn.commit()

def post_feishu(webhook: str, payload: Dict[str, Any]) -> (int, str):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(webhook, data=data, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="ignore")
            return status, body
    except Exception as e:
        return 0, str(e)

def fetch_do_now_trends(conn: sqlite3.Connection, limit: int) -> List[sqlite3.Row]:
    cur = conn.cursor()
    where = ["action_level='DO_NOW'"]
    params: List[Any] = []
    if COUNTRY:
        where.append("country=?")
        params.append(COUNTRY)
    cur.execute(
        f"""SELECT id, date, country, term, hit_score
            FROM trends
            WHERE {' AND '.join(where)}
            ORDER BY hit_score DESC
            LIMIT ?""",
        (*params, limit)
    )
    return cur.fetchall()

def fetch_ideas(conn: sqlite3.Connection, trend_id: int, limit: int) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """SELECT id, idea, score
           FROM design_ideas
           WHERE trend_id=?
           ORDER BY score DESC, id ASC
           LIMIT ?""",
        (trend_id, limit)
    )
    return cur.fetchall()

def fetch_prompts(conn: sqlite3.Connection, idea_ids: List[int], limit: int) -> List[sqlite3.Row]:
    if not idea_ids or limit <= 0:
        return []
    cur = conn.cursor()
    q = ",".join(["?"]*len(idea_ids))
    cur.execute(
        f"""SELECT idea_id, prompt, score
            FROM design_prompts
            WHERE idea_id IN ({q})
            ORDER BY score DESC
            LIMIT ?""",
        (*idea_ids, limit)
    )
    return cur.fetchall()

def digest_payload(trends: List[sqlite3.Row]) -> Dict[str, Any]:
    lines = []
    for i, t in enumerate(trends, 1):
        lines.append(f"{i}. {t['term']}  (score {float(t['hit_score'] or 0):.0f})")
    content = "\n".join(lines) if lines else "No DO_NOW trends."
    return {"msg_type": "text", "content": {"text": "🔥 TrendForge Digest (DO_NOW)\n\n" + content}}

def vip_payload(trend: sqlite3.Row, ideas: List[sqlite3.Row], prompts: List[sqlite3.Row]) -> Dict[str, Any]:
    idea_lines = [f"{i}. {r['idea']}" for i, r in enumerate(ideas, 1)]
    prompt_lines = [f"- {p['prompt']}" for p in prompts[:VIP_PROMPTS_PER_TREND]]
    text = (
        "🚀 TrendForge VIP (DO_NOW)\n\n"
        f"Trend: {trend['term']}\n"
        f"Score: {float(trend['hit_score'] or 0):.0f}\n\n"
        "Design Ideas:\n" + ("\n".join(idea_lines) if idea_lines else "(no ideas yet)") + "\n\n"
        "MJ Prompts:\n" + ("\n".join(prompt_lines) if prompt_lines else "(no prompts yet)")
    )
    return {"msg_type": "text", "content": {"text": text}}

def main():
    conn = connect()
    webhooks = load_webhooks()

    if "group_main" in webhooks:
        trends = fetch_do_now_trends(conn, MAIN_TOP_N)
        payload = digest_payload(trends)
        msg_hash = sha1(json.dumps(payload, ensure_ascii=False))
        if not in_cooldown(conn, "group_main", msg_hash):
            status, body = post_feishu(webhooks["group_main"], payload)
            ok = 1 if status and 200 <= status < 300 else 0
            log_push(conn, "group_main", 0, msg_hash, ok, status or 0, "" if ok else body[:500])
        else:
            print("group_main: skipped due to cooldown/dedup")

    if "group_vip" in webhooks:
        vip_trends = fetch_do_now_trends(conn, VIP_TOP_N)
        for tr in vip_trends:
            ideas = fetch_ideas(conn, int(tr["id"]), VIP_IDEAS_PER_TREND)
            idea_ids = [int(r["id"]) for r in ideas]
            prompts = fetch_prompts(conn, idea_ids, VIP_PROMPTS_PER_TREND)

            payload = vip_payload(tr, ideas, prompts)
            msg_hash = sha1(json.dumps(payload, ensure_ascii=False))

            if in_cooldown(conn, "group_vip", msg_hash):
                print(f"group_vip: skipped trend_id={tr['id']} due to cooldown/dedup")
                continue

            status, body = post_feishu(webhooks["group_vip"], payload)
            ok = 1 if status and 200 <= status < 300 else 0
            log_push(conn, "group_vip", int(tr["id"]), msg_hash, ok, status or 0, "" if ok else body[:500])

    conn.close()
    print("Feishu Push V7 done.")

if __name__ == "__main__":
    main()
