#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V32 pipeline start ==="

echo "[1/3] migrate_v32.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v32.sql"

echo "[2/3] subscription_seed_engine_v1.py"
python3 "$ROOT/engines/subscription_seed_engine_v1.py"

echo "[3/3] subscription_api_v1.py"
python3 "$ROOT/api/subscription_api_v1.py"

echo "=== TrendForge V32 pipeline end ==="
