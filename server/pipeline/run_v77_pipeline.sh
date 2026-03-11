#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V77 pipeline start ==="

echo "[1/3] migrate_v77.sql"
sqlite3 trendforge.db < sql/migrate_v77.sql

echo "[2/3] launch_control_v77.py"
python3 engines/launch_control_v77.py

echo "[3/3] launch_control_v77_api.py"
python3 api/launch_control_v77_api.py

echo "=== TrendForge V77 pipeline end ==="
