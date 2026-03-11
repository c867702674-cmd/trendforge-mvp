#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V72 pipeline start ==="

echo "[1/3] migrate_v72.sql"
sqlite3 trendforge.db < sql/migrate_v72.sql

echo "[2/3] portfolio_matrix_v72.py"
python3 engines/portfolio_matrix_v72.py

echo "[3/3] portfolio_matrix_v72_api.py"
python3 api/portfolio_matrix_v72_api.py

echo "=== TrendForge V72 pipeline end ==="
