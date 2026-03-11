#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V64 pipeline start ==="

echo "[1/3] migrate_v64.sql"
sqlite3 trendforge.db < sql/migrate_v64.sql

echo "[2/3] command_center_v64.py"
python3 engines/command_center_v64.py

echo "[3/3] command_center_v64_api.py"
python3 api/command_center_v64_api.py

echo "=== TrendForge V64 pipeline end ==="
