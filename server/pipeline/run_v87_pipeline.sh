#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V87 pipeline start ==="
echo "[1/3] migrate_v87.sql"
sqlite3 trendforge.db < sql/migrate_v87.sql
echo "[2/3] command_center_v87.py"
python3 engines/command_center_v87.py
echo "[3/3] command_center_v87_api.py"
python3 api/command_center_v87_api.py
echo "=== TrendForge V87 pipeline end ==="
