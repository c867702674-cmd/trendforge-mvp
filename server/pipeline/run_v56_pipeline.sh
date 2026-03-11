
#!/usr/bin/env bash

ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V56 pipeline start ==="

echo "[1/3] migrate_v56.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v56.sql"

echo "[2/3] pod_sku_pack_engine_v56.py"
python3 "$ROOT/engines/pod_sku_pack_engine_v56.py"

echo "[3/3] pod_sku_pack_v56_api.py"
python3 "$ROOT/api/pod_sku_pack_v56_api.py"

echo "=== TrendForge V56 pipeline end ==="
