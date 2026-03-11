#!/bin/bash

echo "Installing TrendForge V96..."

mkdir -p server/sql
mkdir -p server/engines
mkdir -p server/api
mkdir -p web

########################
# SQL
########################

cat > server/sql/migrate_v96.sql << 'EOF'
CREATE TABLE IF NOT EXISTS listing_drafts_v96 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
trend_id INTEGER,
source_term TEXT,
product_type TEXT,
title TEXT,
tags TEXT,
description TEXT,
sku TEXT,
status TEXT
);
EOF

########################
# ENGINE
########################

cat > server/engines/listing_draft_v96.py << 'EOF'
import sqlite3,re

DB='/root/trendforge-mvp/server/trendforge.db'

def slug(s):
    return re.sub('[^a-zA-Z0-9]+','-',s.lower())

def main():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row

    rows=conn.execute(
        'select id,source_term,product_type from trend_data_v89'
    ).fetchall()

    for i,r in enumerate(rows):

        conn.execute(
        'insert into listing_drafts_v96(trend_id,source_term,product_type,title,tags,description,sku,status) values(?,?,?,?,?,?,?,?)',
        (
        r["id"],
        r["source_term"],
        r["product_type"],
        r["source_term"].title(),
        "pod,trend,design",
        "Auto generated listing",
        f"TF96-{i}",
        "READY"
        ))

    conn.commit()
    conn.close()

    print("V96 drafts generated")

if __name__=='__main__':
    main()
EOF

########################
# API
########################

cat > server/api/listing_draft_v96_api.py << 'EOF'
import sqlite3,json

DB='/root/trendforge-mvp/server/trendforge.db'
OUT='/root/trendforge-mvp/server/docs/listing_draft_v96.json'

conn=sqlite3.connect(DB)
conn.row_factory=sqlite3.Row

rows=conn.execute(
'select * from listing_drafts_v96'
).fetchall()

data=[dict(r) for r in rows]

with open(OUT,'w') as f:
    json.dump(data,f,indent=2)

print("listing_draft_v96.json generated")
EOF

########################
# WEB HTML
########################

cat > web/listing-draft-v96.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge V96 Listing Draft Engine</title>
</head>

<body style="background:#0b1220;color:white;font-family:Arial;padding:40px">

<h1>TrendForge V96 Listing Draft Engine</h1>

<div id="app"></div>

<script src="listing-draft-v96.js"></script>

</body>
</html>
EOF

########################
# WEB JS
########################

cat > web/listing-draft-v96.js << 'EOF'
fetch('/docs/listing_draft_v96.json')
.then(r=>r.json())
.then(data=>{

let html=""

data.forEach(x=>{

html+=`
<div style="background:#1b2a44;padding:20px;margin-bottom:20px;border-radius:10px">
<b>${x.title}</b><br>
Product: ${x.product_type}<br>
SKU: ${x.sku}<br>
Tags: ${x.tags}<br>
<p>${x.description}</p>
</div>
`

})

document.getElementById("app").innerHTML=html

})
EOF

echo "TrendForge V96 files installed successfully."
