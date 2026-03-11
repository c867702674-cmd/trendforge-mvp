#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DEFAULT_SELLER_EMAIL = os.getenv("DEFAULT_SELLER_EMAIL", "owner@trendforge.local")
DEFAULT_SELLER_NAME = os.getenv("DEFAULT_SELLER_NAME", "TrendForge Owner")
DEFAULT_PROJECT_NAME = os.getenv("DEFAULT_PROJECT_NAME", "Main POD Workspace")

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def connect():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def ensure_schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS seller_accounts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      name TEXT,
      tier TEXT DEFAULT 'trial',
      created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS seller_projects (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      seller_id INTEGER NOT NULL,
      project_name TEXT NOT NULL,
      market TEXT DEFAULT 'US',
      platform TEXT DEFAULT 'amazon',
      created_at TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_seller_projects_name ON seller_projects(seller_id, project_name);
    """)
    conn.commit()

def main():
    conn = connect(); ensure_schema(conn)
    conn.execute("INSERT OR IGNORE INTO seller_accounts(email, name, tier, created_at) VALUES (?, ?, 'owner', ?)",
                 (DEFAULT_SELLER_EMAIL, DEFAULT_SELLER_NAME, utc_now_iso()))
    seller = conn.execute("SELECT id FROM seller_accounts WHERE email=?", (DEFAULT_SELLER_EMAIL,)).fetchone()
    seller_id = int(seller["id"])
    conn.execute("""INSERT OR IGNORE INTO seller_projects(seller_id, project_name, market, platform, created_at)
                    VALUES (?, ?, 'US', 'amazon', ?)""",
                 (seller_id, DEFAULT_PROJECT_NAME, utc_now_iso()))
    conn.commit()
    print(f"[OK] seller_workspace_engine seller_id={seller_id} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
