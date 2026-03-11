#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V91 pipeline start ==="
echo "[1/3] migrate_v91.sql"
sqlite3 trendforge.db < sql/migrate_v91.sql
echo "[2/3] push_center_v91.py"
python3 engines/push_center_v91.py
echo "[3/3] push_center_v91_api.py"
python3 api/push_center_v91_api.py
echo "=== TrendForge V91 pipeline end ==="
