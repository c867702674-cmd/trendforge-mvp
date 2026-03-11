#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V34 pipeline start ==="

echo "[1/3] migrate_v34.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v34.sql"

echo "[2/3] seller_alert_engine_v1.py"
python3 "$ROOT/engines/seller_alert_engine_v1.py"

echo "[3/3] seller_alerts_v34_api.py"
python3 "$ROOT/api/seller_alerts_v34_api.py"

echo "=== TrendForge V34 pipeline end ==="
