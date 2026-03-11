#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V58 pipeline start ==="

echo "[1/3] migrate_v58.sql"
sqlite3 trendforge.db < sql/migrate_v58.sql

echo "[2/3] risk_ip_scan_engine_v58.py"
python3 risk_ip_scan_engine_v58.py

echo "[3/3] risk_ip_scan_v58_api.py"
python3 risk_ip_scan_v58_api.py

echo "=== TrendForge V58 pipeline end ==="