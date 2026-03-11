#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V68 pipeline start ==="

echo "[1/3] migrate_v68.sql"
sqlite3 trendforge.db < sql/migrate_v68.sql

echo "[2/3] war_room_v68.py"
python3 engines/war_room_v68.py

echo "[3/3] war_room_v68_api.py"
python3 api/war_room_v68_api.py

echo "=== TrendForge V68 pipeline end ==="
