#!/bin/bash

echo "Installing TrendForge V104..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v104.sql << 'EOF'
CREATE TABLE IF NOT EXISTS operator_console_v104 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
queue_id INTEGER,
source_term TEXT,
product_type TEXT,
stage_name TEXT,
action_advice TEXT,
blocker_reason TEXT,
owner TEXT,
executable_action TEXT,
final_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/operator_console_v104.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def stage_from_queue(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "READY_PUSH"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "ASSET_CHECK"
    return "MANUAL_REVIEW"

def advice_from_queue(queue_name, product_type):
    if queue_name == "READY_TO_RELEASE":
        return f"{product_type} can move into final publish after operator QA"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return f"{product_type} needs final asset/mockup review before publish"
    return f"{product_type} requires manual operator review"

def blocker_from_queue(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "none"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "asset review pending"
    return "manual verification pending"

def exec_action(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "Run final QA -> confirm listing -> push live"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "Finish asset review -> approve mockup -> move to release"
    return "Manual inspection -> approve or reject"

def final_note(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "This item is near-commercial-ready."
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "This item is waiting for asset completion before commercial release."
    return "This item is held for manual review."

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, queue_name, operator_owner, status FROM release_queue_v103"
    ).fetchall()

    inserted = 0

    for r in rows:
        stage_name = stage_from_queue(r["queue_name"])
        action_advice = advice_from_queue(r["queue_name"], r["product_type"])
        blocker_reason = blocker_from_queue(r["queue_name"])
        owner = r["operator_owner"]
        executable_action = exec_action(r["queue_name"])
        note = final_note(r["queue_name"])

        conn.execute(
            """
            INSERT INTO operator_console_v104
            (queue_id, source_term, product_type, stage_name, action_advice, blocker_reason, owner, executable_action, final_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                r["product_type"],
                stage_name,
                action_advice,
                blocker_reason,
                owner,
                executable_action,
                note,
                r["status"]
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] operator_console_v104 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/operator_console_v104_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/operator_console_v104.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM operator_console_v104 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] operator_console_v104_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/operator-console-v104.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V104 Operator Console</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V104 Operator Console</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">把 Release Queue 收口为运营操作台：阶段 / 建议 / 阻塞 / 动作。</p>
  <div id="app"></div>
  <script src="operator-console-v104.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/operator-console-v104.js << 'EOF'
fetch('/docs/operator_console_v104.json')
.then(r => r.json())
.then(data => {
  let html = '';

  data.forEach(x => {
    html += `
      <div style="background:#16233d;padding:20px;margin-bottom:20px;border-radius:14px;">
        <div style="font-size:28px;font-weight:bold;margin-bottom:16px;">
          ${x.source_term}
        </div>

        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
          <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.product_type}</span>
          <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
          <span style="background:#69531b;padding:6px 12px;border-radius:999px;">${x.stage_name}</span>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">ACTION ADVICE</div>
          <div>${x.action_advice}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">BLOCKER REASON</div>
          <div>${x.blocker_reason}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">OWNER</div>
          <div>${x.owner}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">EXECUTABLE ACTION</div>
          <div>${x.executable_action}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">FINAL NOTE</div>
          <div>${x.final_note}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V104 files installed successfully."
