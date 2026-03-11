#!/bin/bash

echo "Installing TrendForge V100..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v100.sql << 'EOF'
CREATE TABLE IF NOT EXISTS creative_pack_v100 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
brief_id INTEGER,
source_term TEXT,
product_type TEXT,
title_idea TEXT,
tagline TEXT,
visual_direction TEXT,
prompt_pack TEXT,
mockup_pack TEXT,
production_checklist TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/creative_pack_v100.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

TAGLINE_MAP = {
    "shirt": "Fast-read POD graphic direction for commercial click-through",
    "mug": "Giftable consumer-friendly creative direction for ecommerce conversion",
    "poster": "Decor-oriented visual concept for printable wall-art positioning"
}

VISUAL_MAP = {
    "shirt": "Focus on a bold centered hero graphic, thumbnail readability, POD-ready composition",
    "mug": "Focus on clear print zone, warm gifting mood, simple commercial composition",
    "poster": "Focus on premium wall-art layout, tasteful spacing, interior-friendly design language"
}

CHECKLIST_MAP = {
    "shirt": "1. Generate artwork 2. Review thumbnail readability 3. Prepare hero mockup 4. Prepare detail crop 5. Final listing upload",
    "mug": "1. Generate artwork 2. Review handle-safe print layout 3. Prepare hero mug mockup 4. Prepare desk scene 5. Final listing upload",
    "poster": "1. Generate artwork 2. Review frame-safe composition 3. Prepare wall mockup 4. Prepare white background product shot 5. Final listing upload"
}

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, hero_brief, production_note FROM image_brief_v99"
    ).fetchall()

    inserted = 0

    for r in rows:
        term = r["source_term"]
        product_type = r["product_type"]

        title_idea = f"{term} | {product_type} creative pack"
        tagline = TAGLINE_MAP.get(product_type, "Commercial creative execution pack")
        visual_direction = VISUAL_MAP.get(product_type, "Clean ecommerce design direction")
        prompt_pack = f"Use MJ prompt + negative prompt + mockup prompt for {term}"
        mockup_pack = f"Hero / Scene / White BG / Detail pack for {product_type}"
        production_checklist = CHECKLIST_MAP.get(product_type, "Artwork → Mockup → Upload")

        conn.execute(
            """
            INSERT INTO creative_pack_v100
            (brief_id, source_term, product_type, title_idea, tagline, visual_direction, prompt_pack, mockup_pack, production_checklist, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                title_idea,
                tagline,
                visual_direction,
                prompt_pack,
                mockup_pack,
                production_checklist,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] creative_pack_v100 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/creative_pack_v100_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/creative_pack_v100.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM creative_pack_v100 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] creative_pack_v100_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/creative-pack-v100.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V100 Creative Pack Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V100 Creative Pack Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">把 Trend / Prompt / Mockup / Brief 收口为商业可执行 Creative Pack。</p>
  <div id="app"></div>
  <script src="creative-pack-v100.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/creative-pack-v100.js << 'EOF'
fetch('/docs/creative_pack_v100.json')
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
          <div style="color:#9fb3d9;margin-bottom:6px;">TITLE IDEA</div>
          <div>${x.title_idea}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">TAGLINE</div>
          <div>${x.tagline}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">VISUAL DIRECTION</div>
          <div>${x.visual_direction}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PROMPT PACK</div>
          <div>${x.prompt_pack}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">MOCKUP PACK</div>
          <div>${x.mockup_pack}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PRODUCTION CHECKLIST</div>
          <div>${x.production_checklist}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V100 files installed successfully."
