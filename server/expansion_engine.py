# /root/trendforge-mvp/server/expansion_engine.py
# TrendForge A3 - Trend Expansion Engine (Rule + Lexicon MVP)
# - Input: trend term
# - Output: design ideas + MJ prompts
# - Persist: design_ideas, design_prompts

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional


# ----------------------------
# Config
# ----------------------------
DEFAULT_DB_PATH = os.environ.get(
    "TRENDFORGE_DB_PATH",
    "/root/trendforge-mvp/server/trendforge.db",
)

DEFAULT_IDEAS_N = 12

# A3 词库（先用稳定可控的“可执行”词）
STYLE_PACKS = [
    "minimalist line art",
    "retro sunset",
    "vintage distressed",
    "cute kawaii",
    "bold cartoon",
    "watercolor",
    "sticker style",
    "patchwork quilt",
    "geometric",
    "hand-drawn sketch",
]

FORMAT_PACKS = [
    "t-shirt design",
    "hoodie graphic",
    "sticker design",
    "poster illustration",
    "mug wrap design",
]

QUALITY_PACKS = [
    "vector",
    "high contrast",
    "clean lines",
    "center composition",
    "transparent background",
    "print-ready",
    "no text",
    "no watermark",
    "no signature",
]

THEME_MODIFIERS = [
    "funny",
    "wholesome",
    "sarcastic",
    "motivational",
    "cozy",
    "adventure",
    "minimal",
    "aesthetic",
]

AUDIENCE_NICHES = [
    "for teachers",
    "for nurses",
    "for moms",
    "for dads",
    "for dog lovers",
    "for cat lovers",
    "for gamers",
    "for hikers",
    "for gym lovers",
]

OCCASIONS = [
    "Mother's Day",
    "Father's Day",
    "Halloween",
    "Christmas",
    "Valentine's Day",
    "St. Patrick's Day",
    "Thanksgiving",
    "Back to School",
]

NEGATIVE_TOKENS = [
    # MJ/SD 常用 negative（这里用作尾部约束语）
    "text",
    "logo",
    "watermark",
    "signature",
    "blurry",
    "low quality",
]


# ----------------------------
# Utils
# ----------------------------
def _now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _clean_term(term: str) -> str:
    term = (term or "").strip()
    term = re.sub(r"\s+", " ", term)
    return term


def _tokenize(term: str) -> List[str]:
    # 简单 token：英文按空格；中文/混合就直接整体
    if re.search(r"[\u4e00-\u9fff]", term):
        return [term]
    return [t for t in re.split(r"[^\w]+", term.lower()) if t]


def _seed_from(term: str, trend_id: Optional[int] = None) -> int:
    base = term
    if trend_id is not None:
        base = f"{trend_id}:{term}"
    return abs(hash(base)) % (2**31 - 1)


@dataclass
class ExpansionItem:
    idea: str
    prompt: str
    meta: Dict[str, Any]


# ----------------------------
# Core generator (MVP rules)
# ----------------------------
def generate_design_ideas(term: str, n: int = DEFAULT_IDEAS_N, seed: Optional[int] = None) -> List[ExpansionItem]:
    term = _clean_term(term)
    if not term:
        return []

    if seed is None:
        seed = _seed_from(term)

    rng = random.Random(seed)
    tokens = _tokenize(term)

    # 关键：把 term 变成“可执行”的结构化组合
    # 组合维度：style + modifier + niche/occasion + format
    ideas: List[ExpansionItem] = []
    used = set()

    # 生成策略权重：优先 niche，其次 occasion
    niche_pool = AUDIENCE_NICHES[:]
    occasion_pool = OCCASIONS[:]
    rng.shuffle(niche_pool)
    rng.shuffle(occasion_pool)

    for i in range(max(n * 3, 30)):
        style = rng.choice(STYLE_PACKS)
        fmt = rng.choice(FORMAT_PACKS)
        mood = rng.choice(THEME_MODIFIERS)

        add_on = None
        if i % 3 == 0 and niche_pool:
            add_on = niche_pool[i % len(niche_pool)]
        elif occasion_pool:
            add_on = occasion_pool[i % len(occasion_pool)]

        # idea 文本（给人看的“设计方向”）
        # 示例："retro sunset funny hiking dog for hikers"
        idea_parts = [style, mood, term]
        if add_on:
            idea_parts.append(add_on)
        idea = " ".join([p for p in idea_parts if p]).strip()
        idea = re.sub(r"\s+", " ", idea)

        key = idea.lower()
        if key in used:
            continue
        used.add(key)

        prompt = build_mj_prompt(term=term, style=style, mood=mood, add_on=add_on, fmt=fmt)

        meta = {
            "seed": seed,
            "style": style,
            "format": fmt,
            "mood": mood,
            "add_on": add_on,
            "tokens": tokens,
            "version": "a3_rulelex_v1",
        }

        ideas.append(ExpansionItem(idea=idea, prompt=prompt, meta=meta))
        if len(ideas) >= n:
            break

    return ideas


