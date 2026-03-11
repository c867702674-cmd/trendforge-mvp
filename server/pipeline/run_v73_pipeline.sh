#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V73 pipeline start ==="

echo "[1/3] migrate_v73.sql"
sqlite3 trendforge.db < sql/migrate_v73.sql

echo "[2/3] allocation_board_v73.py"
python3 engines/allocation_board_v73.py

echo "[3/3] allocation_board_v73_api.py"
python3 api/allocation_board_v73_api.py

echo "=== TrendForge V73 pipeline end ==="
