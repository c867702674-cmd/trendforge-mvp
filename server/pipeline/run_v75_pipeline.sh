#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V75 pipeline start ==="

echo "[1/3] migrate_v75.sql"
sqlite3 trendforge.db < sql/migrate_v75.sql

echo "[2/3] dispatch_center_v75.py"
python3 engines/dispatch_center_v75.py

echo "[3/3] dispatch_center_v75_api.py"
python3 api/dispatch_center_v75_api.py

echo "=== TrendForge V75 pipeline end ==="
