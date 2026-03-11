#!/bin/bash

echo "Installing TrendForge V106..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v106.sql << 'EOF'
CREATE TABLE IF NOT EXISTS home_portal_v106 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
block_name TEXT,
block_title TEXT,
block_value TEXT,
block_note TEXT,
status TEXT,
sort_order INTEGER,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/home_portal_v106.py << 'EOF'
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

    blocks = [
        ("overview", "趋势数据", str(count_table(conn, "trend_data_v89")), "Google Trends / Etsy / Amazon 趋势入口", "ACTIVE", 1),
        ("overview", "Prompt能力", str(count_table(conn, "mj_prompt_v97")), "Midjourney Prompt 自动生成", "ACTIVE", 2),
        ("overview", "Mockup能力", str(count_table(conn, "mockup_pack_v98")), "Hero / Scene / White BG / Detail 模型包", "ACTIVE", 3),
        ("overview", "创意执行", str(count_table(conn, "creative_pack_v100")), "Creative Pack 商业执行包", "ACTIVE", 4),
        ("listing", "Listing草稿", str(count_table(conn, "listing_pack_v101")), "可直接上架使用的 Listing Pack", "ACTIVE", 5),
        ("listing", "发布准备", str(count_table(conn, "publish_pack_v102")), "Publish Pack 最终发布包", "ACTIVE", 6),
        ("ops", "发布队列", str(count_table(conn, "release_queue_v103")), "Release Queue 发布队列", "ACTIVE", 7),
        ("ops", "运营操作台", str(count_table(conn, "operator_console_v104")), "Operator Console 运营执行台", "ACTIVE", 8),
        ("saas", "用户系统", str(count_table(conn, "user_system_v88")), "Free / Pro / VIP 用户体系", "ACTIVE", 9),
        ("saas", "计费系统", str(count_table(conn, "billing_system_v90")), "订阅 / 套餐 / 支付通道", "ACTIVE", 10),
        ("automation", "自动化中心", str(count_table(conn, "automation_hub_v92")), "规则驱动自动化", "ACTIVE", 11),
        ("automation", "推送中心", str(count_table(conn, "push_center_v91")), "Feishu / Email 自动推送", "ACTIVE", 12),
    ]

    conn.execute("DELETE FROM home_portal_v106")

    for row in blocks:
        conn.execute(
            """
            INSERT INTO home_portal_v106
            (block_name, block_title, block_value, block_note, status, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            row
        )

    conn.commit()
    conn.close()
    print(f"[OK] home_portal_v106 inserted={len(blocks)} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/home_portal_v106_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/home_portal_v106.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM home_portal_v106 ORDER BY sort_order ASC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] home_portal_v106_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/home-portal-v106.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V106 Unified Home Portal</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V106 Unified Home Portal</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">商业版正式首页整合入口：趋势 / Prompt / Mockup / Listing / 发布 / 运营 / 用户 / 计费 / 自动化。</p>

  <div id="summary" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-bottom:28px;"></div>
  <div id="sections"></div>

  <script src="home-portal-v106.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/home-portal-v106.js << 'EOF'
fetch('/docs/home_portal_v106.json')
.then(r => r.json())
.then(data => {
  const summary = document.getElementById('summary');
  const sections = document.getElementById('sections');

  const summaryBlocks = data.slice(0, 4);
  let summaryHtml = '';
  summaryBlocks.forEach(x => {
    summaryHtml += `
      <div style="background:#16233d;padding:18px;border-radius:14px;">
        <div style="font-size:15px;color:#9fb3d9;margin-bottom:8px;">${x.block_title}</div>
        <div style="font-size:34px;font-weight:bold;">${x.block_value}</div>
        <div style="margin-top:10px;display:inline-block;background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</div>
      </div>
    `;
  });
  summary.innerHTML = summaryHtml;

  const groupNames = {
    listing: "Listing & Publish",
    ops: "Operations",
    saas: "SaaS System",
    automation: "Automation"
  };

  ["listing", "ops", "saas", "automation"].forEach(group => {
    const rows = data.filter(x => x.block_name === group);
    let groupHtml = `
      <div style="margin-bottom:26px;">
        <div style="font-size:28px;font-weight:bold;margin-bottom:14px;">${groupNames[group]}</div>
    `;

    rows.forEach(x => {
      groupHtml += `
        <div style="background:#16233d;padding:18px;border-radius:14px;margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;">
            <div style="font-size:24px;font-weight:bold;">${x.block_title}</div>
            <div style="display:flex;gap:10px;align-items:center;">
              <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.block_value}</span>
              <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
            </div>
          </div>
          <div style="background:#0d1730;padding:14px;border-radius:10px;margin-top:14px;">
            <div style="color:#9fb3d9;margin-bottom:6px;">BLOCK NOTE</div>
            <div>${x.block_note}</div>
          </div>
        </div>
      `;
    });

    groupHtml += `</div>`;
    sections.innerHTML += groupHtml;
  });
});
EOF

echo "TrendForge V106 files installed successfully."
