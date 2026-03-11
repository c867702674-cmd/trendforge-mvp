#!/bin/bash

echo "Installing TrendForge V101..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v101.sql << 'EOF'
CREATE TABLE IF NOT EXISTS listing_pack_v101 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
creative_id INTEGER,
source_term TEXT,
product_type TEXT,
listing_title TEXT,
listing_bullets TEXT,
listing_tags TEXT,
listing_description TEXT,
sku TEXT,
listing_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/listing_pack_v101.py << 'EOF'
import sqlite3
import re

DB='/root/trendforge-mvp/server/trendforge.db'

def slug(s):
    return re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')

def build_title(term, product_type):
    if product_type == "shirt":
        return f"{term.title()}, Minimalist POD Graphic Tee"
    if product_type == "mug":
        return f"{term.title()}, Giftable POD Coffee Cup"
    if product_type == "poster":
        return f"{term.title()}, Printable Wall Art Decor"
    return f"{term.title()}, POD Listing"

def build_bullets(term, product_type):
    bullets = [
        f"Theme: {term.title()}",
        f"Product: {product_type.title()}",
        "Style: commercial POD ready",
        "Audience: general ecommerce buyer",
        "Use as listing draft, then manually review trademark and platform policy"
    ]
    return " | ".join(bullets)

def build_tags(term, product_type):
    parts = [p.strip() for p in term.split() if p.strip()]
    extra = [product_type, "pod", "gift idea", "trending design"]
    tags = parts + extra
    return ", ".join(tags[:13])

def build_description(term, product_type):
    return (
        f"This {product_type} listing pack is built around the theme '{term.title()}'. "
        f"It is positioned as a commercial POD concept for sellers. "
        f"Use this as a marketplace-ready foundation, then manually refine sizing, "
        f"materials, production details, and compliance checks before publishing."
    )

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM creative_pack_v100"
    ).fetchall()

    inserted = 0

    for i, r in enumerate(rows, start=1):
        term = r["source_term"]
        product_type = r["product_type"]

        listing_title = build_title(term, product_type)
        listing_bullets = build_bullets(term, product_type)
        listing_tags = build_tags(term, product_type)
        listing_description = build_description(term, product_type)
        sku = f"TF-V101-{product_type.upper()}-{slug(term)[:28]}-{i:04d}"
        listing_note = "Ready for listing draft use; operator should do final compliance review"

        conn.execute(
            """
            INSERT INTO listing_pack_v101
            (creative_id, source_term, product_type, listing_title, listing_bullets, listing_tags, listing_description, sku, listing_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                listing_title,
                listing_bullets,
                listing_tags,
                listing_description,
                sku,
                listing_note,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] listing_pack_v101 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/listing_pack_v101_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/listing_pack_v101.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM listing_pack_v101 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] listing_pack_v101_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/listing-pack-v101.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V101 Listing Pack Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V101 Listing Pack Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">把 Creative Pack 收口为可直接上架使用的 Listing Pack。</p>
  <div id="app"></div>
  <script src="listing-pack-v101.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/listing-pack-v101.js << 'EOF'
fetch('/docs/listing_pack_v101.json')
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
          <div style="color:#9fb3d9;margin-bottom:6px;">LISTING TITLE</div>
          <div>${x.listing_title}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">BULLETS</div>
          <div>${x.listing_bullets}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">TAGS</div>
          <div>${x.listing_tags}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">DESCRIPTION</div>
          <div>${x.listing_description}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">SKU</div>
          <div>${x.sku}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">LISTING NOTE</div>
          <div>${x.listing_note}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V101 files installed successfully."
