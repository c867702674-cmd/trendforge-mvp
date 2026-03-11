#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/trendforge-mvp/server"

mkdir -p "$ROOT/pipeline"
mkdir -p "$ROOT/sources"
mkdir -p "$ROOT/engines"
mkdir -p "$ROOT/push"
mkdir -p "$ROOT/sql"
mkdir -p "$ROOT/docs"
mkdir -p "$ROOT/legacy_root"

echo "[OK] V9 structure folders created under $ROOT"
find "$ROOT" -maxdepth 1 -type d | sort
