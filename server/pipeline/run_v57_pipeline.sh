#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V57 pipeline start ==="

echo "[1/3] migrate_v57.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v57.sql"

echo "[2/3] trend_expansion_engine_v57.py"
python3 "$ROOT/engines/trend_expansion_engine_v57.py"

echo "[3/3] trend_expansion_v57_api.py"
python3 "$ROOT/api/trend_expansion_v57_api.py"

echo "=== TrendForge V57 pipeline end ==="
