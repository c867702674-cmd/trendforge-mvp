#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
GOOD_HINTS = {"gift","mom","dad","teacher","nurse","cat","dog","retro","vintage","minimalist","line art","funny","cute","shirt","hoodie","mug","sticker","poster","patch","boho","golf","birthday","holiday"}
BAD_HINTS = {"election","politic","war","conflict","forecast","storm","hurricane","snow","earthquake","recall","stock","earnings"}

def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_column(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(trends);").fetchall()]
    if "pod_relevance_score" not in cols:
        conn.execute("ALTER TABLE trends ADD COLUMN pod_relevance_score REAL DEFAULT 0;")
    conn.commit()
def calc(term):
    tl = (term or "").lower()
    score = 0.0
    for g in GOOD_HINTS:
        if g in tl: score += 12.0
    for b in BAD_HINTS:
        if b in tl: score -= 18.0
    toks = re.sub(r"[^a-z0-9\s&'-]+", " ", tl).split()
    if len(toks) <= 2: score -= 4.0
    return score
def main():
    conn = connect(); ensure_column(conn)
    rows = conn.execute("SELECT id, term FROM trends ORDER BY id ASC").fetchall()
    updated = 0
    for r in rows:
        conn.execute("UPDATE trends SET pod_relevance_score=? WHERE id=?", (float(calc(str(r['term'] or ''))), int(r["id"])))
        updated += 1
    conn.commit()
    print(f"[OK] pod_relevance_filter_v1 updated={updated} db={DB_PATH}")
    conn.close()
if __name__ == "__main__":
    main()
