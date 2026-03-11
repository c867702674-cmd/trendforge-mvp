#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V78 pipeline start ==="
echo "[1/3] migrate_v78.sql"
sqlite3 trendforge.db < sql/migrate_v78.sql
echo "[2/3] release_command_v78.py"
python3 engines/release_command_v78.py
echo "[3/3] release_command_v78_api.py"
python3 api/release_command_v78_api.py
echo "=== TrendForge V78 pipeline end ==="
