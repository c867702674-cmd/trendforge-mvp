#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V79 pipeline start ==="
echo "[1/3] migrate_v79.sql"
sqlite3 trendforge.db < sql/migrate_v79.sql
echo "[2/3] listing_ai_v79.py"
python3 engines/listing_ai_v79.py
echo "[3/3] listing_ai_v79_api.py"
python3 api/listing_ai_v79_api.py
echo "=== TrendForge V79 pipeline end ==="
