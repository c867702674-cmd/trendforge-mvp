#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V62 pipeline start ==="

echo "[1/3] migrate_v62.sql"
sqlite3 trendforge.db < sql/migrate_v62.sql

echo "[2/3] publish_board_v62.py"
python3 engines/publish_board_v62.py

echo "[3/3] publish_board_v62_api.py"
python3 api/publish_board_v62_api.py

echo "=== TrendForge V62 pipeline end ==="
