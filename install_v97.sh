#!/bin/bash

echo "Installing TrendForge V97..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p server/docs
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v97.sql << 'EOF'
CREATE TABLE IF NOT EXISTS mj_prompt_v97 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
trend_id INTEGER,
source_term TEXT,
product_type TEXT,
style_hint TEXT,
mj_prompt TEXT,
negative_prompt TEXT,
mockup_prompt TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# ENGINE
########################
cat > server/engines/mj_prompt_v97.py << 'EOF'
import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

STYLE_MAP = {
    "shirt": "clean typography t-shirt design, centered composition, commercial POD style, print-ready, isolated artwork",
    "mug": "clean giftable mug graphic, centered composition, commercial POD style, print-ready, isolated artwork",
    "poster": "minimal wall art poster design, elegant composition, printable decor style, isolated artwork"
}

NEGATIVE = "no watermark, no logo, no brand name, no signature, no mockup, no extra limbs, no blurry details, no messy background"

MOCKUP_MAP = {
    "shirt": "realistic t-shirt mockup, ecommerce product display, folded or front flat lay, clean lighting, white background",
    "mug": "white ceramic mug mockup on clean desk scene, ecommerce lighting, realistic product showcase",
    "poster": "minimal poster mockup in modern interior, framed wall art scene, soft natural lighting, ecommerce presentation"
}

def build_prompt(term, product_type):
    style = STYLE_MAP.get(product_type, "commercial POD design, isolated artwork")
    return f"{term}, {style}, high contrast, transparent background style, no mockup --ar 1:1 --v 6"

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type FROM trend_data_v89"
    ).fetchall()

    inserted = 0

    for r in rows:
        term = r["source_term"]
        product_type = r["product_type"]
        style_hint = STYLE_MAP.get(product_type, "commercial POD design")

        mj_prompt = build_prompt(term, product_type)
        negative_prompt = NEGATIVE
        mockup_prompt = MOCKUP_MAP.get(product_type, "ecommerce product mockup")

        conn.execute(
            """
            INSERT INTO mj_prompt_v97
            (trend_id, source_term, product_type, style_hint, mj_prompt, negative_prompt, mockup_prompt, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                term,
                product_type,
                style_hint,
                mj_prompt,
                negative_prompt,
                mockup_prompt,
                "READY"
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] mj_prompt_v97 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
EOF

########################
# API
########################
cat > server/api/mj_prompt_v97_api.py << 'EOF'
import sqlite3, json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/mj_prompt_v97.json'

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT * FROM mj_prompt_v97 ORDER BY id DESC"
    ).fetchall()

    data = [dict(r) for r in rows]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"[OK] mj_prompt_v97_api wrote={OUT} items={len(data)}")

if __name__ == '__main__':
    main()
EOF

########################
# WEB HTML
########################
cat > web/mj-prompt-v97.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TrendForge V97 MJ Prompt Engine</title>
</head>
<body style="background:#081224;color:#fff;font-family:Arial;padding:32px;">
  <h1 style="margin-bottom:10px;">TrendForge V97 MJ Prompt Engine</h1>
  <p style="color:#9fb3d9;margin-bottom:24px;">基于趋势词自动生成 Midjourney Prompt / Negative Prompt / Mockup Prompt。</p>
  <div id="app"></div>
  <script src="mj-prompt-v97.js"></script>
</body>
</html>
EOF

########################
# WEB JS
########################
cat > web/mj-prompt-v97.js << 'EOF'
fetch('/docs/mj_prompt_v97.json')
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
          <div style="color:#9fb3d9;margin-bottom:6px;">STYLE HINT</div>
          <div>${x.style_hint}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">MJ PROMPT</div>
          <div>${x.mj_prompt}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">NEGATIVE PROMPT</div>
          <div>${x.negative_prompt}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">MOCKUP PROMPT</div>
          <div>${x.mockup_prompt}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
EOF

echo "TrendForge V97 files installed successfully."
