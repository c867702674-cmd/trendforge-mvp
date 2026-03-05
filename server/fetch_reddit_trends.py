#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge V6.1 - Reddit lightweight trending fetcher (public JSON)
Writes into raw_trends.

Run:
  export DB_PATH=/root/trendforge-mvp/server/trendforge.db
  python fetch_reddit_trends.py --sub popular --limit 50
"""

import os
import json
import argparse
import sqlite3
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc_date():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def log(msg):
    print(msg, flush=True)


def get_db_path():
    return os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "trendforge.db"))


def ensure_tables(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS raw_trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        country TEXT NOT NULL,
        term TEXT NOT NULL,
        score REAL DEFAULT 0,
        source TEXT NOT NULL,
        payload_json TEXT DEFAULT '{}',
        created_at TEXT DEFAULT ''
    );
    """)
    conn.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_trends_uniq
    ON raw_trends(date, country, term, source);
    """)
    conn.commit()


def fetch_json(url: str, timeout: int = 20) -> dict:
    headers = {
        "User-Agent": os.getenv(
            "TF_USER_AGENT",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        ),
        "Accept": "application/json",
    }
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    return json.loads(data)


def upsert_raw(conn: sqlite3.Connection, date: str, country: str, source: str, items):
    ensure_tables(conn)
    now = utc_now_iso()
    inserted = 0
    for r in items:
        term = str(r.get("term", "")).strip()
        if not term:
            continue
        score = float(r.get("score", 0) or 0)
        payload = dict(r)
        payload["source"] = source
        payload["fetched_at"] = now
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO raw_trends(date, country, term, score, source, payload_json, created_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (date, country, term, score, source, json.dumps(payload, ensure_ascii=False), now)
        )
        if cur.rowcount == 1:
            inserted += 1
    conn.commit()
    return inserted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo", default=os.getenv("COUNTRY", "US"), help="country label (not used by Reddit), default US")
    ap.add_argument("--sub", default=os.getenv("REDDIT_SUB", "popular"), help="subreddit: popular / all / etc.")
    ap.add_argument("--limit", type=int, default=int(os.getenv("REDDIT_LIMIT", "50")))
    ap.add_argument("--timeout", type=int, default=int(os.getenv("TF_HTTP_TIMEOUT", "20")))
    ap.add_argument("--date", default=os.getenv("TF_DATE", ""), help="override date YYYY-MM-DD, default today(UTC)")
    args = ap.parse_args()

    db = get_db_path()
    date = args.date.strip() or today_utc_date()
    country = args.geo.upper().strip()
    sub = args.sub.strip().strip("/")
    source = f"reddit:{sub}"

    log(f"[INFO] db={db}")
    log(f"[INFO] sub={sub} date={date} limit={args.limit}")

    inserted = 0
    try:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={max(1, args.limit)}"
        data = fetch_json(url, timeout=args.timeout)
        children = (((data or {}).get("data") or {}).get("children") or [])
        items = []
        for ch in children:
            d = (ch or {}).get("data") or {}
            title = (d.get("title") or "").strip()
            if not title:
                continue
            # score: upvotes-ish; keep as a weak signal
            score = float(d.get("score") or 0)
            items.append({
                "term": title,
                "score": score,
                "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                "subreddit": d.get("subreddit"),
            })

        conn = sqlite3.connect(db)
        inserted = upsert_raw(conn, date=date, country=country, source=source, items=items)
        conn.close()
        log(f"[OK] fetch_reddit_trends inserted_raw={inserted} source={source}")
        return 0
    except HTTPError as e:
        log(f"[WARN] fetch_reddit_trends failed err=HTTP {e.code} (not blocking)")
    except URLError as e:
        log(f"[WARN] fetch_reddit_trends failed err=URLError {e} (not blocking)")
    except Exception as e:
        log(f"[WARN] fetch_reddit_trends failed err={type(e).__name__}: {e} (not blocking)")

    log(f"[OK] fetch_reddit_trends done inserted_raw={inserted} (not blocking pipeline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())