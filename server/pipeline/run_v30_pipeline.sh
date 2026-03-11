#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V30 pipeline start ==="

echo "[1/3] migrate_v30.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v30.sql"

echo "[2/3] saas_core_snapshot_engine_v1.py"
python3 "$ROOT/engines/saas_core_snapshot_engine_v1.py"

echo "[3/3] saas_core_v30_api.py"
python3 "$ROOT/api/saas_core_v30_api.py"

echo "=== TrendForge V30 pipeline end ==="
