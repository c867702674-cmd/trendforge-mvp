#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
SKU_PRODUCTS = [p.strip() for p in os.getenv("SKU_PRODUCTS", "shirt,hoodie,sticker,mug,poster").split(",") if p.strip()]

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS sku_packs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      trend_id INTEGER NOT NULL,
      product_type TEXT NOT NULL,
      title_seed TEXT,
      tags_json TEXT,
      score REAL DEFAULT 0,
      payload_json TEXT,
      created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_sku_packs_trend ON sku_packs(trend_id);
    """); conn.commit()
def fetch_trends(conn):
    return conn.execute("SELECT id, term, COALESCE(hit_score,0) AS hit_score FROM trends WHERE action_level='DO_NOW' ORDER BY hit_score DESC LIMIT 50").fetchall()
def main():
    conn = connect(); ensure_schema(conn); trends = fetch_trends(conn); inserted = 0
    for tr in trends:
        trend_id, term = int(tr["id"]), str(tr["term"]).strip()
        conn.execute("DELETE FROM sku_packs WHERE trend_id=?", (trend_id,))
        for idx, product in enumerate(SKU_PRODUCTS, start=1):
            title_seed = f"{term} {product}"
            tags = [term, product, "pod", "gift", "trend"]
            conn.execute("INSERT INTO sku_packs(trend_id, product_type, title_seed, tags_json, score, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (trend_id, product, title_seed, json.dumps(tags, ensure_ascii=False), float(100-idx), json.dumps({"trend_term": term, "product_type": product}, ensure_ascii=False), utc_now_iso()))
            inserted += 1
    conn.commit(); print(f"[OK] sku_pack_engine inserted={inserted} db={DB_PATH}"); conn.close()
if __name__ == "__main__": main()
