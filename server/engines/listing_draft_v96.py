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
