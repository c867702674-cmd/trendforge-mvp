
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V24 pipeline start ==="

echo "[1/3] migrate_v24.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v24.sql"

echo "[2/3] auto_trend_discovery_engine_v1.py"
python3 "$ROOT/engines/auto_trend_discovery_engine_v1.py"

echo "[3/3] auto_trend_discovery_api.py"
python3 "$ROOT/api/auto_trend_discovery_api.py"

echo "=== TrendForge V24 pipeline end ==="
