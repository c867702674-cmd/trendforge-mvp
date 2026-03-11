#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V61 pipeline start ==="

echo "[1/3] migrate_v61.sql"
sqlite3 trendforge.db < sql/migrate_v61.sql

echo "[2/3] launch_queue_v61.py"
python3 engines/launch_queue_v61.py

echo "[3/3] launch_queue_v61_api.py"
python3 api/launch_queue_v61_api.py

echo "=== TrendForge V61 pipeline end ==="
