#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V92 pipeline start ==="
echo "[1/3] migrate_v92.sql"
sqlite3 trendforge.db < sql/migrate_v92.sql
echo "[2/3] automation_hub_v92.py"
python3 engines/automation_hub_v92.py
echo "[3/3] automation_hub_v92_api.py"
python3 api/automation_hub_v92_api.py
echo "=== TrendForge V92 pipeline end ==="
