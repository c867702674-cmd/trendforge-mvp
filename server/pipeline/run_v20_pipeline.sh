
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V20 pipeline start ==="

echo "[1/3] migrate_v20.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v20.sql"

echo "[2/3] ai_opportunity_board_engine_v1.py"
python3 "$ROOT/engines/ai_opportunity_board_engine_v1.py"

echo "[3/3] ai_opportunity_board_api.py"
python3 "$ROOT/api/ai_opportunity_board_api.py"

echo "=== TrendForge V20 pipeline end ==="
