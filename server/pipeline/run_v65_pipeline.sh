#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V65 pipeline start ==="

echo "[1/3] migrate_v65.sql"
sqlite3 trendforge.db < sql/migrate_v65.sql

echo "[2/3] batch_studio_v65.py"
python3 engines/batch_studio_v65.py

echo "[3/3] batch_studio_v65_api.py"
python3 api/batch_studio_v65_api.py

echo "=== TrendForge V65 pipeline end ==="
