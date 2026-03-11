#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V60 pipeline start ==="

echo "[1/3] migrate_v60.sql"
sqlite3 trendforge.db < sql/migrate_v60.sql

echo "[2/3] execution_pack_v60.py"
python3 engines/execution_pack_v60.py

echo "[3/3] execution_pack_v60_api.py"
python3 api/execution_pack_v60_api.py

echo "=== TrendForge V60 pipeline end ==="
