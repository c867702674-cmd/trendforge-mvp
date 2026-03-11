#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/trendforge-mvp/server"

cp "$ROOT/fetch_trends_rss.py" "$ROOT/sources/" 2>/dev/null || true
cp "$ROOT/fetch_google_trends_serpapi.py" "$ROOT/sources/" 2>/dev/null || true
cp "$ROOT/fetch_etsy_pod.py" "$ROOT/sources/" 2>/dev/null || true
cp "$ROOT/fetch_etsy_pod_v2.py" "$ROOT/sources/" 2>/dev/null || true
cp "$ROOT/fetch_amazon_movers_v1.py" "$ROOT/sources/" 2>/dev/null || true
cp "$ROOT/fetch_amazon_pod_terms_v2.py" "$ROOT/sources/" 2>/dev/null || true
cp "$ROOT/fetch_tiktok_pod_trends_v1.py" "$ROOT/sources/" 2>/dev/null || true

cp "$ROOT/build_trends_from_raw.py" "$ROOT/engines/" 2>/dev/null || true
cp "$ROOT/trend_filter_pod.py" "$ROOT/engines/" 2>/dev/null || true
cp "$ROOT/trend_filter_pod_v2.py" "$ROOT/engines/" 2>/dev/null || true
cp "$ROOT/trend_expansion_engine.py" "$ROOT/engines/" 2>/dev/null || true
cp "$ROOT/trend_expansion_engine_v2.py" "$ROOT/engines/" 2>/dev/null || true
cp "$ROOT/mj_prompt_generator.py" "$ROOT/engines/" 2>/dev/null || true
cp "$ROOT/extract_pod_keywords.py" "$ROOT/engines/" 2>/dev/null || true

cp "$ROOT/push_trends_feishu.py" "$ROOT/push/" 2>/dev/null || true
cp "$ROOT/push_trends_feishu_v7.py" "$ROOT/push/" 2>/dev/null || true
cp "$ROOT/push_trends_feishu_v711.py" "$ROOT/push/" 2>/dev/null || true
cp "$ROOT/execution_pack.py" "$ROOT/push/" 2>/dev/null || true

cp "$ROOT/create_design_ideas.sql" "$ROOT/sql/" 2>/dev/null || true
cp "$ROOT/migrate_v7.sql" "$ROOT/sql/" 2>/dev/null || true
cp "$ROOT/migrate_v8.sql" "$ROOT/sql/" 2>/dev/null || true
cp "$ROOT/migrate_v85.sql" "$ROOT/sql/" 2>/dev/null || true

echo "[OK] Current files copied into V9 modular folders"
