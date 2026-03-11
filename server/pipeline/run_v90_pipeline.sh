#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V90 pipeline start ==="
echo "[1/3] migrate_v90.sql"
sqlite3 trendforge.db < sql/migrate_v90.sql
echo "[2/3] billing_system_v90.py"
python3 engines/billing_system_v90.py
echo "[3/3] billing_system_v90_api.py"
python3 api/billing_system_v90_api.py
echo "=== TrendForge V90 pipeline end ==="
