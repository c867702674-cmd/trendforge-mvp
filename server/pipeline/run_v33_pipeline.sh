#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V33 pipeline start ==="

echo "[1/3] migrate_v33.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v33.sql"

echo "[2/3] opportunity_cards_engine_v1.py"
python3 "$ROOT/engines/opportunity_cards_engine_v1.py"

echo "[3/3] opportunity_cards_v33_api.py"
python3 "$ROOT/api/opportunity_cards_v33_api.py"

echo "=== TrendForge V33 pipeline end ==="
