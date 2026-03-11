#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V94 pipeline start ==="
echo "[1/3] migrate_v94.sql"
sqlite3 trendforge.db < sql/migrate_v94.sql
echo "[2/3] feishu_webhook_v94.py"
python3 engines/feishu_webhook_v94.py
echo "[3/3] feishu_webhook_v94_api.py"
python3 api/feishu_webhook_v94_api.py
echo "=== TrendForge V94 pipeline end ==="
