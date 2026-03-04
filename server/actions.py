#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env():
    load_dotenv(".env.feishu")
    load_dotenv("/root/trendforge-mvp/.env.feishu", override=False)


def db_connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trend_actions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          trend_id INTEGER NOT NULL,
          term TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'NEW',
          note TEXT,
          updated_at TEXT NOT NULL,
          UNIQUE(trend_id)
        );
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trend_actions_status ON trend_actions(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trend_actions_term ON trend_actions(term);")
    conn.commit()


def get_latest_trend(conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, term, action_level, hit_score, growth, created_at
        FROM trends
        ORDER BY id DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if not row:
        return None
    return dict(row)


def get_trend(conn: sqlite3.Connection, trend_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, term, action_level, hit_score, growth, created_at, payload_json
        FROM trends
        WHERE id = ?
        """,
        (trend_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return dict(row)


def upsert_action(conn: sqlite3.Connection, trend_id: int, status: str, note: str) -> None:
    trend = get_trend(conn, trend_id)
    if not trend:
        raise SystemExit(f"Trend id={trend_id} not found")

    term = trend["term"] or ""
    now = utc_now_iso()
    status = status.upper().strip()

    if status not in ("NEW", "DOING", "DONE", "SKIP"):
        raise SystemExit("status must be one of: NEW, DOING, DONE, SKIP")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO trend_actions (trend_id, term, status, note, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(trend_id) DO UPDATE SET
          status=excluded.status,
          note=excluded.note,
          updated_at=excluded.updated_at,
          term=excluded.term
        """,
        (trend_id, term, status, note, now),
    )
    conn.commit()


def list_actions(conn: sqlite3.Connection, status: Optional[str], limit: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    if status:
        cur.execute(
            """
            SELECT ta.trend_id, ta.term, ta.status, ta.note, ta.updated_at,
                   t.action_level, t.hit_score, t.growth, t.created_at
            FROM trend_actions ta
            LEFT JOIN trends t ON t.id = ta.trend_id
            WHERE ta.status = ?
            ORDER BY ta.updated_at DESC
            LIMIT ?
            """,
            (status.upper(), limit),
        )
    else:
        cur.execute(
            """
            SELECT ta.trend_id, ta.term, ta.status, ta.note, ta.updated_at,
                   t.action_level, t.hit_score, t.growth, t.created_at
            FROM trend_actions ta
            LEFT JOIN trends t ON t.id = ta.trend_id
            ORDER BY ta.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

    return [dict(r) for r in cur.fetchall()]


def show_trend(conn: sqlite3.Connection, trend_id: int) -> None:
    t = get_trend(conn, trend_id)
    if not t:
        raise SystemExit(f"Trend id={trend_id} not found")

    cur = conn.cursor()
    cur.execute(
        """
        SELECT trend_id, term, status, note, updated_at
        FROM trend_actions
        WHERE trend_id = ?
        """,
        (trend_id,),
    )
    a = cur.fetchone()

    print("=== Trend ===")
    print(f"id: {t['id']}")
    print(f"term: {t['term']}")
    print(f"action_level: {t['action_level']}")
    print(f"hit_score: {t['hit_score']}")
    print(f"growth: {t['growth']}")
    print(f"created_at: {t['created_at']}")

    print("\n=== Action ===")
    if a:
        a = dict(a)
        print(f"status: {a['status']}")
        print(f"note: {a.get('note') or ''}")
        print(f"updated_at: {a['updated_at']}")
    else:
        print("(no action yet)")

    # payload 只展示关键信息（避免刷屏）
    try:
        payload = json.loads(t.get("payload_json") or "{}")
        do_now = payload.get("do_now") or {}
        how = do_now.get("how") or {}
        print("\n=== DO_NOW (brief) ===")
        if do_now:
            print("why:", (do_now.get("why") or [])[:3])
            print("title_templates:", (how.get("title_templates") or do_now.get("title_templates") or [])[:2])
            print("tags:", (how.get("tags") or do_now.get("tags") or [])[:8])
            img = (how.get("image_prompts") or [])[:1]
            if img:
                print("mj_prompt:", img[0])
        else:
            print("(no do_now)")
    except Exception:
        pass


def main():
    load_env()
    db_path = os.getenv("TRENDFORGE_DB", "server/trendforge.db")

    parser = argparse.ArgumentParser(description="TrendForge Execution Actions")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="init action tables")
    p_init.set_defaults(cmd="init")

    p_latest = sub.add_parser("latest", help="show latest trend")
    p_latest.set_defaults(cmd="latest")

    p_show = sub.add_parser("show", help="show trend + action")
    p_show.add_argument("--id", type=int, required=True)
    p_show.set_defaults(cmd="show")

    p_mark = sub.add_parser("mark", help="mark action status for a trend")
    p_mark.add_argument("--id", type=int, required=True)
    p_mark.add_argument("--status", type=str, required=True, help="NEW/DOING/DONE/SKIP")
    p_mark.add_argument("--note", type=str, default="", help="optional note")
    p_mark.set_defaults(cmd="mark")

    p_list = sub.add_parser("list", help="list actions")
    p_list.add_argument("--status", type=str, default="", help="optional filter: NEW/DOING/DONE/SKIP")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(cmd="list")

    args = parser.parse_args()

    conn = db_connect(db_path)
    try:
        ensure_tables(conn)

        if args.cmd == "init":
            print("[actions] ok: trend_actions ready")
            return

        if args.cmd == "latest":
            t = get_latest_trend(conn)
            if not t:
                print("[actions] no trends found")
                return
            print(json.dumps(t, ensure_ascii=False, indent=2))
            return

        if args.cmd == "show":
            show_trend(conn, args.id)
            return

        if args.cmd == "mark":
            upsert_action(conn, args.id, args.status, args.note)
            print(f"[actions] ok: id={args.id} status={args.status.upper()} note={args.note}")
            return

        if args.cmd == "list":
            status = (args.status or "").strip() or None
            rows = list_actions(conn, status, args.limit)
            print(json.dumps(rows, ensure_ascii=False, indent=2))
            return

    finally:
        conn.close()


if __name__ == "__main__":
    main()