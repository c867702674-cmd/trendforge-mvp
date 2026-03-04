#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge D10 (A1): Write execution feedback into trends table.

This script updates:
- execution_feedback_json (TEXT JSON)
- execution_feedback_updated_at (ISO Z)

Examples:
  # Dry-run preview
  python3 write_execution_feedback.py --id 123 --uploaded 1 --platform Etsy --days-to-first-sale 3 --sales-7d-estimate 5 --note "good" --dry-run 1

  # Real write
  python3 write_execution_feedback.py --id 123 --uploaded 1 --platform Etsy --days-to-first-sale 3 --sales-7d-estimate 5 --note "good"

  # Only add a note
  python3 write_execution_feedback.py --id 123 --note "seller said conversion ok"
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

DEFAULT_DB_PATH = "/root/trendforge-mvp/server/trendforge.db"


def iso_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def db_connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_columns(conn: sqlite3.Connection) -> None:
    cols = conn.execute("PRAGMA table_info(trends)").fetchall()
    names = {c["name"] for c in cols}
    missing = []
    for c in ("execution_feedback_json", "execution_feedback_updated_at"):
        if c not in names:
            missing.append(c)
    if missing:
        raise RuntimeError(
            "Missing required columns: "
            + ", ".join(missing)
            + "\nPlease run:\n"
            + "ALTER TABLE trends ADD COLUMN execution_feedback_json TEXT;\n"
            + "ALTER TABLE trends ADD COLUMN execution_feedback_updated_at TEXT;"
        )


def get_trend(conn: sqlite3.Connection, trend_id: int) -> sqlite3.Row:
    r = conn.execute("SELECT id, term, execution_feedback_json FROM trends WHERE id = ?", (trend_id,)).fetchone()
    if not r:
        raise RuntimeError(f"Trend not found: id={trend_id}")
    return r


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    p.add_argument("--db-path", default=os.getenv("TRENDFORGE_DB_PATH", DEFAULT_DB_PATH))
    p.add_argument("--id", type=int, required=True, help="trend id")
    p.add_argument("--dry-run", type=int, default=0, help="1=do not write DB")

    # Core feedback fields
    p.add_argument("--uploaded", type=int, default=None, help="1/0")
    p.add_argument("--platform", default=None, help="Etsy / Amazon / Shopify / ...")
    p.add_argument("--days-to-first-sale", type=int, default=None)
    p.add_argument("--sales-7d-estimate", type=int, default=None)

    # Optional metadata
    p.add_argument("--note", default=None, help="operator note")
    p.add_argument("--seller_id", default=None, help="optional internal seller id")
    p.add_argument("--source", default="manual", help="manual / webhook / import")

    # Merge behavior
    p.add_argument("--overwrite", type=int, default=0, help="1=overwrite whole JSON; 0=merge update")
    return p.parse_args()


def merge_dict(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    # Simple shallow merge; patch wins
    out = dict(base)
    for k, v in patch.items():
        if v is not None:
            out[k] = v
    return out


def main() -> int:
    args = parse_args()
    dry_run = bool(args.dry_run)
    overwrite = bool(args.overwrite)

    db_path = args.db_path
    if not os.path.exists(db_path):
        print(f"[ERROR] DB not found: {db_path}")
        return 2

    conn = db_connect(db_path)
    try:
        ensure_columns(conn)
        row = get_trend(conn, args.id)

        term = row["term"] or ""
        old_raw = row["execution_feedback_json"] or ""
        old_obj: Dict[str, Any] = {}
        if old_raw.strip():
            try:
                old_obj = json.loads(old_raw)
                if not isinstance(old_obj, dict):
                    old_obj = {}
            except Exception:
                old_obj = {}

        patch: Dict[str, Any] = {
            "uploaded": (bool(args.uploaded) if args.uploaded is not None else None),
            "platform": (args.platform.strip() if isinstance(args.platform, str) and args.platform.strip() else None),
            "days_to_first_sale": args.days_to_first_sale,
            "sales_7d_estimate": args.sales_7d_estimate,
            "operator_note": (args.note.strip() if isinstance(args.note, str) and args.note.strip() else None),
            "seller_id": (args.seller_id.strip() if isinstance(args.seller_id, str) and args.seller_id.strip() else None),
            "source": (args.source.strip() if isinstance(args.source, str) and args.source.strip() else "manual"),
            "updated_at": iso_z(),
        }

        new_obj = patch if overwrite else merge_dict(old_obj, patch)

        new_raw = json.dumps(new_obj, ensure_ascii=False)
        updated_at = new_obj.get("updated_at") or iso_z()

        print(f"[INFO] id={args.id} term={term}")
        print(f"[INFO] old_feedback={'(empty)' if not old_raw.strip() else old_raw[:180] + ('...' if len(old_raw) > 180 else '')}")
        print(f"[INFO] new_feedback={new_raw[:220] + ('...' if len(new_raw) > 220 else '')}")
        print(f"[INFO] dry_run={dry_run} overwrite={overwrite}")

        if dry_run:
            print("[DONE] dry-run only, no DB write.")
            return 0

        conn.execute(
            "UPDATE trends SET execution_feedback_json = ?, execution_feedback_updated_at = ? WHERE id = ?",
            (new_raw, updated_at, args.id),
        )
        conn.commit()
        print("[DONE] wrote execution_feedback_json successfully.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())