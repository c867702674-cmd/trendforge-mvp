#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timezone

try:
    from pytrends.request import TrendReq
except Exception:
    TrendReq = None

DB_PATH = os.environ.get("DB_PATH") or os.path.join(os.path.dirname(__file__), "trendforge.db")

# 你只需要配置 GEO=US / GB / CA ...
GEO = (os.environ.get("GTR_GEO") or "US").upper()
LIMIT = int(os.environ.get("GTR_LIMIT") or "20")

# pytrends trending_searches 的 pn 不是 "US"，而是 "united_states"
PN_MAP = {
    "US": "united_states",
    "GB": "united_kingdom",
    "CA": "canada",
    "AU": "australia",
    "DE": "germany",
    "FR": "france",
    "JP": "japan",
    "SG": "singapore",
    "HK": "hong_kong",
    "TW": "taiwan",
}


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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_trends(source);")
    conn.commit()


def dedup_hash(source: str, country: str, term: str, date: str) -> str:
    raw = f"{source}|{country}|{term}|{date}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def safe_fetch_terms():
    """
    pytrends 抓取趋势词。任何异常都返回空列表，不阻塞整体流水线。
    """
    if TrendReq is None:
        return [], "pytrends_not_installed"

    pn = PN_MAP.get(GEO, None)
    if not pn:
        return [], f"unsupported_geo:{GEO}"

    try:
        pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        df = pytrends.trending_searches(pn=pn)
        terms = df[0].astype(str).tolist()
        terms = [t.strip() for t in terms if t and str(t).strip()]
        return terms[:LIMIT], f"pytrends_ok pn={pn}"
    except Exception as e:
        return [], f"pytrends_failed:{e.__class__.__name__}"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_tables(conn)

    today = utc_date()
    terms, status = safe_fetch_terms()

    if not terms:
        print(f"[WARN] fetch_google_trends empty ({status}) GEO={GEO} (not blocking pipeline)")
        print(f"[OK] fetch_google_trends done inserted_raw=0 db={DB_PATH}")
        return 0

    inserted = 0
    for rank, term in enumerate(terms):
        # score：简单用排名反转，后续 build 会统一做 hit_score
        score = float(max(1, LIMIT - rank))
        payload = {
            "term": term,
            "rank": rank,
            "score": score,
            "source": "gtrends:pytrends",
            "geo": GEO,
            "flags": {"updated_at": utc_iso()}
        }
        h = dedup_hash("gtrends:pytrends", GEO, term, today)
        try:
            conn.execute(
                "INSERT INTO raw_trends(date,source,country,term,score,payload_json,dedup_hash) VALUES (?,?,?,?,?,?,?)",
                (today, "gtrends:pytrends", GEO, term, score, json.dumps(payload, ensure_ascii=False), h)
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    print(f"[OK] fetch_google_trends done inserted_raw={inserted} db={DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())