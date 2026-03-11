#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V66 pipeline start ==="

echo "[1/3] migrate_v66.sql"
sqlite3 trendforge.db < sql/migrate_v66.sql

echo "[2/3] mission_planner_v66.py"
python3 engines/mission_planner_v66.py

echo "[3/3] mission_planner_v66_api.py"
python3 api/mission_planner_v66_api.py

echo "=== TrendForge V66 pipeline end ==="
