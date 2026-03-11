#!/usr/bin/env bash
set -u
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V23 pipeline start ==="

echo "[1/3] migrate_v23.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v23.sql"

echo "[2/3] ai_trend_ranking_engine_v1.py"
python3 "$ROOT/engines/ai_trend_ranking_engine_v1.py"

echo "[3/3] ai_trend_ranking_api.py"
python3 "$ROOT/api/ai_trend_ranking_api.py"

echo "=== TrendForge V23 pipeline end ==="
