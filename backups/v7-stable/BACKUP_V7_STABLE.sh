#!/usr/bin/env bash
set -euo pipefail

TS=$(date +%Y%m%d_%H%M%S)
ROOT="/root/trendforge-mvp"
SERVER="$ROOT/server"
BACKUP_DIR="$ROOT/backups/v7_stable_$TS"

mkdir -p "$BACKUP_DIR"

echo "[INFO] creating backup dir: $BACKUP_DIR"

# Core pipeline / env
cp "$SERVER/run_v7_pipeline.sh" "$BACKUP_DIR/" 2>/dev/null || true
cp "/etc/trendforge-v6.env" "$BACKUP_DIR/" 2>/dev/null || true

# Core V7 chain
cp "$SERVER/trend_filter_pod_v2.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/trend_expansion_engine_v2.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/mj_prompt_generator.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/push_trends_feishu_v7.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/push_trends_feishu.py" "$BACKUP_DIR/" 2>/dev/null || true

# Data / scoring
cp "$SERVER/fetch_trends_rss.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/fetch_etsy_pod.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/build_trends_from_raw.py" "$BACKUP_DIR/" 2>/dev/null || true

# Migrations / DB
cp "$SERVER/migrate_v7.sql" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/create_design_ideas.sql" "$BACKUP_DIR/" 2>/dev/null || true
cp "$SERVER/trendforge.db" "$BACKUP_DIR/" 2>/dev/null || true

echo "[INFO] backup complete: $BACKUP_DIR"
ls -lah "$BACKUP_DIR"
