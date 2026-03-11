#!/bin/bash

echo "Installing TrendForge V107..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v107.sql << 'EOF'
CREATE TABLE IF NOT EXISTS homepage_v107 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
section_key TEXT,
section_title TEXT,
section_value TEXT,
section_desc TEXT,
status TEXT,
sort_order INTEGER,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/homepage_v107.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def count_table(conn, table_name):
    try:
        row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return row[0] if row else 0
    except:
        return 0

def main():
    conn = sqlite3.connect(DB)

    trend_count = count_table(conn, "trend_data_v89")
    prompt_count = count_table(conn, "mj_prompt_v97")
    mockup_count = count_table(conn, "mockup_pack_v98")
    listing_count = count_table(conn, "listing_pack_v101")
    publish_count = count_table(conn, "publish_pack_v102")
    user_count = count_table(conn, "user_system_v88")

    rows = [
        ("hero", "北美 POD 趋势商业引擎", str(trend_count), "把趋势、Prompt、Mockup、Listing、发布收口为一套真正可执行的商业闭环。", "ACTIVE", 1),
        ("metric", "趋势数据", str(trend_count), "Google Trends / Etsy / Amazon 多源趋势入口", "ACTIVE", 2),
        ("metric", "Prompt能力", str(prompt_count), "Midjourney Prompt 自动生成", "ACTIVE", 3),
        ("metric", "Mockup能力", str(mockup_count), "Hero / Scene / White BG / Detail 模型包", "ACTIVE", 4),
        ("metric", "Listing草稿", str(listing_count), "自动生成可上架 Listing 包", "ACTIVE", 5),
        ("metric", "发布包", str(publish_count), "发布前最终收口 Publish Pack", "ACTIVE", 6),
        ("feature", "DO_NOW 趋势发现", "实时发现", "为中国 POD 卖家快速发现北美市场值得立刻执行的主题词与产品方向。", "ACTIVE", 7),
        ("feature", "AI 创意执行", "自动生成", "自动产出 Prompt、Mockup 思路、出图 Brief、Creative Pack。", "ACTIVE", 8),
        ("feature", "商品上架链路", "直接收口", "从趋势到 Listing、再到 Publish Queue 与 Operator Console，形成完整执行路径。", "ACTIVE", 9),
        ("feature", "SaaS 商业化能力", str(user_count), "包含用户系统、权限、套餐、订阅与自动化推送能力。", "ACTIVE", 10),
        ("plan", "Free", "$0", "适合体验版用户：少量趋势查看。", "ACTIVE", 11),
        ("plan", "Pro", "$39/mo", "适合个人卖家：趋势 + Prompt + Mockup + Listing。", "ACTIVE", 12),
        ("plan", "VIP", "$99/mo", "适合重度卖家/团队：完整商业链路 + Command Center。", "ACTIVE", 13),
        ("cta", "立即开始", "TrendForge 商业版", "下一步建议：把本页替换为正式首页入口，并接入登录/套餐跳转。", "ACTIVE", 14),
    ]

    conn.execute("DELETE FROM homepage_v107")

    for row in rows:
        conn.execute(
            """
            INSERT INTO homepage_v107
            (section_key, section_title, section_value, section_desc, status, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            row
        )

    conn.commit()
    conn.close()
    print(f"[OK] homepage_v107 inserted={len(rows)} db={DB}")

if __name__ == "__main__":
    main()
EOF

########################
# API
########################
cat > server/api/homepage_v107_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/homepage_v107.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM homepage_v107 ORDER BY sort_order ASC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] homepage_v107_api wrote={OUT} items={len(data)}")

if __name__ == "__main__":
    main()
EOF

########################
# WEB HTML
########################
cat > web/index-v107.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TrendForge V107 正式首页版</title>
</head>
<body style="margin:0;background:#07111f;color:#fff;font-family:Arial,Helvetica,sans-serif;">
  <div id="app"></div>
  <script src="index-v107.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/index-v107.js << 'EOF'
fetch('/docs/homepage_v107.json')
  .then(r => r.json())
  .then(data => {
    const hero = data.find(x => x.section_key === 'hero');
    const metrics = data.filter(x => x.section_key === 'metric');
    const features = data.filter(x => x.section_key === 'feature');
    const plans = data.filter(x => x.section_key === 'plan');
    const cta = data.find(x => x.section_key === 'cta');

    const metricHtml = metrics.map(x => `
      <div style="background:#16233d;border-radius:18px;padding:24px;">
        <div style="font-size:16px;color:#9fb3d9;margin-bottom:12px;">${x.section_title}</div>
        <div style="font-size:42px;font-weight:bold;margin-bottom:12px;">${x.section_value}</div>
        <div style="display:inline-block;background:#215732;padding:6px 12px;border-radius:999px;margin-bottom:14px;">${x.status}</div>
        <div style="color:#d7def0;line-height:1.7;">${x.section_desc}</div>
      </div>
    `).join('');

    const featureHtml = features.map(x => `
      <div style="background:#16233d;border-radius:18px;padding:24px;">
        <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px;">
          <div style="font-size:26px;font-weight:bold;">${x.section_title}</div>
          <div style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.section_value}</div>
        </div>
        <div style="color:#d7def0;line-height:1.8;">${x.section_desc}</div>
      </div>
    `).join('');

    const planHtml = plans.map(x => `
      <div style="background:#16233d;border-radius:18px;padding:24px;flex:1;min-width:240px;">
        <div style="font-size:28px;font-weight:bold;margin-bottom:8px;">${x.section_title}</div>
        <div style="font-size:36px;font-weight:bold;margin-bottom:12px;color:#fff;">${x.section_value}</div>
        <div style="color:#d7def0;line-height:1.8;">${x.section_desc}</div>
      </div>
    `).join('');

    document.getElementById('app').innerHTML = `
      <div style="max-width:1320px;margin:0 auto;padding:34px 24px 60px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;margin-bottom:28px;">
          <div style="font-size:34px;font-weight:bold;">TrendForge</div>
          <div style="color:#9fb3d9;font-size:16px;">北美 POD 趋势商业版</div>
        </div>

        <div style="background:linear-gradient(135deg,#142441,#1b3158);border-radius:24px;padding:34px;margin-bottom:28px;">
          <div style="font-size:18px;color:#9fb3d9;margin-bottom:10px;">正式首页整合版</div>
          <div style="font-size:56px;font-weight:bold;line-height:1.15;margin-bottom:18px;">${hero.section_title}</div>
          <div style="font-size:22px;color:#fff;margin-bottom:12px;">当前趋势引擎数据量：${hero.section_value}</div>
          <div style="max-width:920px;color:#d7def0;line-height:1.9;font-size:18px;margin-bottom:24px;">${hero.section_desc}</div>
          <div style="display:flex;gap:14px;flex-wrap:wrap;">
            <div style="background:#215732;padding:12px 18px;border-radius:999px;font-weight:bold;">${hero.status}</div>
            <div style="background:#2a3b5f;padding:12px 18px;border-radius:999px;">趋势 → Prompt → Mockup → Listing → 发布</div>
          </div>
        </div>

        <div style="font-size:36px;font-weight:bold;margin:20px 0 18px;">核心指标</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-bottom:34px;">
          ${metricHtml}
        </div>

        <div style="font-size:36px;font-weight:bold;margin:20px 0 18px;">核心能力</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-bottom:34px;">
          ${featureHtml}
        </div>

        <div style="font-size:36px;font-weight:bold;margin:20px 0 18px;">套餐建议</div>
        <div style="display:flex;gap:18px;flex-wrap:wrap;margin-bottom:34px;">
          ${planHtml}
        </div>

        <div style="background:#16233d;border-radius:24px;padding:30px;">
          <div style="font-size:34px;font-weight:bold;margin-bottom:14px;">${cta.section_title}</div>
          <div style="font-size:22px;margin-bottom:12px;">${cta.section_value}</div>
          <div style="color:#d7def0;line-height:1.8;margin-bottom:20px;">${cta.section_desc}</div>
          <div style="display:flex;gap:14px;flex-wrap:wrap;">
            <a href="/home-portal-v106.html" style="text-decoration:none;background:#215732;color:#fff;padding:12px 18px;border-radius:999px;font-weight:bold;">进入统一门户</a>
            <a href="/commercial-dashboard-v105.html" style="text-decoration:none;background:#2a3b5f;color:#fff;padding:12px 18px;border-radius:999px;font-weight:bold;">查看商业总览</a>
          </div>
        </div>
      </div>
    `;
  });
EOF

echo "TrendForge V107 files installed successfully."
