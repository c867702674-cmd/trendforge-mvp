#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V86 pipeline start ==="
echo "[1/3] migrate_v86.sql"
sqlite3 trendforge.db < sql/migrate_v86.sql
echo "[2/3] launch_ops_v86.py"
python3 engines/launch_ops_v86.py
echo "[3/3] launch_ops_v86_api.py"
python3 api/launch_ops_v86_api.py
echo "=== TrendForge V86 pipeline end ==="
