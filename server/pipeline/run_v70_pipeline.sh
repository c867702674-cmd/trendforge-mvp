#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V70 pipeline start ==="

echo "[1/3] migrate_v70.sql"
sqlite3 trendforge.db < sql/migrate_v70.sql

echo "[2/3] strategic_hub_v70.py"
python3 engines/strategic_hub_v70.py

echo "[3/3] strategic_hub_v70_api.py"
python3 api/strategic_hub_v70_api.py

echo "=== TrendForge V70 pipeline end ==="
