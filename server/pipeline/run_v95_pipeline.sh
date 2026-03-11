#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V95 pipeline start ==="
echo "[1/3] migrate_v95.sql"
sqlite3 trendforge.db < sql/migrate_v95.sql
echo "[2/3] feishu_card_v95.py"
python3 engines/feishu_card_v95.py
echo "[3/3] feishu_card_v95_api.py"
python3 api/feishu_card_v95_api.py
echo "=== TrendForge V95 pipeline end ==="
