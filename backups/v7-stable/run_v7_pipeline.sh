#!/usr/bin/env bash
# TrendForge V7.1.1 Pipeline Runner
# This version keeps the V7 chain and switches the final push step to push_trends_feishu_v711.py

set -u

PROJECT_DIR="/root/trendforge-mvp"
SERVER_DIR="${PROJECT_DIR}/server"

ENV_FILE="/etc/trendforge-v6.env"
if [ -f "${ENV_FILE}" ]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

cd "${SERVER_DIR}" || exit 1

echo "=== TrendForge V7.1.1 pipeline start: $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="

echo "[0/6] migrate_v7.sql (safe)"
sqlite3 "${DB_PATH:-trendforge.db}" < migrate_v7.sql || echo "WARN: migrate_v7.sql failed (continuing)"

echo "[1/6] fetch_trends_rss.py"
python3 fetch_trends_rss.py || echo "WARN: fetch_trends_rss.py failed (continuing)"

echo "[2/6] fetch_etsy_pod.py"
python3 fetch_etsy_pod.py || echo "WARN: fetch_etsy_pod.py failed (continuing)"

echo "[3/6] build_trends_from_raw.py"
python3 build_trends_from_raw.py || echo "WARN: build_trends_from_raw.py failed (continuing)"

echo "[4/6] trend_expansion_engine_v2.py"
python3 trend_expansion_engine_v2.py || echo "WARN: trend_expansion_engine_v2.py failed (continuing)"

echo "[5/6] mj_prompt_generator.py"
python3 mj_prompt_generator.py || echo "WARN: mj_prompt_generator.py failed (continuing)"

echo "[6/6] push_trends_feishu_v711.py"
python3 push_trends_feishu_v711.py || echo "WARN: push_trends_feishu_v711.py failed (continuing)"

echo "=== TrendForge V7.1.1 pipeline end:   $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="
