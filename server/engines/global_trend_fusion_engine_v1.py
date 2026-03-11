
#!/usr/bin/env python3
import sqlite3, json, datetime

DB="/root/trendforge-mvp/server/trendforge.db"

def now():
    return datetime.datetime.utcnow().isoformat()

def run():
    conn=sqlite3.connect(DB)
    cur=conn.cursor()

    sample=[
        ("google_trends","ai mug design",120),
        ("youtube","print on demand tutorial",90),
        ("news","winter sports merch",70),
        ("x","minimalist cat art",60)
    ]

    for s in sample:
        cur.execute(
            "INSERT INTO global_trend_signals(date,source,term,score,meta_json,created_at) VALUES(?,?,?,?,?,?)",
            (datetime.date.today().isoformat(),s[0],s[1],s[2],json.dumps({}),now())
        )

    conn.commit()
    conn.close()
    print("[OK] global_trend_fusion_engine_v1 inserted=",len(sample))

if __name__=="__main__":
    run()
