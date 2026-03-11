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
