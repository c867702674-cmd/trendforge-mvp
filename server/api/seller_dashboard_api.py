#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
OUTPUT_DIR = os.getenv("DASHBOARD_OUTPUT_DIR", "/root/trendforge-mvp/server/docs")
DEFAULT_SELLER_EMAIL = os.getenv("DEFAULT_SELLER_EMAIL", "owner@trendforge.local")
TOP_LISTINGS = int(os.getenv("SELLER_DASHBOARD_LISTINGS", "20"))
TOP_PACKS = int(os.getenv("SELLER_DASHBOARD_PACKS", "20"))

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_seller(conn):
    return conn.execute(
        "SELECT id, email, name, tier FROM seller_accounts WHERE email=?",
        (DEFAULT_SELLER_EMAIL,)
    ).fetchone()

def fetch_saved_trends(conn, seller_id):
    rows = conn.execute("""
        SELECT t.id, t.term, t.action_level,
               COALESCE(t.hit_score,0) AS hit_score,
               COALESCE(t.pod_relevance_score,0) AS pod_relevance_score
        FROM seller_saved_trends s
        JOIN trends t ON t.id=s.trend_id
        WHERE s.seller_id=?
        ORDER BY t.hit_score DESC, t.id ASC
        LIMIT 20
    """, (seller_id,)).fetchall()
    return [dict(r) for r in rows]

def fetch_execution_packs(conn):
    if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='execution_packs'").fetchone():
        return []
    rows = conn.execute("""
        SELECT id, trend_id, COALESCE(score,0) AS score, pack_json
        FROM execution_packs
        ORDER BY score DESC, id ASC
        LIMIT ?
    """, (TOP_PACKS,)).fetchall()
    out = []
    for r in rows:
        try:
            pack = json.loads(r["pack_json"] or "{}")
        except Exception:
            pack = {}
        out.append({
            "id": int(r["id"]),
            "trend_id": int(r["trend_id"]),
            "score": float(r["score"] or 0),
            "title": str(pack.get("title") or ""),
            "trend_term": str(pack.get("trend_term") or ""),
            "rank_score": float(pack.get("rank_score") or 0),
            "tags": pack.get("tags") if isinstance(pack.get("tags"), list) else [],
        })
    return out

def fetch_amazon_listings(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(listing_drafts)").fetchall()]
    if "amazon_title" not in cols:
        return []
    rows = conn.execute("""
        SELECT id, trend_id, amazon_title, amazon_description, amazon_search_terms,
               COALESCE(rank_score,0) AS rank_score
        FROM listing_drafts
        WHERE amazon_title IS NOT NULL AND amazon_title != ''
        ORDER BY rank_score DESC, id ASC
        LIMIT ?
    """, (TOP_LISTINGS,)).fetchall()
    return [dict(r) for r in rows]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect()
    seller = fetch_seller(conn)
    payload = {
        "generated_at": utc_now_iso(),
        "seller": None,
        "kpis": {"saved_trends": 0, "execution_packs": 0, "amazon_listings": 0},
        "saved_trends": [],
        "execution_packs": [],
        "amazon_listings": [],
    }
    if seller:
        payload["seller"] = dict(seller)
        payload["saved_trends"] = fetch_saved_trends(conn, int(seller["id"]))
    payload["execution_packs"] = fetch_execution_packs(conn)
    payload["amazon_listings"] = fetch_amazon_listings(conn)
    payload["kpis"] = {
        "saved_trends": len(payload["saved_trends"]),
        "execution_packs": len(payload["execution_packs"]),
        "amazon_listings": len(payload["amazon_listings"]),
    }
    out_path = os.path.join(OUTPUT_DIR, "seller_dashboard_api.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[OK] seller_dashboard_api wrote={out_path} saved_trends={len(payload['saved_trends'])} packs={len(payload['execution_packs'])} listings={len(payload['amazon_listings'])} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
