#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V37 pipeline start ==="

echo "[1/3] migrate_v37.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v37.sql"

echo "[2/3] push_ready_engine_v1.py"
python3 "$ROOT/engines/push_ready_engine_v1.py"

echo "[3/3] push_ready_v37_api.py"
python3 "$ROOT/api/push_ready_v37_api.py"

echo "=== TrendForge V37 pipeline end ==="
