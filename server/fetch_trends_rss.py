#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge V6.1 - Google Trends RSS fetcher (stable, no API key)
Writes into raw_trends table.

Run:
  export DB_PATH=/root/trendforge-mvp/server/trendforge.db
  python fetch_trends_rss.py --geo US --limit 50
"""

import os
import sys
import json
import time
import argparse
import sqlite3
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET


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


def fetch_rss(geo: str, timeout: int = 20) -> str:
    # Official public RSS endpoint
    url = f"https://trends.google.com/trending/rss?geo={geo.upper()}"
    headers = {
        "User-Agent": os.getenv(
            "TF_USER_AGENT",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
    }
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="ignore")


def parse_items(xml_text: str):
    """
    RSS structure: <item><title>...</title><ht:approx_traffic>...</ht:approx_traffic>...
    We'll capture title + approx_traffic (if exists) + pubDate + news_items count (if present).
    """
    items = []
    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        raise RuntimeError(f"RSS parse failed: {e}")

    # namespaces
    ns = {
        "ht": "http://purl.org/rss/1.0/modules/content/",
        "atom": "http://www.w3.org/2005/Atom",
    }

    channel = root.find("channel")
    if channel is None:
        # some rss variations
        channel = root.find("./rss/channel")
    if channel is None:
        raise RuntimeError("RSS parse failed: channel not found")

    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()

        approx = ""
        # Google uses ht:approx_traffic with namespace "http://trends.google.com/trends/hottrends"
        # But some feeds expose as "ht:approx_traffic" without strict namespace.
        # We'll search any tag ending with 'approx_traffic'.
        for child in list(item):
            if child.tag.endswith("approx_traffic"):
                approx = (child.text or "").strip()
                break

        # normalize approx traffic like "200K+" => 200000
        score = 0.0
        if approx:
            s = approx.replace("+", "").replace(",", "").strip().lower()
            try:
                if s.endswith("k"):
                    score = float(s[:-1]) * 1000.0
                elif s.endswith("m"):
                    score = float(s[:-1]) * 1000000.0
                else:
                    score = float(s)
            except Exception:
                score = 0.0

        if not title:
            continue

        items.append({
            "term": title,
            "score": score,
            "pubDate": pub,
            "approx_traffic": approx,
        })
    return items


def upsert_raw(conn: sqlite3.Connection, date: str, country: str, source: str, rows):
    ensure_tables(conn)
    now = utc_now_iso()
    inserted = 0
    for r in rows:
        term = str(r.get("term", "")).strip()
        if not term:
            continue
        payload = {
            "term": term,
            "score": r.get("score", 0),
            "pubDate": r.get("pubDate", ""),
            "approx_traffic": r.get("approx_traffic", ""),
            "source": source,
            "fetched_at": now,
        }
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO raw_trends(date, country, term, score, source, payload_json, created_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (date, country, term, float(r.get("score", 0) or 0), source, json.dumps(payload, ensure_ascii=False), now)
        )
        if cur.rowcount == 1:
            inserted += 1
    conn.commit()
    return inserted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo", default=os.getenv("COUNTRY", "US"), help="country/geo, e.g. US")
    ap.add_argument("--limit", type=int, default=int(os.getenv("RSS_LIMIT", "50")))
    ap.add_argument("--date", default=os.getenv("TF_DATE", ""), help="override date YYYY-MM-DD, default today(UTC)")
    ap.add_argument("--timeout", type=int, default=int(os.getenv("TF_HTTP_TIMEOUT", "20")))
    args = ap.parse_args()

    db = get_db_path()
    date = args.date.strip() or today_utc_date()
    geo = args.geo.upper().strip()
    source = f"gtrends:rss:{geo.lower()}"

    log(f"[INFO] db={db}")
    log(f"[INFO] geo={geo} date={date} limit={args.limit}")

    inserted = 0
    try:
        xml_text = fetch_rss(geo=geo, timeout=args.timeout)
        items = parse_items(xml_text)
        if args.limit > 0:
            items = items[:args.limit]
        conn = sqlite3.connect(db)
        inserted = upsert_raw(conn, date=date, country=geo, source=source, rows=items)
        conn.close()
        log(f"[OK] fetch_trends_rss inserted_raw={inserted} source={source}")
        return 0
    except HTTPError as e:
        log(f"[WARN] fetch_rss failed geo={geo} err=HTTP {e.code}")
    except URLError as e:
        log(f"[WARN] fetch_rss failed geo={geo} err=URLError {e}")
    except Exception as e:
        log(f"[WARN] fetch_rss failed geo={geo} err={type(e).__name__}: {e}")

    log(f"[OK] fetch_trends_rss done inserted_raw={inserted} (not blocking pipeline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())