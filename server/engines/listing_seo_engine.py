#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
SEO_TAG_LIMIT = int(os.getenv("SEO_TAG_LIMIT", "12"))

def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn

def fetch_keywords(conn, limit=200):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pod_keywords'").fetchone():
        return []
    rows = conn.execute("SELECT keyword, COALESCE(score,0) AS score FROM pod_keywords ORDER BY score DESC, id ASC LIMIT ?", (limit,)).fetchall()
    return [str(r["keyword"]) for r in rows]

def ensure_columns(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts);").fetchall()]
    if "quality_json" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN quality_json TEXT;")
    if "rank_score" not in cols:
        conn.execute("ALTER TABLE listing_drafts ADD COLUMN rank_score REAL DEFAULT 0;")
    conn.commit()

def main():
    conn = connect(); ensure_columns(conn)
    kws = fetch_keywords(conn, 200)
    if not kws:
        print(f"[WARN] listing_seo_engine no pod_keywords found db={DB_PATH}")
        conn.close(); return
    rows = conn.execute("SELECT id, title, tags_json, quality_json FROM listing_drafts ORDER BY id ASC").fetchall()
    updated = 0
    for r in rows:
        try: tags = json.loads(r["tags_json"] or "[]")
        except Exception: tags = []
        if not isinstance(tags, list): tags = []
        title = str(r["title"] or "").lower()
        extra = []
        for kw in kws:
            if kw in title and kw not in tags and kw not in extra:
                extra.append(kw)
            if len(extra) >= 5: break
        merged = tags + extra
        out, seen = [], set()
        for x in [str(x).strip() for x in merged if str(x).strip()]:
            if x not in seen: seen.add(x); out.append(x)
        out = out[:SEO_TAG_LIMIT]
        try: qj = json.loads(r["quality_json"] or "{}")
        except Exception: qj = {}
        qj["seo_tags"] = out
        conn.execute("UPDATE listing_drafts SET tags_json=?, quality_json=? WHERE id=?",
                     (json.dumps(out, ensure_ascii=False), json.dumps(qj, ensure_ascii=False), int(r["id"])))
        updated += 1
    conn.commit(); print(f"[OK] listing_seo_engine updated={updated} db={DB_PATH}"); conn.close()

if __name__ == "__main__": main()
