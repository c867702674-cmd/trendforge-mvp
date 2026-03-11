#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V71 pipeline start ==="

echo "[1/3] migrate_v71.sql"
sqlite3 trendforge.db < sql/migrate_v71.sql

echo "[2/3] executive_grid_v71.py"
python3 engines/executive_grid_v71.py

echo "[3/3] executive_grid_v71_api.py"
python3 api/executive_grid_v71_api.py

echo "=== TrendForge V71 pipeline end ==="
