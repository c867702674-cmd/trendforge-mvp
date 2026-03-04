mkdir -p scripts

cat > scripts/deploy.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/trendforge-mvp"
cd "$ROOT"

echo "[1/4] git pull..."
git pull --rebase

echo "[2/4] venv check..."
if [ ! -d "$ROOT/venv" ]; then
  python3 -m venv "$ROOT/venv"
fi

echo "[3/4] install requirements..."
source "$ROOT/venv/bin/activate"
pip install -U pip
if [ -f "$ROOT/server/requirements.txt" ]; then
  pip install -r "$ROOT/server/requirements.txt"
fi

echo "[4/4] restart services (if exists)..."
systemctl daemon-reload || true
systemctl restart trendforge-api.service 2>/dev/null || true
systemctl restart trendforge-feishu-push.service 2>/dev/null || true

echo "[OK] deploy done"
EOF

chmod +x scripts/deploy.sh