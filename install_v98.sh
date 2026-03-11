#!/bin/bash

echo "Installing TrendForge V98..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v98.sql << 'EOF'
CREATE TABLE IF NOT EXISTS mockup_pack_v98 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
prompt_id INTEGER,
source_term TEXT,
product_type TEXT,
hero_mockup TEXT,
scene_mockup TEXT,
white_bg_mockup TEXT,
detail_mockup TEXT,
mockup_pack_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/mockup_pack_v98.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

HERO_MAP = {
    "shirt": "Front flat lay hero image, centered design, white background, ecommerce-ready",
    "mug": "White ceramic mug hero image, 45-degree angle, clean desk lighting, ecommerce-ready",
    "poster": "Framed poster hero image, straight-on wall shot, modern minimal interior"
}

SCENE_MAP = {
    "shirt": "Lifestyle shirt scene, casual indoor setting, soft natural light",
    "mug": "Giftable mug scene on desk, coffee setup, warm lifestyle atmosphere",
    "poster": "Modern interior wall decor scene, styled room, soft daylight"
}

WHITE_BG_MAP = {
    "shirt": "Pure white background product shot, front-only, no props",
    "mug": "Pure white background mug shot, isolated product, no props",
    "poster": "Pure white background framed poster shot, isolated product"
}

DETAIL_MAP = {
    "shirt": "Fabric close-up, print detail close-up, collar / texture detail",
    "mug": "Handle close-up, print detail close-up, ceramic texture detail",
    "poster": "Frame corner close-up, paper texture detail, print detail close-up"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM mj_prompt_v97"
    ).fetchall()

    inserted = 0

    for r in rows:
        product_type = r["product_type"]

        conn.execute(
            """
            INSERT INTO mockup_pack_v98
            (prompt_id, source_term, product_type, hero_mockup, scene_mockup, white_bg_mockup, detail_mockup, mockup_pack_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                product_type,
                HERO_MAP.get(product_type, "Hero mockup"),
                SCENE_MAP.get(product_type, "Scene mockup"),
                WHITE_BG_MAP.get(product_type, "White background mockup"),
                DETAIL_MAP.get(product_type, "Detail mockup"),
                "Use 4-image pack: hero / scene / white-bg / detail",
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] mockup_pack_v98 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/mockup_pack_v98_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/mockup_pack_v98.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM mockup_pack_v98 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] mockup_pack_v98_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/mockup-pack-v98.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V98 Mockup Pack Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V98 Mockup Pack Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">基于 V97 Prompt 自动生成商品展示图方案：Hero / Scene / White BG / Detail。</p>
  <div id="app"></div>
  <script src="mockup-pack-v98.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/mockup-pack-v98.js << 'EOF'
fetch('/docs/mockup_pack_v98.json')
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
          <div style="color:#9fb3d9;margin-bottom:6px;">HERO MOCKUP</div>
          <div>${x.hero_mockup}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">SCENE MOCKUP</div>
          <div>${x.scene_mockup}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">WHITE BG MOCKUP</div>
          <div>${x.white_bg_mockup}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">DETAIL MOCKUP</div>
          <div>${x.detail_mockup}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PACK NOTE</div>
          <div>${x.mockup_pack_note}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V98 files installed successfully."
