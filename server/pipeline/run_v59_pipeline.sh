#!/usr/bin/env bash
set -e

cd /root/trendforge-mvp/server

echo "=== TrendForge V59 pipeline start ==="

echo "[1/3] migrate_v59.sql"
sqlite3 trendforge.db < sql/migrate_v59.sql

echo "[2/3] listing_generator_v59.py"
python3 engines/listing_generator_v59.py

echo "[3/3] listing_v59_api.py"
python3 api/listing_v59_api.py

echo "=== TrendForge V59 pipeline end ==="
