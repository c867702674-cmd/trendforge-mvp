#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone


DEFAULT_DB_PATH = "/root/trendforge-mvp/server/trendforge.db"
DB_PATH = os.getenv("TRENDFORGE_DB_PATH", DEFAULT_DB_PATH)


def now_utc():
    return datetime.now(timezone.utc)


def iso_z(dt):
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def compute_boost(feedback):
    uploaded = feedback.get("uploaded")
    if uploaded is False:
        return 0

    score = 0
    d1 = feedback.get("days_to_first_sale")
    s7 = feedback.get("sales_7d_estimate")

    if isinstance(d1, int) and 0 < d1 <= 3:
        score += 1

    if isinstance(s7, int):
        if s7 >= 5:
            score += 1
        if s7 >= 10:
            score += 1
        if s7 >= 20:
            score += 1

    return min(score, 5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default=DB_PATH)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--dry-run", type=int, default=0)
    args = ap.parse_args()

    since = now_utc() - timedelta(days=args.days)
    dry_run = bool(args.dry_run)

    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, execution_feedback_json, execution_feedback_updated_at,
               COALESCE(feedback_boost_score, 0) AS feedback_boost_score
        FROM trends
        WHERE execution_feedback_json IS NOT NULL
          AND execution_feedback_json <> ''
        ORDER BY id DESC
    """).fetchall()

    print(f"[INFO] rows={len(rows)} dry_run={dry_run}")

    updated = 0

    for r in rows:
        fb = json.loads(r["execution_feedback_json"])
        fb_updated = parse_iso(r["execution_feedback_updated_at"])

        if fb_updated and fb_updated < since:
            continue

        new_boost = compute_boost(fb)
        old_boost = r["feedback_boost_score"]

        if new_boost == old_boost:
            continue

        if dry_run:
            print(f"[DRY] id={r['id']} old={old_boost} new={new_boost}")
            continue

        conn.execute("""
            UPDATE trends
            SET feedback_boost_score=?,
                feedback_boost_updated_at=?
            WHERE id=?
        """, (new_boost, iso_z(now_utc()), r["id"]))

        updated += 1

    if not dry_run:
        conn.commit()

    conn.close()
    print(f"[DONE] updated={updated}")


if __name__ == "__main__":
    main()
