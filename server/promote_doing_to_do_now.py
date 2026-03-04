#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge D9: Promote DOING -> DO_NOW automatically.

Default rule (v1, no snapshot table needed):
- action_level == "DOING"
- hit_score >= HIT_MIN
- growth >= GROWTH_MIN
- (optional) risk_level != "HIGH"  (if column exists)
- (optional) require_pack: execution_pack_json not empty (recommended)

Writes:
- action_level -> DO_NOW
- last_action_level updated (if exists)
- reason text (if column exists, else skip)
- flags_updated_at (if exists, else skip)

Usage:
  python3 /root/trendforge-mvp/server/promote_doing_to_do_now.py
  python3 ... --dry-run 1
  python3 ... --hit-min 140 --growth-min 12
  python3 ... --limit 50
  python3 ... --no-require-pack 1
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_DB_PATH = "/root/trendforge-mvp/server/trendforge.db"


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def db_connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [c["name"] for c in cols]


def col_exists(colnames: List[str], name: str) -> bool:
    return name in set(colnames)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", default=os.getenv("TRENDFORGE_DB_PATH", DEFAULT_DB_PATH))
    p.add_argument("--limit", type=int, default=200)

    # thresholds
    p.add_argument("--hit-min", type=int, default=120)
    p.add_argument("--growth-min", type=float, default=10.0)

    # switches
    p.add_argument("--dry-run", type=int, default=0, help="1=do not write DB")
    p.add_argument("--allow-high-risk", type=int, default=0, help="1=allow risk_level=HIGH")
    p.add_argument("--no-require-pack", type=int, default=0, help="1=do not require execution_pack_json")

    return p.parse_args()


def main() -> int:
    args = parse_args()
    db_path: str = args.db_path
    limit: int = max(1, args.limit)

    hit_min: int = args.hit_min
    growth_min: float = args.growth_min

    dry_run: bool = bool(args.dry_run)
    allow_high_risk: bool = bool(args.allow_high_risk)
    require_pack: bool = not bool(args.no_require_pack)

    if not os.path.exists(db_path):
        print(f"[ERROR] DB not found: {db_path}")
        return 2

    conn = db_connect(db_path)
    try:
        cols = get_columns(conn, "trends")

        has_risk = col_exists(cols, "risk_level")
        has_reason = col_exists(cols, "reason")
        has_flags_updated_at = col_exists(cols, "flags_updated_at")
        has_last_action_level = col_exists(cols, "last_action_level")
        has_pack = col_exists(cols, "execution_pack_json")

        if require_pack and not has_pack:
            print("[ERROR] require_pack enabled but column execution_pack_json not found.")
            print("        Please add it: ALTER TABLE trends ADD COLUMN execution_pack_json TEXT;")
            return 3

        print(
            f"[INFO] db={db_path} limit={limit} dry_run={dry_run} "
            f"hit_min={hit_min} growth_min={growth_min} require_pack={require_pack} "
            f"allow_high_risk={allow_high_risk} has_risk={has_risk}"
        )

        # Build WHERE conditions dynamically
        where = ["action_level = 'DOING'"]
        where.append("hit_score >= ?")
        where.append("growth >= ?")
        params: List[Any] = [hit_min, growth_min]

        if require_pack:
            where.append("(execution_pack_json IS NOT NULL AND execution_pack_json <> '')")

        if has_risk and not allow_high_risk:
            where.append("(risk_level IS NULL OR UPPER(risk_level) <> 'HIGH')")

        where_sql = " AND ".join(where)

        rows = conn.execute(
            f"""
            SELECT id, term, hit_score, growth, action_level
                   {", risk_level" if has_risk else ""}
                   {", execution_pack_json" if has_pack else ""}
            FROM trends
            WHERE {where_sql}
            ORDER BY hit_score DESC, growth DESC, id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()

        print(f"[INFO] matched={len(rows)}")

        promoted = 0
        skipped = 0

        for r in rows:
            tid = int(r["id"])
            term = r["term"] or ""
            hit = int(r["hit_score"] or 0)
            growth = float(r["growth"] or 0.0)
            risk = (r["risk_level"] if has_risk else None) or ""
            pack_len = 0
            if has_pack:
                pack_len = len(r["execution_pack_json"] or "")

            reason_text = (
                f"D9 promote DOING->DO_NOW: hit>={hit_min}, growth>={growth_min}"
                + (", require_pack=1" if require_pack else ", require_pack=0")
                + (", allow_high_risk=1" if allow_high_risk else ", allow_high_risk=0")
            )

            if dry_run:
                promoted += 1
                print(f"[DRY] promote id={tid} hit={hit} growth={growth} risk={risk} pack_len={pack_len} term={term}")
                continue

            # Prepare UPDATE statement based on available columns
            set_parts = ["action_level = 'DO_NOW'"]
            set_vals: List[Any] = []

            if has_last_action_level:
                set_parts.append("last_action_level = 'DOING'")

            if has_reason:
                set_parts.append("reason = ?")
                set_vals.append(reason_text)

            if has_flags_updated_at:
                set_parts.append("flags_updated_at = ?")
                set_vals.append(utc_iso())

            set_sql = ", ".join(set_parts)

            conn.execute(
                f"UPDATE trends SET {set_sql} WHERE id = ?",
                (*set_vals, tid),
            )
            promoted += 1
            print(f"[OK]  promote id={tid} hit={hit} growth={growth} risk={risk} term={term}")

        if not dry_run:
            conn.commit()

        print(f"[DONE] promoted={promoted} skipped={skipped} dry_run={dry_run}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())