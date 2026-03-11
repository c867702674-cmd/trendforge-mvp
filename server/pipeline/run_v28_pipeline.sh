
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V28 pipeline start ==="

echo "[1/3] migrate_v28.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v28.sql"

echo "[2/3] seller_dashboard_snapshot_engine_v1.py"
python3 "$ROOT/engines/seller_dashboard_snapshot_engine_v1.py"

echo "[3/3] seller_dashboard_v28_api.py"
python3 "$ROOT/api/seller_dashboard_v28_api.py"

echo "=== TrendForge V28 pipeline end ==="
