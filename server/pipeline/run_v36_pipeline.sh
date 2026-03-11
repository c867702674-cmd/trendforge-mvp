#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V36 pipeline start ==="

echo "[1/3] migrate_v36.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v36.sql"

echo "[2/3] execution_pack_distributor_v1.py"
python3 "$ROOT/engines/execution_pack_distributor_v1.py"

echo "[3/3] execution_pack_distribution_v36_api.py"
python3 "$ROOT/api/execution_pack_distribution_v36_api.py"

echo "=== TrendForge V36 pipeline end ==="
