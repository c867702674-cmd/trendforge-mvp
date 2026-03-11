#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V50 pipeline start ==="

echo "[1/3] migrate_v50.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v50.sql"

echo "[2/3] ai_trend_score_engine_v50.py"
python3 "$ROOT/engines/ai_trend_score_engine_v50.py"

echo "[3/3] ai_trend_score_api_v50.py"
python3 "$ROOT/api/ai_trend_score_api_v50.py"

echo "=== TrendForge V50 pipeline end ==="
