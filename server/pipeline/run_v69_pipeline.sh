#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V69 pipeline start ==="

echo "[1/3] migrate_v69.sql"
sqlite3 trendforge.db < sql/migrate_v69.sql

echo "[2/3] operations_hq_v69.py"
python3 engines/operations_hq_v69.py

echo "[3/3] operations_hq_v69_api.py"
python3 api/operations_hq_v69_api.py

echo "=== TrendForge V69 pipeline end ==="
