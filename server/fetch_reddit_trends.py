#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import json
import hashlib
import sqlite3
import argparse
from datetime import datetime, timezone
from typing import List, Tuple

import requests


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None and str(v).strip() != "" else default


def ensure_raw_trends(conn: sqlite3.Connection) -> None:
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
        );
        """
    )
    cols = {r[1] for r in conn.execute("PRAGMA table_info(raw_trends);").fetchall()}
    if "created_at" not in cols:
        conn.execute("ALTER TABLE raw_trends ADD COLUMN created_at TEXT;")
    if "meta_json" not in cols:
        conn.execute("ALTER TABLE raw_trends ADD COLUMN meta_json TEXT;")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_raw_trends_dedup ON raw_trends(dedup_hash);")
    conn.commit()


def hash_dedup(date: str, country: str, source: str, term: str) -> str:
    raw = f"{date}|{country}|{source}|{term}".encode("utf-8")
    return hashlib.md5(raw).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=env_str("DB_PATH", "/root/trendforge-mvp/server/trendforge.db"))
    ap.add_argument("--sub", default=env_str("REDDIT_SUB", "popular"))
    ap.add_argument("--country", default=env_str("COUNTRY", "US"))
    ap.add_argument("--date", default=env_str("DATE", today_utc()))
    ap.add_argument("--limit", type=int, default=int(env_str("LIMIT", "30")))
    args = ap.parse_args()

    db = args.db
    sub = args.sub.strip()
    country = args.country.upper().strip()
    date = args.date
    limit = max(1, args.limit)

    print(f"[INFO] db={db}")
    print(f"[INFO] sub={sub} date={date} limit={limit}")

    conn = sqlite3.connect(db)
    try:
        ensure_raw_trends(conn)

        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
        headers = {"User-Agent": env_str("REDDIT_UA", "TrendForgeBot/1.0 (by u/trendforge)")}

        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")

        data = r.json()
        posts = data.get("data", {}).get("children", [])
        now = utc_now_iso()

        inserted = 0
        source = f"reddit:{sub}"
        for i, p in enumerate(posts):
            d = p.get("data", {}) or {}
            title = (d.get("title") or "").strip()
            if not title:
                continue

            score = float(d.get("score") or 0)
            dedup = hash_dedup(date, country, source, title)

            cur = conn.execute("SELECT 1 FROM raw_trends WHERE dedup_hash=? LIMIT 1;", (dedup,))
            if cur.fetchone():
                continue

            payload = {"rank": i + 1, "sub": sub, "permalink": d.get("permalink"), "score": score}
            meta = {"fetcher": "fetch_reddit_trends", "fetched_at": now}

            conn.execute(
                """
                INSERT INTO raw_trends(date,source,country,term,score,payload_json,dedup_hash,created_at,meta_json)
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (date, source, country, title, float(score), json.dumps(payload, ensure_ascii=False), dedup, now, json.dumps(meta, ensure_ascii=False)),
            )
            inserted += 1

        conn.commit()
        print(f"[OK] fetch_reddit_trends inserted_raw={inserted} (not blocking pipeline)")
        return 0

    except Exception as e:
        print(f"[WARN] fetch_reddit_trends failed err={repr(e)} (not blocking)")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())