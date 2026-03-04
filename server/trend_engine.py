# server/trend_engine.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import math
import re
import sqlite3
import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


DEFAULT_STOPWORDS: Set[str] = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "by", "is", "are",
    # POD common fillers (tune later)
    "gift", "gifts", "shirt", "shirts", "tee", "tees", "tshirt", "tshirts", "hoodie", "hoodies",
    "poster", "posters", "print", "prints", "wall", "art", "svg", "png", "jpg", "digital",
}


@dataclass
class TrendItem:
    """Unified input item (source-agnostic)."""
    title: str
    tags: List[str]
    shop_id: Optional[int] = None
    item_id: Optional[int] = None  # listing_id or other id
    created_at: Optional[str] = None
    url: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass
class TrendScore:
    term: str
    hit_score: float
    action_level: str
    growth: float
    metrics: Dict[str, Any]
    evidence: List[Dict[str, Any]]


def utc_now_iso() -> str:
    # Keep it simple: your feed script already uses timezone-aware.
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def log2p(x: float) -> float:
    return math.log2(1.0 + max(0.0, x))


def normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\s]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(title: str, tags: List[str], stopwords: Set[str]) -> List[str]:
    parts: List[str] = []
    if title:
        parts.append(title)
    if tags:
        parts.extend(tags)
    text = normalize_text(" ".join(parts))
    toks = [t for t in text.split(" ") if t and t not in stopwords and len(t) >= 2]
    return toks


def extract_2grams(tokens: List[str], stopwords: Set[str]) -> List[str]:
    grams: List[str] = []
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i + 1]
        if a in stopwords or b in stopwords:
            continue
        grams.append(f"{a} {b}")
    return grams


