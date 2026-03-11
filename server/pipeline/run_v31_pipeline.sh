
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V31 pipeline start ==="

echo "[1/3] migrate_v31.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v31.sql"

echo "[2/3] user_seed_engine_v1.py"
python3 "$ROOT/engines/user_seed_engine_v1.py"

echo "[3/3] user_api_v1.py"
python3 "$ROOT/api/user_api_v1.py"

echo "=== TrendForge V31 pipeline end ==="
