
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V29 pipeline start ==="

echo "[1/3] migrate_v29.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v29.sql"

echo "[2/3] web_dashboard_bundle_engine_v1.py"
python3 "$ROOT/engines/web_dashboard_bundle_engine_v1.py"

echo "[3/3] web_dashboard_v29_api.py"
python3 "$ROOT/api/web_dashboard_v29_api.py"

echo "=== TrendForge V29 pipeline end ==="
