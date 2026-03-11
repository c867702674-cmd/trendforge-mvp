#!/bin/bash

echo "Installing TrendForge V102..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v102.sql << 'EOF'
CREATE TABLE IF NOT EXISTS publish_pack_v102 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
listing_id INTEGER,
source_term TEXT,
product_type TEXT,
publish_title TEXT,
publish_subtitle TEXT,
publish_checklist TEXT,
marketplace_note TEXT,
final_publish_pack TEXT,
operator_action TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/publish_pack_v102.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

SUBTITLE_MAP = {
    "shirt": "Commercial POD shirt draft ready for operator review and publish flow",
    "mug": "Giftable mug draft ready for operator review and publish flow",
    "poster": "Printable wall-art draft ready for operator review and publish flow"
}

CHECKLIST_MAP = {
    "shirt": "1. Review title 2. Review tags 3. Check artwork placement 4. Confirm mockup quality 5. Confirm platform policy 6. Publish",
    "mug": "1. Review title 2. Review tags 3. Check mug print zone 4. Confirm mockup quality 5. Confirm platform policy 6. Publish",
    "poster": "1. Review title 2. Review tags 3. Check framed composition 4. Confirm mockup quality 5. Confirm platform policy 6. Publish"
}

MARKETPLACE_NOTE_MAP = {
    "shirt": "Best suited for Etsy / Shopify POD apparel workflow",
    "mug": "Best suited for Etsy / Shopify giftable mug workflow",
    "poster": "Best suited for Etsy / Shopify printable wall decor workflow"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, listing_title, sku FROM listing_pack_v101"
    ).fetchall()

    inserted = 0

    for r in rows:
        term = r["source_term"]
        product_type = r["product_type"]

        publish_title = r["listing_title"]
        publish_subtitle = SUBTITLE_MAP.get(product_type, "Publish-ready draft")
        publish_checklist = CHECKLIST_MAP.get(product_type, "Review and publish")
        marketplace_note = MARKETPLACE_NOTE_MAP.get(product_type, "General POD marketplace workflow")
        final_publish_pack = f"{publish_title} | SKU={r['sku']} | Ready for final operator publish flow"
        operator_action = "Operator should complete final QA and push listing live"

        conn.execute(
            """
            INSERT INTO publish_pack_v102
            (listing_id, source_term, product_type, publish_title, publish_subtitle, publish_checklist, marketplace_note, final_publish_pack, operator_action, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                publish_title,
                publish_subtitle,
                publish_checklist,
                marketplace_note,
                final_publish_pack,
                operator_action,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] publish_pack_v102 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/publish_pack_v102_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/publish_pack_v102.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM publish_pack_v102 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] publish_pack_v102_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/publish-pack-v102.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V102 Publish Pack Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V102 Publish Pack Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">把 Listing Pack 收口为最终可发布 Publish Pack。</p>
  <div id="app"></div>
  <script src="publish-pack-v102.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/publish-pack-v102.js << 'EOF'
fetch('/docs/publish_pack_v102.json')
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
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PUBLISH TITLE</div>
          <div>${x.publish_title}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PUBLISH SUBTITLE</div>
          <div>${x.publish_subtitle}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PUBLISH CHECKLIST</div>
          <div>${x.publish_checklist}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">MARKETPLACE NOTE</div>
          <div>${x.marketplace_note}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">FINAL PUBLISH PACK</div>
          <div>${x.final_publish_pack}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">OPERATOR ACTION</div>
          <div>${x.operator_action}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V102 files installed successfully."
