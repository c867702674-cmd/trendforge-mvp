#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V81 pipeline start ==="
echo "[1/3] migrate_v81.sql"
sqlite3 trendforge.db < sql/migrate_v81.sql
echo "[2/3] mj_prompt_v81.py"
python3 engines/mj_prompt_v81.py
echo "[3/3] mj_prompt_v81_api.py"
python3 api/mj_prompt_v81_api.py
echo "=== TrendForge V81 pipeline end ==="
