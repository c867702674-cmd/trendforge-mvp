#!/bin/bash

echo "Installing TrendForge V99..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v99.sql << 'EOF'
CREATE TABLE IF NOT EXISTS image_brief_v99 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
mockup_id INTEGER,
source_term TEXT,
product_type TEXT,
hero_brief TEXT,
color_brief TEXT,
composition_brief TEXT,
copy_brief TEXT,
production_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/image_brief_v99.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

COLOR_MAP = {
    "shirt": "Use high-contrast POD-friendly colors, readable from thumbnail view",
    "mug": "Use giftable warm palette with clean contrast and simple focal point",
    "poster": "Use tasteful decor palette, neutral base with elegant accent colors"
}

COMP_MAP = {
    "shirt": "Centered composition, clear focal hierarchy, print-safe margins",
    "mug": "Front-facing readable layout, balanced print area, simple hero focus",
    "poster": "Wall-art layout, breathing space, premium framed-poster composition"
}

COPY_MAP = {
    "shirt": "Keep visual message bold, fast to understand, POD-commercial style",
    "mug": "Emphasize giftability, daily use mood, clean consumer appeal",
    "poster": "Emphasize decor value, aesthetic mood, printable wall-art positioning"
}

PROD_MAP = {
    "shirt": "Deliver 1 hero design + 1 clean mockup + 1 detail shot suggestion",
    "mug": "Deliver 1 hero design + 1 desk scene + 1 isolated ecommerce mockup",
    "poster": "Deliver 1 framed wall mockup + 1 white-bg product view + 1 detail crop"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM mockup_pack_v98"
    ).fetchall()

    inserted = 0

    for r in rows:
        product_type = r["product_type"]

        conn.execute(
            """
            INSERT INTO image_brief_v99
            (mockup_id, source_term, product_type, hero_brief, color_brief, composition_brief, copy_brief, production_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                product_type,
                f"Create a commercial hero image for {r['source_term']} optimized for {product_type}",
                COLOR_MAP.get(product_type, "Use clean commercial colors"),
                COMP_MAP.get(product_type, "Use clean ecommerce composition"),
                COPY_MAP.get(product_type, "Keep message clear and commercial"),
                PROD_MAP.get(product_type, "Deliver hero + mockup pack"),
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] image_brief_v99 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/image_brief_v99_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/image_brief_v99.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM image_brief_v99 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] image_brief_v99_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/image-brief-v99.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V99 Image Brief Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V99 Image Brief Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">基于 V98 Mockup Pack 自动生成出图执行 Brief：Hero / Color / Composition / Copy / Production。</p>
  <div id="app"></div>
  <script src="image-brief-v99.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/image-brief-v99.js << 'EOF'
fetch('/docs/image_brief_v99.json')
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
          <div style="color:#9fb3d9;margin-bottom:6px;">HERO BRIEF</div>
          <div>${x.hero_brief}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">COLOR BRIEF</div>
          <div>${x.color_brief}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">COMPOSITION BRIEF</div>
          <div>${x.composition_brief}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">COPY BRIEF</div>
          <div>${x.copy_brief}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PRODUCTION NOTE</div>
          <div>${x.production_note}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V99 files installed successfully."
