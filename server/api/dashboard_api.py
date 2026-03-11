#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")
TOP_TRENDS_LIMIT = int(os.getenv("TOP_TRENDS_LIMIT", "20"))
TOP_PACKS_LIMIT = int(os.getenv("TOP_PACKS_LIMIT", "20"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS dashboard_views (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      view_name TEXT NOT NULL,
      payload_json TEXT,
      created_at TEXT
    );""")
    conn.commit()
def fetch_top_trends(conn):
    rows = conn.execute("SELECT id, term, action_level, COALESCE(hit_score,0) AS hit_score, COALESCE(growth,0) AS growth FROM trends ORDER BY hit_score DESC, id ASC LIMIT ?", (TOP_TRENDS_LIMIT,)).fetchall()
    return [dict(r) for r in rows]
def fetch_top_packs(conn):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='execution_packs'").fetchone():
        return []
    rows = conn.execute("SELECT id, trend_id, COALESCE(score,0) AS score, pack_json FROM execution_packs ORDER BY score DESC, id ASC LIMIT ?", (TOP_PACKS_LIMIT,)).fetchall()
    out = []
    for r in rows:
        try: pack = json.loads(r["pack_json"] or "{}")
        except Exception: pack = {}
        out.append({"id": int(r["id"]), "trend_id": int(r["trend_id"]), "score": float(r["score"] or 0), "title": str(pack.get("title") or ""), "trend_term": str(pack.get("trend_term") or ""), "rank_score": float(pack.get("rank_score") or 0)})
    return out
def save_view(conn, name, payload):
    conn.execute("INSERT INTO dashboard_views(view_name, payload_json, created_at) VALUES (?, ?, ?)", (name, json.dumps(payload, ensure_ascii=False), utc_now_iso()))
    conn.commit()
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect(); ensure_schema(conn)
    top_trends = fetch_top_trends(conn); top_packs = fetch_top_packs(conn)
    payload = {"generated_at": utc_now_iso(), "top_trends": top_trends, "top_execution_packs": top_packs}
    save_view(conn, "dashboard_api", payload)
    out_path = os.path.join(OUTPUT_DIR, "dashboard_api.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[OK] dashboard_api wrote={out_path} trends={len(top_trends)} packs={len(top_packs)} db={DB_PATH}")
    conn.close()
if __name__ == "__main__": main()
