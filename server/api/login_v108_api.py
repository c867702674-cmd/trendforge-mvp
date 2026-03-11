import sqlite3, json, hashlib, sys

DB='/root/trendforge-mvp/server/trendforge.db'

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login(email, pw):
    conn=sqlite3.connect(DB)
    cur=conn.cursor()

    pw_hash=hash_pw(pw)

    r=cur.execute(
        "SELECT id,email,plan FROM users_v108 WHERE email=? AND password=?",
        (email,pw_hash)
    ).fetchone()

    conn.close()

    if r:
        print(json.dumps({"status":"ok","user":r[1],"plan":r[2]}))
    else:
        print(json.dumps({"status":"fail"}))

if __name__=="__main__":
    login(sys.argv[1],sys.argv[2])
