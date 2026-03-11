#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V82 pipeline start ==="
echo "[1/3] migrate_v82.sql"
sqlite3 trendforge.db < sql/migrate_v82.sql
echo "[2/3] launch_readiness_v82.py"
python3 engines/launch_readiness_v82.py
echo "[3/3] launch_readiness_v82_api.py"
python3 api/launch_readiness_v82_api.py
echo "=== TrendForge V82 pipeline end ==="
