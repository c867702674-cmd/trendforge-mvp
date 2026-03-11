#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V74 pipeline start ==="

echo "[1/3] migrate_v74.sql"
sqlite3 trendforge.db < sql/migrate_v74.sql

echo "[2/3] release_routing_v74.py"
python3 engines/release_routing_v74.py

echo "[3/3] release_routing_v74_api.py"
python3 api/release_routing_v74_api.py

echo "=== TrendForge V74 pipeline end ==="
