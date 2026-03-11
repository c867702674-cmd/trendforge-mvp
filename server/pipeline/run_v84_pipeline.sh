#!/usr/bin/env bash
set -e
cd /root/trendforge-mvp/server
echo "=== TrendForge V84 pipeline start ==="
echo "[1/3] migrate_v84.sql"
sqlite3 trendforge.db < sql/migrate_v84.sql
echo "[2/3] launch_checklist_v84.py"
python3 engines/launch_checklist_v84.py
echo "[3/3] launch_checklist_v84_api.py"
python3 api/launch_checklist_v84_api.py
echo "=== TrendForge V84 pipeline end ==="
