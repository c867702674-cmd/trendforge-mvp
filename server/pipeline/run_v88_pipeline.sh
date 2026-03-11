#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V88 pipeline start ==="
echo "[1/3] migrate_v88.sql"
sqlite3 trendforge.db < sql/migrate_v88.sql
echo "[2/3] user_system_v88.py"
python3 engines/user_system_v88.py
echo "[3/3] user_system_v88_api.py"
python3 api/user_system_v88_api.py
echo "=== TrendForge V88 pipeline end ==="
