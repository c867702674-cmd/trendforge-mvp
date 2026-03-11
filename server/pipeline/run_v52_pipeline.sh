#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V52 pipeline start ==="

echo "[1/3] migrate_v52.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v52.sql"

echo "[2/3] sales_home_builder_v52.py"
python3 "$ROOT/engines/sales_home_builder_v52.py"

echo "[3/3] sales_home_v52_api.py"
python3 "$ROOT/api/sales_home_v52_api.py"

echo "=== TrendForge V52 pipeline end ==="
