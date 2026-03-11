#!/bin/bash

echo "Installing TrendForge V105..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v105.sql << 'EOF'
CREATE TABLE IF NOT EXISTS commercial_dashboard_v105 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
section_name TEXT,
section_value TEXT,
section_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/commercial_dashboard_v105.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def count_table(conn, table_name):
    try:
        row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
        return row[0] if row else 0
    except:
        return 0

def main():
    conn = sqlite3.connect(DB)

    sections = [
        ("Trend Data Engine", str(count_table(conn, "trend_data_v89")), "Google Trends / Etsy / Amazon 数据入口", "ACTIVE"),
        ("MJ Prompt Engine", str(count_table(conn, "mj_prompt_v97")), "Midjourney Prompt 自动生成", "ACTIVE"),
        ("Mockup Pack Engine", str(count_table(conn, "mockup_pack_v98")), "Hero / Scene / White BG / Detail 模型包", "ACTIVE"),
        ("Image Brief Engine", str(count_table(conn, "image_brief_v99")), "出图执行 Brief", "ACTIVE"),
        ("Creative Pack Engine", str(count_table(conn, "creative_pack_v100")), "商业创意收口包", "ACTIVE"),
        ("Listing Pack Engine", str(count_table(conn, "listing_pack_v101")), "可上架 Listing 包", "ACTIVE"),
        ("Publish Pack Engine", str(count_table(conn, "publish_pack_v102")), "最终发布包", "ACTIVE"),
        ("Release Queue Engine", str(count_table(conn, "release_queue_v103")), "发布队列管理", "ACTIVE"),
        ("Operator Console", str(count_table(conn, "operator_console_v104")), "运营执行台", "ACTIVE"),
        ("Billing System", str(count_table(conn, "billing_system_v90")), "商业付费系统", "ACTIVE"),
        ("User System", str(count_table(conn, "user_system_v88")), "SaaS 用户体系", "ACTIVE"),
        ("Automation Hub", str(count_table(conn, "automation_hub_v92")), "自动化规则中心", "ACTIVE"),
    ]

    conn.execute("DELETE FROM commercial_dashboard_v105")

    for s in sections:
        conn.execute(
            """
            INSERT INTO commercial_dashboard_v105
            (section_name, section_value, section_note, status)
            VALUES (?, ?, ?, ?)
            """,
            s
        )

    conn.commit()
    conn.close()
    print(f"[OK] commercial_dashboard_v105 inserted={len(sections)} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/commercial_dashboard_v105_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/commercial_dashboard_v105.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM commercial_dashboard_v105 ORDER BY id ASC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] commercial_dashboard_v105_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/commercial-dashboard-v105.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V105 Commercial Dashboard</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V105 Commercial Dashboard</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">商业版统一总览入口：趋势 / Prompt / Mockup / Listing / Publish / Queue / Operator / Billing / User。</p>
  <div id="app"></div>
  <script src="commercial-dashboard-v105.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/commercial-dashboard-v105.js << 'EOF'
fetch('/docs/commercial_dashboard_v105.json')
.then(r => r.json())
.then(data => {
  let html = '';

  data.forEach(x => {
    html += `
      <div style="background:#16233d;padding:20px;margin-bottom:20px;border-radius:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
          <div style="font-size:28px;font-weight:bold;">${x.section_name}</div>
          <div style="display:flex;gap:10px;align-items:center;">
            <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.section_value}</span>
            <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
          </div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-top:14px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">SECTION NOTE</div>
          <div>${x.section_note}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V105 files installed successfully."
