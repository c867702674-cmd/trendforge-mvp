#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V76 pipeline start ==="

echo "[1/3] migrate_v76.sql"
sqlite3 trendforge.db < sql/migrate_v76.sql

echo "[2/3] launch_orchestrator_v76.py"
python3 engines/launch_orchestrator_v76.py

echo "[3/3] launch_orchestrator_v76_api.py"
python3 api/launch_orchestrator_v76_api.py

echo "=== TrendForge V76 pipeline end ==="
