#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")
VIEW_LIMIT = int(os.getenv("EXEC_PACK_VIEW_LIMIT", "30"))

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def fetch_packs(conn):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='execution_packs'").fetchone():
        return []
    rows = conn.execute("SELECT id, trend_id, COALESCE(score,0) AS score, pack_json FROM execution_packs ORDER BY score DESC, id ASC LIMIT ?", (VIEW_LIMIT,)).fetchall()
    out = []
    for r in rows:
        try: pack = json.loads(r["pack_json"] or "{}")
        except Exception: pack = {}
        out.append({"id": int(r["id"]), "trend_id": int(r["trend_id"]), "score": float(r["score"] or 0), "pack": pack})
    return out
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect(); packs = fetch_packs(conn)
    html = ["<!doctype html><html><head><meta charset='utf-8'><title>TrendForge Execution Packs</title>",
            "<style>body{font-family:Arial,sans-serif;margin:24px;background:#f7f7f8}.card{background:#fff;padding:16px;border-radius:12px;margin:12px 0;box-shadow:0 2px 8px rgba(0,0,0,.06)}.meta{color:#666;font-size:13px;margin-bottom:8px}.title{font-size:18px;font-weight:700;margin-bottom:8px}code{background:#f1f1f1;padding:2px 6px;border-radius:6px}</style>",
            "</head><body><h1>TrendForge Execution Packs</h1>",
            f"<p>Generated at {utc_now_iso()}</p>"]
    for item in packs:
        p = item["pack"]
        tags = p.get("tags", [])
        html += [
            "<div class='card'>",
            f"<div class='meta'>Pack #{item['id']} · Trend #{item['trend_id']} · Score {item['score']:.2f}</div>",
            f"<div class='title'>{p.get('title','')}</div>",
            f"<div><b>Trend:</b> {p.get('trend_term','')}</div>",
            f"<div><b>Description:</b> {p.get('description','')}</div>",
            f"<div><b>Tags:</b> <code>{', '.join(tags) if isinstance(tags,list) else ''}</code></div>",
            "</div>"
        ]
    html.append("</body></html>")
    out_path = os.path.join(OUTPUT_DIR, "execution_pack_viewer.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"[OK] execution_pack_viewer wrote={out_path} packs={len(packs)} db={DB_PATH}")
    conn.close()
if __name__ == "__main__": main()
