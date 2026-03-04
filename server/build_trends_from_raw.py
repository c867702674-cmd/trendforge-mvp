#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH") or os.path.join(os.path.dirname(__file__), "trendforge.db")

# 可调阈值（先用稳的默认）
DO_NOW_MIN = float(os.environ.get("DO_NOW_MIN") or "18")
WATCH_MIN = float(os.environ.get("WATCH_MIN") or "8")

# source 权重：你后续接 Etsy API / Amazon / 其它源时继续加
SOURCE_WEIGHT = {
    "gtrends:pytrends": 1.2,
    "gtrends:rss": 1.0,
    "etsy:public": 1.0,
    "etsy:api": 1.2,
}


def utc_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def table_cols(conn: sqlite3.Connection, table: str) -> set:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def ensure_schema(conn: sqlite3.Connection):
    # raw_trends
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

    # trends（推送引擎的主表）
    conn.execute("""
    CREATE TABLE IF NOT EXISTS trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        country TEXT,
        category TEXT,
        term TEXT,
        growth REAL DEFAULT 0,
        hit_score REAL DEFAULT 0,
        action_level TEXT,
        payload_json TEXT,
        updated_at TEXT
    );
    """)

    # 自动补列（兼容你旧版本引擎可能用到的字段）
    cols = table_cols(conn, "trends")
    def addcol(name, ddl):
        nonlocal cols
        if name not in cols:
            conn.execute(f"ALTER TABLE trends ADD COLUMN {ddl};")
            cols.add(name)

    addcol("source", "source TEXT")
    addcol("score", "score REAL DEFAULT 0")
    addcol("feedback_boost_score", "feedback_boost_score REAL DEFAULT 0")
    addcol("final_score", "final_score REAL DEFAULT 0")  # 可选：你以后想看 final

    # 唯一索引：同一天同国家同 term
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uniq_trends_day_term ON trends(date,country,term);")
    conn.commit()


def compute_action_level(final_score: float) -> str:
    if final_score >= DO_NOW_MIN:
        return "DO_NOW"
    if final_score >= WATCH_MIN:
        return "WATCH"
    return "IGNORE"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)

    day = os.environ.get("DAY") or utc_date()

    rows = conn.execute(
        "SELECT date, country, term, source, score, payload_json FROM raw_trends WHERE date=?",
        (day,)
    ).fetchall()

    if not rows:
        print(f"[OK] build_trends_from_raw date={day} upserted=0 db={DB_PATH} (no raw rows)")
        return 0

    # 合并：同 term 取 max(score * weight)
    best = {}
    for r in rows:
        term = (r["term"] or "").strip()
        if not term:
            continue
        country = (r["country"] or "US").upper()
        source = (r["source"] or "unknown").strip()
        score = float(r["score"] or 0)
        w = float(SOURCE_WEIGHT.get(source, 1.0))
        hit = score * w

        payload = {}
        try:
            if r["payload_json"]:
                payload = json.loads(r["payload_json"])
        except Exception:
            payload = {}

        key = (day, country, term)
        cur = best.get(key)
        if (cur is None) or (hit > cur["hit_score"]):
            best[key] = {
                "date": day,
                "country": country,
                "category": "POD",
                "term": term,
                "score": score,
                "source": source,
                "growth": payload.get("growth", 0) if isinstance(payload, dict) else 0,
                "hit_score": hit,
                "payload": payload,
            }

    upserted = 0
    now = utc_iso()

    for key, item in best.items():
        feedback_boost = 0.0  # 先默认 0，你的推送引擎会从 actions/feedback 里加权
        final_score = float(item["hit_score"]) + float(feedback_boost)
        action_level = compute_action_level(final_score)

        payload = item["payload"] if isinstance(item["payload"], dict) else {}
        # 统一塞进 payload，方便飞书卡片解释来源
        payload["_v6"] = {
            "source": item["source"],
            "score": item["score"],
            "hit_score": item["hit_score"],
            "feedback_boost_score": feedback_boost,
            "final_score": final_score,
            "action_level": action_level,
            "updated_at": now,
        }

        payload_json = json.dumps(payload, ensure_ascii=False)

        conn.execute("""
        INSERT INTO trends(date,country,category,term,growth,hit_score,action_level,payload_json,updated_at,source,score,feedback_boost_score,final_score)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(date,country,term) DO UPDATE SET
          category=excluded.category,
          growth=excluded.growth,
          hit_score=excluded.hit_score,
          action_level=excluded.action_level,
          payload_json=excluded.payload_json,
          updated_at=excluded.updated_at,
          source=excluded.source,
          score=excluded.score,
          feedback_boost_score=excluded.feedback_boost_score,
          final_score=excluded.final_score
        """, (
            item["date"], item["country"], item["category"], item["term"],
            float(item["growth"] or 0), float(item["hit_score"] or 0), action_level,
            payload_json, now,
            item["source"], float(item["score"] or 0), float(feedback_boost), float(final_score)
        ))
        upserted += 1

    conn.commit()
    print(f"[OK] build_trends_from_raw date={day} upserted={upserted} db={DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())