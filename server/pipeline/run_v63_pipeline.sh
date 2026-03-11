#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V63 pipeline start ==="

echo "[1/3] migrate_v63.sql"
sqlite3 trendforge.db < sql/migrate_v63.sql

echo "[2/3] ops_dashboard_v63.py"
python3 engines/ops_dashboard_v63.py

echo "[3/3] ops_dashboard_v63_api.py"
python3 api/ops_dashboard_v63_api.py

echo "=== TrendForge V63 pipeline end ==="
