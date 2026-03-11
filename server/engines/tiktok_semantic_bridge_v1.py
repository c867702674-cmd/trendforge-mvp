#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
BRIDGE_MAP = {
    "coquette": ["pink bow mug", "coquette poster", "pink ribbon shirt"],
    "teacher": ["teacher gift mug", "teacher tote bag", "teacher shirt design"],
    "nurse": ["nurse humor mug", "night shift shirt", "nurse appreciation gift"],
    "cat": ["cat mom mug", "cute cat hoodie", "kitty line art poster"],
    "dog": ["dog mom mug", "pet lover hoodie", "puppy line art sticker"],
    "retro": ["retro typography shirt", "vintage mug design", "retro poster art"],
    "minimalist": ["minimalist line art print", "neutral decor poster", "clean outline shirt"],
}

def utc():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def main():
    conn = connect()
    rows = conn.execute("SELECT DISTINCT term FROM tiktok_trend_signals ORDER BY id DESC LIMIT 100").fetchall()
    conn.execute("DELETE FROM tiktok_semantic_links")
    inserted = 0
    for r in rows:
        term = str(r["term"] or "")
        tl = term.lower()
        bridges = []
        for key, vals in BRIDGE_MAP.items():
            if key in tl:
                bridges.extend(vals)
        toks = tl.split()
        if len(toks) >= 2:
            bridges.append(f"{toks[0]} gift idea")
            bridges.append(f"{toks[0]} shirt design")
        seen = set()
        for idx, b in enumerate(bridges, start=1):
            if b in seen:
                continue
            seen.add(b)
            score = max(1.0, 20 - idx)
            conn.execute(
                "INSERT INTO tiktok_semantic_links(source_term, bridge_term, bridge_score, payload_json, created_at) VALUES (?,?,?,?,?)",
                (term, b, score, json.dumps({"source_term": term, "bridge_term": b}, ensure_ascii=False), utc())
            )
            inserted += 1
    conn.commit()
    print(f"[OK] tiktok_semantic_bridge_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
