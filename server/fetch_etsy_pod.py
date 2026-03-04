#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import sqlite3
import hashlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH") or os.path.join(os.path.dirname(__file__), "trendforge.db")

# 你可以在环境变量里改：ETSY_SEEDS="pod,shirt,tshirt,hoodie,sticker,mug"
ETSY_SEEDS = os.environ.get("ETSY_SEEDS") or "pod,shirt,tshirt,hoodie,sticker,mug,embroidery patch,retro typography"
ETSY_SEEDS = [s.strip() for s in ETSY_SEEDS.split(",") if s.strip()]

ETSY_GEO = os.environ.get("ETSY_GEO") or "US"
ETSY_LIMIT = int(os.environ.get("ETSY_LIMIT") or "12")
SLEEP = float(os.environ.get("ETSY_SLEEP") or "0.8")

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36 TrendForge/1.0"

# 用 Etsy 搜索页的 public JSON： __NEXT_DATA__ 里能拿到 query 建议/结果结构
BASE = "https://www.etsy.com/search?q={q}"


def utc_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def ensure_tables(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS raw_trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        source TEXT,
        country TEXT,
        term TEXT,
        score REAL DEFAULT 0,
        payload_json TEXT,
        dedup_hash TEXT UNIQUE
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_raw_date ON raw_trends(date);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_raw_country ON raw_trends(country);")
    conn.commit()


def dedup_hash(source: str, country: str, term: str, date: str) -> str:
    raw = f"{source}|{country}|{term}|{date}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_next_data(html: str) -> dict:
    """
    Etsy 页面通常有 <script id="__NEXT_DATA__">...</script>
    """
    m = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>\s*(\{.*?\})\s*</script>', html, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


def extract_terms_from_next(data: dict) -> list:
    """
    尽量从 next data 里抓一些 “query / categories / suggested terms”
    结构会变，所以做宽松提取：抓所有短字符串里像关键词的
    """
    terms = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(k)
                walk(v)
        elif isinstance(x, list):
            for it in x:
                walk(it)
        elif isinstance(x, str):
            s = x.strip()
            # 过滤太短/太长/URL
            if 3 <= len(s) <= 40 and "http" not in s and "/" not in s:
                # 尽量像关键词：包含字母/空格
                if re.search(r"[A-Za-z]", s):
                    terms.add(s.lower())

    walk(data)
    # 去掉一些噪音
    bad = {"etsy", "shop", "sale", "review", "shipping", "gift", "cart"}
    out = [t for t in terms if all(b not in t for b in bad)]
    out.sort(key=lambda s: (len(s), s))
    return out


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_tables(conn)

    today = utc_date()
    inserted = 0

    for seed in ETSY_SEEDS:
        q = urllib.parse.quote(seed)
        url = BASE.format(q=q)
        try:
            html = fetch_html(url)
            data = extract_next_data(html)
            terms = extract_terms_from_next(data)

            # 取前 N 个，score 给个简单权重（seed 越靠前越高）
            terms = terms[:ETSY_LIMIT]
            for i, term in enumerate(terms):
                score = float(max(1, ETSY_LIMIT - i))
                payload = {
                    "seed": seed,
                    "term": term,
                    "score": score,
                    "source": "etsy:public",
                    "flags": {"updated_at": utc_iso()}
                }
                h = dedup_hash("etsy:public", ETSY_GEO, term, today)
                try:
                    conn.execute(
                        "INSERT INTO raw_trends(date,source,country,term,score,payload_json,dedup_hash) VALUES (?,?,?,?,?,?,?)",
                        (today, "etsy:public", ETSY_GEO, term, score, json.dumps(payload, ensure_ascii=False), h)
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass

        except Exception as e:
            print(f"[WARN] etsy fetch failed seed={seed} err={e.__class__.__name__}")
        time.sleep(SLEEP)

    conn.commit()
    print(f"[OK] fetch_etsy_pod done inserted_raw={inserted} db={DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())