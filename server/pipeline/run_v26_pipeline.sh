
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V26 pipeline start ==="

echo "[1/3] migrate_v26.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v26.sql"

echo "[2/3] seller_opportunity_feed_engine_v1.py"
python3 "$ROOT/engines/seller_opportunity_feed_engine_v1.py"

echo "[3/3] seller_opportunity_feed_api.py"
python3 "$ROOT/api/seller_opportunity_feed_api.py"

echo "=== TrendForge V26 pipeline end ==="