class TrendEngine:
    """
    2-gram + hourly windows:
      - velocity (3h vs 24h baseline)
      - acceleration (1h vs 6h hourly avg)
      - breadth (unique shops in 6h)
      - novelty (new items share in 6h) if conn provided
    """
    def __init__(
        self,
        stopwords: Optional[Set[str]] = None,
        min_mentions_6h: int = 8,
        top_k: int = 30,
    ):
        self.stopwords = stopwords or set(DEFAULT_STOPWORDS)
        self.min_mentions_6h = int(min_mentions_6h)
        self.top_k = int(top_k)

    # ---------- DB helpers for novelty ----------
    @staticmethod
    def ensure_state_tables(conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS trend_item_state (
          item_key TEXT PRIMARY KEY,
          first_seen_at TEXT NOT NULL,
          source TEXT,
          shop_id INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_trend_item_state_first_seen ON trend_item_state(first_seen_at);
        """)
        conn.commit()

    @staticmethod
    def _item_key(source: str, item: TrendItem) -> Optional[str]:
        if item.item_id is not None:
            return f"{source}:{item.item_id}"
        if item.title:
            return f"{source}:title:{hash(item.title)}"
        return None

    def load_first_seen_map(self, conn: sqlite3.Connection) -> Dict[str, str]:
        cur = conn.cursor()
        cur.execute("SELECT item_key, first_seen_at FROM trend_item_state")
        return {str(r[0]): str(r[1]) for r in cur.fetchall()}

    def score(
        self,
        *,
        source: str,
        fetched_at: str,
        items_1h: List[TrendItem],
        items_3h: List[TrendItem],
        items_6h: List[TrendItem],
        items_24h: List[TrendItem],
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[TrendScore]:
        first_seen_map: Dict[str, str] = {}
        if conn is not None:
            self.ensure_state_tables(conn)
            first_seen_map = self.load_first_seen_map(conn)

        def agg(items: Iterable[TrendItem], window_start_iso: str) -> Dict[str, Dict[str, Any]]:
            acc: Dict[str, Dict[str, Any]] = {}
            for it in items:
                toks = tokenize(it.title, it.tags, self.stopwords)
                grams = extract_2grams(toks, self.stopwords)
                if not grams:
                    continue

                is_new = False
                if conn is not None:
                    key = self._item_key(source, it)
                    if key:
                        fs = first_seen_map.get(key)
                        if fs and fs >= window_start_iso:
                            is_new = True

                for g in grams:
                    d = acc.get(g)
                    if d is None:
                        d = {"mentions": 0, "shops": set(), "new_mentions": 0, "evidence": []}
                        acc[g] = d
                    d["mentions"] += 1
                    if it.shop_id is not None:
                        d["shops"].add(int(it.shop_id))
                    if is_new:
                        d["new_mentions"] += 1
                    if len(d["evidence"]) < 5:
                        d["evidence"].append({
                            "item_id": it.item_id,
                            "shop_id": it.shop_id,
                            "title": (it.title or "")[:140],
                            "url": it.url,
                        })

            for _, d in acc.items():
                d["shops_count"] = len(d["shops"])
                del d["shops"]
            return acc

        # Parse fetched_at like "2026-02-27Txx:xx:xxZ"
        t_now = dt.datetime.fromisoformat(fetched_at.replace("Z", ""))
        w1 = (t_now - dt.timedelta(hours=1)).isoformat() + "Z"
        w3 = (t_now - dt.timedelta(hours=3)).isoformat() + "Z"
        w6 = (t_now - dt.timedelta(hours=6)).isoformat() + "Z"
        w24 = (t_now - dt.timedelta(hours=24)).isoformat() + "Z"

        a1 = agg(items_1h, w1)
        a3 = agg(items_3h, w3)
        a6 = agg(items_6h, w6)
        a24 = agg(items_24h, w24)

        scored: List[TrendScore] = []
        terms = set(a6.keys()) | set(a3.keys()) | set(a1.keys())

        for term in terms:
            m6 = int(a6.get(term, {}).get("mentions", 0))
            if m6 < self.min_mentions_6h:
                continue

            m3 = int(a3.get(term, {}).get("mentions", 0))
            m1 = int(a1.get(term, {}).get("mentions", 0))
            shops6 = int(a6.get(term, {}).get("shops_count", 0))
            new6 = int(a6.get(term, {}).get("new_mentions", 0))
            evidence = list(a6.get(term, {}).get("evidence", []))[:3]

            m24_total = int(a24.get(term, {}).get("mentions", 0))
            base24 = m24_total / 24.0  # hourly baseline

            v = m3 / (base24 + 1.0)              # 3h vs baseline
            a = m1 / ((m6 / 6.0) + 1.0)          # 1h vs 6h hourly avg

            velocity = clamp(20.0 * log2p(v), 0.0, 100.0)
            accel = clamp(25.0 * log2p(a), 0.0, 100.0)
            breadth = clamp(12.0 * log2p(shops6), 0.0, 100.0)
            novelty = clamp((new6 / (m6 + 1.0)) * 120.0, 0.0, 100.0)

            hit = 0.35 * accel + 0.30 * velocity + 0.20 * breadth + 0.15 * novelty

            # anti-spam dampening
            if shops6 < 2:
                hit *= 0.7

            hit = clamp(hit, 0.0, 100.0)

            if hit >= 75 and accel >= 60 and shops6 >= 5:
                level = "DO_NOW"
            elif hit >= 55 and shops6 >= 3:
                level = "DO_SOON"
            else:
                level = "WATCH"

            growth = (m3 / ((base24 * 3.0) + 1.0))

            scored.append(TrendScore(
                term=term,
                hit_score=round(hit, 1),
                action_level=level,
                growth=round(growth, 3),
                metrics={
                    "m1": m1, "m3": m3, "m6": m6,
                    "shops6": shops6, "new6": new6,
                    "base24": round(base24, 4),
                    "velocity_score": round(velocity, 1),
                    "accel_score": round(accel, 1),
                    "breadth_score": round(breadth, 1),
                    "novelty_score": round(novelty, 1),
                },
                evidence=evidence,
            ))

        scored.sort(key=lambda x: x.hit_score, reverse=True)
        return scored[: self.top_k]


def write_scores_to_trends(
    conn: sqlite3.Connection,
    *,
    fetched_at: str,
    country: str,
    category: str,
    source: str,
    scores: List[TrendScore],
) -> int:
    """
    Compatible with your current trends schema:

    CREATE TABLE trends (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      term TEXT NOT NULL,
      country TEXT,
      category TEXT,
      growth REAL,
      payload_json TEXT,
      created_at TEXT NOT NULL,
      hit_score INTEGER,
      action_level TEXT,
      risk_level TEXT,
      reason TEXT,
      amazon_intent_score REAL DEFAULT 0,
      amazon_opportunity_score REAL DEFAULT 0,
      product_type TEXT
    );
    """
    cur = conn.cursor()
    inserted = 0

    for s in scores:
        payload = {
            "source": source,
            "window": "hourly",
            "metrics": s.metrics,
            "evidence": s.evidence,
        }

        # Provide safe defaults for fields you will refine later
        risk_level = "LOW"
        reason = "2-gram hourly score"
        product_type = "POD"

        cur.execute(
            """
            INSERT INTO trends
              (date, term, country, category, growth, payload_json, created_at, hit_score, action_level, risk_level, reason, product_type)
            VALUES
              (?,    ?,    ?,       ?,        ?,      ?,           ?,          ?,        ?,            ?,          ?,      ?)
            """,
            (
                fetched_at,
                s.term,
                country,
                category,
                float(s.growth),
                json.dumps(payload, ensure_ascii=False),
                fetched_at,                 # created_at NOT NULL
                int(round(s.hit_score)),    # hit_score INTEGER
                s.action_level,
                risk_level,
                reason,
                product_type,
            ),
        )
        inserted += 1

    conn.commit()
    return inserted