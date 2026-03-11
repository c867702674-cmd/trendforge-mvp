#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V41 pipeline start ==="

echo "[1/3] migrate_v41.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v41.sql"

echo "[2/3] push_control_center_v1.py"
python3 "$ROOT/engines/push_control_center_v1.py"

echo "[3/3] push_control_v41_api.py"
python3 "$ROOT/api/push_control_v41_api.py"

echo "=== TrendForge V41 pipeline end ==="
