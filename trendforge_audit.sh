#!/usr/bin/env bash
set -e

ROOT="/root/trendforge-mvp"
WEB="/var/www/trendforge"
DOCS="$ROOT/server/docs"
OUT="/root/trendforge_audit_report.txt"

echo "=== TrendForge Audit Report ===" > "$OUT"
date >> "$OUT"
echo "" >> "$OUT"

echo "[1] 关键目录" >> "$OUT"
for p in "$ROOT" "$ROOT/web" "$ROOT/server" "$DOCS" "$WEB" "$WEB/docs"; do
  if [ -d "$p" ]; then
    echo "OK DIR  $p" >> "$OUT"
  else
    echo "MISS DIR $p" >> "$OUT"
  fi
done
echo "" >> "$OUT"

echo "[2] 关键首页文件" >> "$OUT"
for f in   "$ROOT/web/index.html"   "$ROOT/web/index.js"   "$ROOT/server/docs/main_index_v53.json"   "$WEB/index.html"   "$WEB/index.js"   "$WEB/docs/main_index_v53.json"; do
  if [ -f "$f" ]; then
    echo "OK FILE  $f" >> "$OUT"
    ls -lh "$f" >> "$OUT"
  else
    echo "MISS FILE $f" >> "$OUT"
  fi
done
echo "" >> "$OUT"

echo "[3] V50 / V51 / V52 / V53 关键产物" >> "$OUT"
for f in   "$DOCS/ai_trend_score_v50.json"   "$DOCS/saas_dashboard_v50.json"   "$DOCS/site_home_v51.json"   "$DOCS/sales_home_v52.json"   "$DOCS/main_index_v53.json"; do
  if [ -f "$f" ]; then
    echo "OK FILE  $f" >> "$OUT"
  else
    echo "MISS FILE $f" >> "$OUT"
  fi
done
echo "" >> "$OUT"

echo "[4] 网站目录文件清单（首页相关）" >> "$OUT"
ls -1 "$WEB" | grep -E '^(index|app|sales-home-v52|saas-dashboard-v50|trend-board|login-v31).*' >> "$OUT" 2>/dev/null || true
echo "" >> "$OUT"

echo "[5] docs 文件清单（关键 JSON）" >> "$OUT"
ls -1 "$WEB/docs" | grep -E '(main_index_v53|sales_home_v52|site_home_v51|saas_dashboard_v50|ai_trend_score_v50|push_control_v41|push_scheduler_v42)' >> "$OUT" 2>/dev/null || true
echo "" >> "$OUT"

echo "[6] index.html 引用情况" >> "$OUT"
if [ -f "$WEB/index.html" ]; then
  echo "--- /var/www/trendforge/index.html 中 script 引用 ---" >> "$OUT"
  grep -n "<script" "$WEB/index.html" >> "$OUT" || true
  echo "" >> "$OUT"
fi

echo "[7] main_index_v53.json 内容预览" >> "$OUT"
if [ -f "$DOCS/main_index_v53.json" ]; then
  python3 - << 'PY' >> "$OUT"
import json
p="/root/trendforge-mvp/server/docs/main_index_v53.json"
with open(p,"r",encoding="utf-8") as f:
    d=json.load(f)
print("hero=", d.get("hero", {}))
print("pricing_count=", len(d.get("pricing", [])))
print("top_items_count=", len(d.get("top_items", [])))
print("runtime=", d.get("runtime", {}))
PY
else
  echo "MISS main_index_v53.json" >> "$OUT"
fi
echo "" >> "$OUT"

echo "[8] index.js 是否存在并可被首页引用" >> "$OUT"
if [ -f "$WEB/index.js" ]; then
  echo "OK FILE  $WEB/index.js" >> "$OUT"
  head -n 5 "$WEB/index.js" >> "$OUT"
else
  echo "MISS FILE $WEB/index.js" >> "$OUT"
fi
echo "" >> "$OUT"

echo "[9] 建议" >> "$OUT"
echo "1. 如果 /root/trendforge-mvp/server/docs/main_index_v53.json 缺失，说明 V53 产物没有真正生成或被覆盖。" >> "$OUT"
echo "2. 如果 /var/www/trendforge/index.html 仍然引用旧接口，而不是 index.js / main_index_v53.json，首页就会继续显示旧版。" >> "$OUT"
echo "3. 如果 /var/www/trendforge/docs/main_index_v53.json 缺失，需要重新复制。" >> "$OUT"
echo "" >> "$OUT"

echo "审计完成：$OUT"
cat "$OUT"
