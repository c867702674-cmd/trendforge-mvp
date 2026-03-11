#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V55 pipeline start ==="

echo "[1/3] migrate_v55.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v55.sql"

echo "[2/3] mj_prompt_engine_v55.py"
python3 "$ROOT/engines/mj_prompt_engine_v55.py"

echo "[3/3] mj_prompt_v55_api.py"
python3 "$ROOT/api/mj_prompt_v55_api.py"

echo "=== TrendForge V55 pipeline end ==="
