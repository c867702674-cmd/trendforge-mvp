#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

INTENT_RULES = [
    ("gift_intent", ["gift", "mom", "dad", "teacher", "nurse"]),
    ("decor_intent", ["decor", "room", "desk", "poster", "wall"]),
    ("apparel_intent", ["shirt", "hoodie", "outfit", "tee"]),
    ("pet_intent", ["cat", "dog", "pet"]),
    ("aesthetic_intent", ["coquette", "soft girl", "clean girl", "minimalist", "retro"]),
]

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def classify(term):
    tl = (term or "").lower()
    for label, kws in INTENT_RULES:
        if any(k in tl for k in kws):
            return label
    return "general_intent"

def main():
    conn = connect()
    rows = conn.execute("SELECT id, term FROM tiktok_trend_signals WHERE COALESCE(intent_label,'')=''").fetchall()
    updated = 0
    for r in rows:
        label = classify(r["term"])
        conn.execute("UPDATE tiktok_trend_signals SET intent_label=? WHERE id=?", (label, int(r["id"])))
        updated += 1
    conn.commit()
    print(f"[OK] tiktok_pod_signal_engine_v1 updated={updated} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
