#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge V6 - Etsy public best-effort fetcher (no API key)
Goal: insert some POD-related real terms into raw_trends
"""

import os
import re
import json
import time
import math
import hashlib
import argparse
import sqlite3
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests


DEFAULT_SEEDS = [
    "pod", "shirt", "tshirt", "hoodie", "sticker", "mug",
    "embroidery patch", "retro typography", "line art",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def env_str(key: str, default: str) -> str:
    v = os.getenv(key)
    return v.strip() if v and v.strip() else default


def connect_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_trends (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date TEXT,
          source TEXT,
          country TEXT,
          term TEXT,
          score REAL,
          payload_json TEXT,
          dedup_hash TEXT,
          created_at TEXT,
          meta_json TEXT
        )
        """
    )
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(raw_trends)").fetchall()}
    if "created_at" not in cols:
        conn.execute("ALTER TABLE raw_trends ADD COLUMN created_at TEXT")
    if "meta_json" not in cols:
        conn.execute("ALTER TABLE raw_trends ADD COLUMN meta_json TEXT")
    if "dedup_hash" not in cols:
        conn.execute("ALTER TABLE raw_trends ADD COLUMN dedup_hash TEXT")
    conn.commit()


def norm_term(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" -|/\\\t\r\n")
    return s


def make_dedup_hash(date: str, country: str, term: str, source: str) -> str:
    raw = f"{date}|{country}|{term.lower()}|{source}".encode("utf-8", "ignore")
    return hashlib.sha1(raw).hexdigest()


def score_from_rank(rank: int) -> float:
    # rank 越小分越大：大概落在 800~150 区间
    return float(max(150.0, 800.0 - rank * 30.0))


def etsy_search(seed: str, page: int, timeout: int = 15):
    # 注：Etsy 会频繁 403/机器人校验，本脚本为 best-effort。
    # 只要有部分 seed 成功，就足够 pipeline 使用。
    q = quote_plus(seed)
    url = f"https://www.etsy.com/search?q={q}&ref=pagination&page={page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text, url


def extract_titles(html: str, max_items: int = 20):
    """
    解析页面里 listing title（启发式）
    规则尽量“宁少勿乱”
    """
    # 常见 title 片段：data-listing-card-title / aria-label / title
    # 这里做宽松抓取 + 去重
    candidates = set()

    # aria-label="Listing title"
    for m in re.finditer(r'aria-label="([^"]{8,120})"', html):
        t = norm_term(m.group(1))
        if 8 <= len(t) <= 80:
            candidates.add(t)

    # data-listing-card-title="..."
    for m in re.finditer(r'data-listing-card-title="([^"]{8,120})"', html):
        t = norm_term(m.group(1))
        if 8 <= len(t) <= 80:
            candidates.add(t)

    # <h3 ...>Title</h3>
    for m in re.finditer(r"<h3[^>]*>([^<]{8,120})</h3>", html, flags=re.I):
        t = norm_term(m.group(1))
        if 8 <= len(t) <= 80:
            candidates.add(t)

    # 过滤明显噪声
    bad = ["Etsy", "Search", "Results", "Sign in", "Cart", "Help"]
    out = []
    for t in candidates:
        if any(b.lower() in t.lower() for b in bad):
            continue
        out.append(t)

    out = sorted(out, key=lambda x: len(x))
    return out[:max_items]


def upsert_raw(conn: sqlite3.Connection, date: str, country: str, seed: str, terms, page: int, url: str):
    created_at = utc_now_iso()
    source = f"etsy:public:{country.lower()}"
    inserted = 0

    for i, term in enumerate(terms):
        term = norm_term(term)
        if not term:
            continue

        dedup = make_dedup_hash(date, country.upper(), term, source)
        exists = conn.execute(
            "SELECT 1 FROM raw_trends WHERE dedup_hash=? LIMIT 1",
            (dedup,),
        ).fetchone()
        if exists:
            continue

        score = score_from_rank(i + 1)

        meta = {
            "seed": seed,
            "page": page,
            "url": url,
            "rank_in_page": i + 1,
        }
        payload = {"term": term, "score": score, "source": source, "seed": seed, "page": page}

        conn.execute(
            """
            INSERT INTO raw_trends(date, country, term, score, source, payload_json, dedup_hash, created_at, meta_json)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                date,
                country.upper(),
                term,
                float(score),
                source,
                json.dumps(payload, ensure_ascii=False),
                dedup,
                created_at,
                json.dumps(meta, ensure_ascii=False),
            ),
        )
        inserted += 1

    conn.commit()
    return inserted, source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default=env_str("COUNTRY", "US"))
    ap.add_argument("--seeds", default=env_str("ETSY_SEEDS", ",".join(DEFAULT_SEEDS)))
    ap.add_argument("--pages", type=int, default=int(env_str("ETSY_PAGES", "1")))
    ap.add_argument("--limit-per-seed", type=int, default=int(env_str("ETSY_LIMIT_PER_SEED", "30")))
    ap.add_argument("--sleep", type=float, default=float(env_str("ETSY_SLEEP", "0.6")))
    args = ap.parse_args()

    db_path = env_str("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
    country = (args.country or "US").upper()
    date = today_utc_date()
    seeds = [s.strip() for s in (args.seeds or "").split(",") if s.strip()]

    print(f"[INFO] db={db_path}")
    print(f"[INFO] country={country} date={date} pages={args.pages} limit_per_seed={args.limit_per_seed}")

    conn = connect_db(db_path)
    ensure_schema(conn)

    total_inserted = 0
    failed_seeds = 0
    pages_ok = 0
    pages_fail = 0
    parsed = 0

    try:
        for seed in seeds:
            seed_inserted = 0
            for page in range(1, args.pages + 1):
                try:
                    html, url = etsy_search(seed, page)
                    terms = extract_titles(html, max_items=min(20, args.limit_per_seed))
                    parsed += len(terms)
                    ins, _source = upsert_raw(conn, date, country, seed, terms, page, url)
                    seed_inserted += ins
                    total_inserted += ins
                    pages_ok += 1
                    time.sleep(args.sleep)
                except Exception as e:
                    pages_fail += 1
                    print(f"[WARN] etsy fetch failed seed={seed} page={page} err={type(e).__name__}: {e}")
                    time.sleep(args.sleep)
                    continue

            if seed_inserted == 0:
                failed_seeds += 1
            print(f"[OK] etsy seed={seed} inserted_raw={seed_inserted} pages_ok={pages_ok} pages_fail={pages_fail} parsed={parsed}")

        print(f"[OK] fetch_etsy_pod done inserted_raw={total_inserted} failed_seeds={failed_seeds} db={db_path}")
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())