def build_mj_prompt(term: str, style: str, mood: str, add_on: Optional[str], fmt: str) -> str:
    # MJ prompt：稳定出图 + POD 友好
    core = f"{fmt}, {term}, {style}, {mood}"
    if add_on:
        core += f", {add_on}"

    quality = ", ".join(QUALITY_PACKS)
    neg = ", ".join([f"no {t}" for t in NEGATIVE_TOKENS])

    # 你后面可以把 --ar / --v 这些统一加在 push 或生成器层
    prompt = f"{core}, {quality}, {neg}"
    prompt = re.sub(r"\s+", " ", prompt).strip()
    return prompt


# ----------------------------
# DB persistence
# ----------------------------
def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(conn: sqlite3.Connection) -> None:
    # 你的 PROJECT_STATUS 里已存在这些表；这里做“存在即跳过”
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS design_ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_id INTEGER NOT NULL,
            idea TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS design_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            prompt TEXT NOT NULL
        )
        """
    )
    conn.commit()


def get_trend(conn: sqlite3.Connection, trend_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT id, term, country, category, action_level, payload_json, created_at FROM trends WHERE id = ?",
        (trend_id,),
    ).fetchone()
    return dict(row) if row else None


def existing_ideas_count(conn: sqlite3.Connection, trend_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(1) AS c FROM design_ideas WHERE trend_id = ?",
        (trend_id,),
    ).fetchone()
    return int(row["c"]) if row else 0


def persist_expansions(
    conn: sqlite3.Connection,
    trend_id: int,
    expansions: List[ExpansionItem],
    force: bool = False,
) -> Dict[str, Any]:
    ensure_tables(conn)

    if not force:
        c = existing_ideas_count(conn, trend_id)
        if c > 0:
            return {"ok": True, "skipped": True, "reason": "already_exists", "existing_count": c}

    # force：先清理旧的（简单粗暴，MVP 够用）
    if force:
        idea_ids = [r["id"] for r in conn.execute("SELECT id FROM design_ideas WHERE trend_id = ?", (trend_id,)).fetchall()]
        if idea_ids:
            conn.executemany("DELETE FROM design_prompts WHERE idea_id = ?", [(iid,) for iid in idea_ids])
        conn.execute("DELETE FROM design_ideas WHERE trend_id = ?", (trend_id,))
        conn.commit()

    inserted = []
    for item in expansions:
        cur = conn.execute(
            "INSERT INTO design_ideas (trend_id, idea) VALUES (?, ?)",
            (trend_id, item.idea),
        )
        idea_id = int(cur.lastrowid)
        conn.execute(
            "INSERT INTO design_prompts (idea_id, prompt) VALUES (?, ?)",
            (idea_id, item.prompt),
        )
        inserted.append({"idea_id": idea_id, "idea": item.idea, "prompt": item.prompt, "meta": item.meta})

    conn.commit()
    return {"ok": True, "skipped": False, "inserted": inserted, "inserted_count": len(inserted), "created_at": _now_iso()}


def expand_trend_to_db(
    db_path: str,
    trend_id: int,
    n: int = DEFAULT_IDEAS_N,
    force: bool = False,
) -> Dict[str, Any]:
    conn = _connect(db_path)
    try:
        trend = get_trend(conn, trend_id)
        if not trend:
            return {"ok": False, "error": f"trend_id {trend_id} not found"}

        term = _clean_term(trend.get("term", ""))
        seed = _seed_from(term, trend_id=trend_id)
        expansions = generate_design_ideas(term=term, n=n, seed=seed)

        persisted = persist_expansions(conn, trend_id=trend_id, expansions=expansions, force=force)
        return {"ok": True, "trend": trend, "n": n, "force": force, "result": persisted}
    finally:
        conn.close()


# ----------------------------
# CLI
# ----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB_PATH)
    ap.add_argument("--trend-id", type=int, required=True)
    ap.add_argument("--n", type=int, default=DEFAULT_IDEAS_N)
    ap.add_argument("--force", type=int, default=0)
    args = ap.parse_args()

    out = expand_trend_to_db(db_path=args.db, trend_id=args.trend_id, n=args.n, force=bool(args.force))
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()