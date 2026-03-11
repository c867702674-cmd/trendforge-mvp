#!/bin/bash

echo "Installing TrendForge V103..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v103.sql << 'EOF'
CREATE TABLE IF NOT EXISTS release_queue_v103 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
publish_id INTEGER,
source_term TEXT,
product_type TEXT,
queue_name TEXT,
priority TEXT,
risk_level TEXT,
release_note TEXT,
next_step TEXT,
operator_owner TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/release_queue_v103.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def decide_queue(product_type):
    if product_type == "poster":
        return "ASSET_REVIEW_QUEUE"
    if product_type == "mug":
        return "READY_TO_RELEASE"
    if product_type == "shirt":
        return "READY_TO_RELEASE"
    return "MANUAL_QUEUE"

def decide_priority(product_type):
    if product_type == "mug":
        return "P0"
    if product_type == "shirt":
        return "P0"
    if product_type == "poster":
        return "P1"
    return "P2"

def decide_next_step(product_type):
    if product_type == "poster":
        return "Complete final poster asset/mockup review, then move into release"
    if product_type == "mug":
        return "Operator final QA, then publish now"
    if product_type == "shirt":
        return "Operator final QA, then publish now"
    return "Manual operator review"

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, publish_title FROM publish_pack_v102"
    ).fetchall()

    inserted = 0

    for r in rows:
        queue_name = decide_queue(r["product_type"])
        priority = decide_priority(r["product_type"])
        risk_level = "SAFE"
        release_note = f"{r['publish_title']} entered {queue_name}"
        next_step = decide_next_step(r["product_type"])
        operator_owner = "operator"
        status = "READY" if queue_name == "READY_TO_RELEASE" else "WAITING"

        conn.execute(
            """
            INSERT INTO release_queue_v103
            (publish_id, source_term, product_type, queue_name, priority, risk_level, release_note, next_step, operator_owner, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                r["product_type"],
                queue_name,
                priority,
                risk_level,
                release_note,
                next_step,
                operator_owner,
                status
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] release_queue_v103 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/release_queue_v103_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/release_queue_v103.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM release_queue_v103 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] release_queue_v103_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/release-queue-v103.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V103 Release Queue Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V103 Release Queue Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">把 Publish Pack 收口为可执行发布队列：READY / ASSET_REVIEW / MANUAL。</p>
  <div id="app"></div>
  <script src="release-queue-v103.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/release-queue-v103.js << 'EOF'
fetch('/docs/release_queue_v103.json')
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
          <span style="background:#7a2e2e;padding:6px 12px;border-radius:999px;">${x.priority}</span>
          <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.product_type}</span>
          <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
          <span style="background:#69531b;padding:6px 12px;border-radius:999px;">${x.risk_level}</span>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">QUEUE NAME</div>
          <div>${x.queue_name}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">RELEASE NOTE</div>
          <div>${x.release_note}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">NEXT STEP</div>
          <div>${x.next_step}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">OPERATOR OWNER</div>
          <div>${x.operator_owner}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V103 files installed successfully."
