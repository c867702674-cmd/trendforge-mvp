#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V83 pipeline start ==="
echo "[1/3] migrate_v83.sql"
sqlite3 trendforge.db < sql/migrate_v83.sql
echo "[2/3] commercial_golive_v83.py"
python3 engines/commercial_golive_v83.py
echo "[3/3] commercial_golive_v83_api.py"
python3 api/commercial_golive_v83_api.py
echo "=== TrendForge V83 pipeline end ==="
