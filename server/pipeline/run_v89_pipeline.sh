#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V89 pipeline start ==="
echo "[1/3] migrate_v89.sql"
sqlite3 trendforge.db < sql/migrate_v89.sql
echo "[2/3] trend_data_v89.py"
python3 engines/trend_data_v89.py
echo "[3/3] trend_data_v89_api.py"
python3 api/trend_data_v89_api.py
echo "=== TrendForge V89 pipeline end ==="
