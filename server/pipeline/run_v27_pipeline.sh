
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V27 pipeline start ==="

echo "[1/3] migrate_v27.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v27.sql"

echo "[2/3] listing_auto_generator_v1.py"
python3 "$ROOT/engines/listing_auto_generator_v1.py"

echo "[3/3] listing_auto_generator_api.py"
python3 "$ROOT/api/listing_auto_generator_api.py"

echo "=== TrendForge V27 pipeline end ==="
