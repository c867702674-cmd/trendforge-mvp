#!/usr/bin/env bash
set -u
ROOT="/root/trendforge-mvp/server"

echo "=== TrendForge V21 pipeline start ==="

echo "[1/8] migrate_v21.sql"
sqlite3 "$ROOT/trendforge.db" < "$ROOT/sql/migrate_v21.sql"

echo "[2/8] fetch_tiktok_hashtag_trends_v1.py"
python3 "$ROOT/sources/fetch_tiktok_hashtag_trends_v1.py"

echo "[3/8] fetch_tiktok_sound_trends_v2.py"
python3 "$ROOT/sources/fetch_tiktok_sound_trends_v2.py"

echo "[4/8] tiktok_pod_signal_engine_v1.py"
python3 "$ROOT/engines/tiktok_pod_signal_engine_v1.py"

echo "[5/8] tiktok_semantic_bridge_v1.py"
python3 "$ROOT/engines/tiktok_semantic_bridge_v1.py"

echo "[6/8] build_trends_from_raw.py"
python3 "$ROOT/engines/build_trends_from_raw.py" || true

echo "[7/8] tiktok_trend_api.py"
python3 "$ROOT/api/tiktok_trend_api.py"

echo "[8/8] dashboard_api.py"
python3 "$ROOT/api/dashboard_api.py" || true

echo "=== TrendForge V21 pipeline end ==="
