#!/usr/bin/env bash
set -u

ROOT="/root/trendforge-mvp/server"
ENV_FILE="/etc/trendforge-v6.env"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

cd "$ROOT" || exit 1

echo "=== TrendForge V9 pipeline start: $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="

echo "[0/10] sql/migrate_v85.sql"
sqlite3 "${DB_PATH:-trendforge.db}" < "$ROOT/sql/migrate_v85.sql" || echo "WARN: migrate_v85.sql failed (continuing)"

echo "[1/10] sources/fetch_google_trends_serpapi.py"
python3 "$ROOT/sources/fetch_google_trends_serpapi.py" || echo "WARN: fetch_google_trends_serpapi.py failed (continuing)"

echo "[2/10] sources/fetch_etsy_pod_v2.py"
python3 "$ROOT/sources/fetch_etsy_pod_v2.py" || echo "WARN: fetch_etsy_pod_v2.py failed (continuing)"

echo "[3/10] sources/fetch_amazon_pod_terms_v2.py"
python3 "$ROOT/sources/fetch_amazon_pod_terms_v2.py" || echo "WARN: fetch_amazon_pod_terms_v2.py failed (continuing)"

echo "[4/10] sources/fetch_tiktok_pod_trends_v1.py"
python3 "$ROOT/sources/fetch_tiktok_pod_trends_v1.py" || echo "WARN: fetch_tiktok_pod_trends_v1.py failed (continuing)"

echo "[5/10] engines/extract_pod_keywords.py"
python3 "$ROOT/engines/extract_pod_keywords.py" || echo "WARN: extract_pod_keywords.py failed (continuing)"

echo "[6/10] engines/build_trends_from_raw.py"
python3 "$ROOT/engines/build_trends_from_raw.py" || echo "WARN: build_trends_from_raw.py failed (continuing)"

echo "[7/10] engines/trend_expansion_engine_v2.py"
python3 "$ROOT/engines/trend_expansion_engine_v2.py" || echo "WARN: trend_expansion_engine_v2.py failed (continuing)"

echo "[8/10] engines/mj_prompt_generator.py"
python3 "$ROOT/engines/mj_prompt_generator.py" || echo "WARN: mj_prompt_generator.py failed (continuing)"

echo "[9/10] push/push_trends_feishu_v711.py"
python3 "$ROOT/push/push_trends_feishu_v711.py" || echo "WARN: push_trends_feishu_v711.py failed (continuing)"

echo "=== TrendForge V9 pipeline end:   $(date -u +'%Y-%m-%dT%H:%M:%SZ') ==="
