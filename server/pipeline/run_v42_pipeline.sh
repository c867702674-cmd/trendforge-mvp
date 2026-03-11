
#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V42 pipeline start ==="

echo "[1/3] migrate_v42.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v42.sql"

echo "[2/3] push_scheduler_v1.py"
python3 "$ROOT/engines/push_scheduler_v1.py"

echo "[3/3] push_scheduler_v42_api.py"
python3 "$ROOT/api/push_scheduler_v42_api.py"

echo "=== TrendForge V42 pipeline end ==="
