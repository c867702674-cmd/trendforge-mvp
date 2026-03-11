#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V40 pipeline start ==="

echo "[1/3] migrate_v40.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v40.sql"

echo "[2/3] feishu_auto_push_v1.py"
python3 "$ROOT/engines/feishu_auto_push_v1.py"

echo "[3/3] feishu_push_v40_api.py"
python3 "$ROOT/api/feishu_push_v40_api.py"

echo "=== TrendForge V40 pipeline end ==="
