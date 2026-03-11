#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V38 pipeline start ==="

echo "[1/3] migrate_v38.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v38.sql"

echo "[2/3] audience_routing_center_v1.py"
python3 "$ROOT/engines/audience_routing_center_v1.py"

echo "[3/3] audience_routes_v38_api.py"
python3 "$ROOT/api/audience_routes_v38_api.py"

echo "=== TrendForge V38 pipeline end ==="
