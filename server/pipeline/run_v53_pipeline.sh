#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V53 pipeline start ==="

echo "[1/3] migrate_v53.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v53.sql"

echo "[2/3] main_index_builder_v53.py"
python3 "$ROOT/engines/main_index_builder_v53.py"

echo "[3/3] main_index_v53_api.py"
python3 "$ROOT/api/main_index_v53_api.py"

echo "=== TrendForge V53 pipeline end ==="
