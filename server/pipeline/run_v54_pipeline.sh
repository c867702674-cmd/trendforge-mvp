#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V54 pipeline start ==="

echo "[1/3] migrate_v54.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v54.sql"

echo "[2/3] ai_listing_engine_v54.py"
python3 "$ROOT/engines/ai_listing_engine_v54.py"

echo "[3/3] ai_listing_v54_api.py"
python3 "$ROOT/api/ai_listing_v54_api.py"

echo "=== TrendForge V54 pipeline end ==="
