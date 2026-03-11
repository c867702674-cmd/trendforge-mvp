#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V80 pipeline start ==="
echo "[1/3] migrate_v80.sql"
sqlite3 trendforge.db < sql/migrate_v80.sql
echo "[2/3] saas_dashboard_v80.py"
python3 engines/saas_dashboard_v80.py
echo "[3/3] saas_dashboard_v80_api.py"
python3 api/saas_dashboard_v80_api.py
echo "=== TrendForge V80 pipeline end ==="
