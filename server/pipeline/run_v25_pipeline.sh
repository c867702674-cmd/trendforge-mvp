
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V25 pipeline start ==="

echo "[1/3] migrate_v25.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v25.sql"

echo "[2/3] pod_niche_profit_engine_v1.py"
python3 "$ROOT/engines/pod_niche_profit_engine_v1.py"

echo "[3/3] pod_niche_profit_api.py"
python3 "$ROOT/api/pod_niche_profit_api.py"

echo "=== TrendForge V25 pipeline end ==="
