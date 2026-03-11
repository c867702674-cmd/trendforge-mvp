#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge V6 - Google Trends RSS fetcher (stable best-effort)
Insert into raw_trends:
  (date, country, term, score, source, created_at, meta_json, dedup_hash)
"""

import os
import re
import json
import time
import hashlib
import argparse
import sqlite3
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests
import xml.etree.ElementTree as ET


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
    # columns compatibility
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
    return s


def make_dedup_hash(date: str, country: str, term: str, source: str) -> str:
    raw = f"{date}|{country}|{term.lower()}|{source}".encode("utf-8", "ignore")
    return hashlib.sha1(raw).hexdigest()


def fetch_rss(geo: str, limit: int, timeout: int = 15):
    # 这个 RSS 非官方稳定接口：dailytrends?geo=US
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={quote_plus(geo)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


def parse_rss(xml_text: str, limit: int):
    root = ET.fromstring(xml_text)
    # RSS item structure
    items = root.findall(".//item")
    out = []
    for idx, it in enumerate(items[:limit]):
        title = it.findtext("title") or ""
        title = norm_term(title)
        if not title:
            continue
        # score：给一个“可用的”rank分数（越靠前越大）
        # 你后面 build 会用 log1p + threshold，先保证有区分度
        score = 200.0
        if idx < 5:
            score = 500.0
        meta = {
            "rank": idx + 1,
            "rss_title": title,
        }
        out.append((title, score, meta))
    return out


def upsert_raw(conn: sqlite3.Connection, date: str, geo: str, rows):
    created_at = utc_now_iso()
    source = f"gtrends:rss:{geo.lower()}"
    inserted = 0

    for term, score, meta in rows:
        term = norm_term(term)
        if not term:
            continue
        dedup = make_dedup_hash(date, geo.upper(), term, source)

        # 去重：同 dedup_hash 当天同来源只插一次
        exists = conn.execute(
            "SELECT 1 FROM raw_trends WHERE dedup_hash=? LIMIT 1",
            (dedup,),
        ).fetchone()
        if exists:
            continue

        payload = {"term": term, "score": score, "source": source}
        conn.execute(
            """
            INSERT INTO raw_trends(date, country, term, score, source, payload_json, dedup_hash, created_at, meta_json)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                date,
                geo.upper(),
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
    ap.add_argument("--geo", default=env_str("COUNTRY", "US"), help="US/GB/CA/...")
    ap.add_argument("--limit", type=int, default=int(env_str("RSS_LIMIT", "50")))
    args = ap.parse_args()

    db_path = env_str("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
    geo = (args.geo or "US").upper()
    date = today_utc_date()

    print(f"[INFO] db={db_path}")
    print(f"[INFO] geo={geo} date={date} limit={args.limit}")

    conn = connect_db(db_path)
    ensure_schema(conn)

    try:
        xml_text = fetch_rss(geo, args.limit)
        parsed = parse_rss(xml_text, args.limit)
        inserted, source = upsert_raw(conn, date, geo, parsed)
        print(f"[OK] fetch_trends_rss inserted_raw={inserted} source={source}")
    except Exception as e:
        print(f"[WARN] fetch_trends_rss failed geo={geo} err={type(e).__name__}: {e} (not blocking pipeline)")
        return 0
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())