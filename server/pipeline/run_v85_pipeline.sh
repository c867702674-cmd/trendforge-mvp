#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V85 pipeline start ==="
echo "[1/3] migrate_v85.sql"
sqlite3 trendforge.db < sql/migrate_v85.sql
echo "[2/3] commercial_launch_v85.py"
python3 engines/commercial_launch_v85.py
echo "[3/3] commercial_launch_v85_api.py"
python3 api/commercial_launch_v85_api.py
echo "=== TrendForge V85 pipeline end ==="
