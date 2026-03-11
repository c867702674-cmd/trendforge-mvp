#!/usr/bin/env bash
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V39 pipeline start ==="

sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v39.sql"

python3 "$ROOT/engines/push_dispatcher_v1.py"

python3 "$ROOT/api/push_dispatch_v39_api.py"

echo "=== TrendForge V39 pipeline end ==="
