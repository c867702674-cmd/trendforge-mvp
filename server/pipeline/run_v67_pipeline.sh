#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V67 pipeline start ==="

echo "[1/3] migrate_v67.sql"
sqlite3 trendforge.db < sql/migrate_v67.sql

echo "[2/3] control_tower_v67.py"
python3 engines/control_tower_v67.py

echo "[3/3] control_tower_v67_api.py"
python3 api/control_tower_v67_api.py

echo "=== TrendForge V67 pipeline end ==="
