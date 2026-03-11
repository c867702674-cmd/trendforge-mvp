#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V35 pipeline start ==="

echo "[1/3] migrate_v35.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v35.sql"

echo "[2/3] seller_flow_orchestrator_v1.py"
python3 "$ROOT/engines/seller_flow_orchestrator_v1.py"

echo "[3/3] seller_flow_v35_api.py"
python3 "$ROOT/api/seller_flow_v35_api.py"

echo "=== TrendForge V35 pipeline end ==="
