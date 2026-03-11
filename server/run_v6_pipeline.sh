#!/usr/bin/env bash
# TrendForge V6 Pipeline Runner (with Trend Expansion Engine inserted)
# Runs hourly via systemd timer: trendforge-v6-pipeline.timer
# Non-blocking: each step failure won't stop the pipeline.

set -u

PROJECT_DIR="/root/trendforge-mvp"
SERVER_DIR="${PROJECT_DIR}/server"

# Load env (if exists). Your env file is documented as: /etc/trendforge-v6.env
ENV_FILE="/etc/trendforge-v6.env"
if [ -f "${ENV_FILE}" ]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

cd "${SERVER_DIR}" || exit 1

echo "=== TrendForge V6 pipeline start: $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="

echo "[1/5] fetch_trends_rss.py"
python3 fetch_trends_rss.py || echo "WARN: fetch_trends_rss.py failed (continuing)"

echo "[2/5] fetch_etsy_pod.py"
python3 fetch_etsy_pod.py || echo "WARN: fetch_etsy_pod.py failed (continuing)"

echo "[3/5] build_trends_from_raw.py"
python3 build_trends_from_raw.py || echo "WARN: build_trends_from_raw.py failed (continuing)"

echo "[4/5] trend_expansion_engine.py"
python3 trend_expansion_engine.py || echo "WARN: trend_expansion_engine.py failed (continuing)"

echo "[5/5] push_trends_feishu.py"
python3 push_trends_feishu.py || echo "WARN: push_trends_feishu.py failed (continuing)"

echo "=== TrendForge V6 pipeline end:   $(date -u +"%Y-%m-%dT%H:%M:%SZ") ==="
