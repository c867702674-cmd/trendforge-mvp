import sqlite3, json, hashlib, sys, uuid

DB='/root/trendforge-mvp/server/trendforge.db'

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login(email, pw):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    pw_hash = hash_pw(pw)
    row = cur.execute(
        "SELECT email, plan FROM users_v108 WHERE email=? AND password=?",
        (email, pw_hash)
    ).fetchone()

    if not row:
        conn.close()
        print(json.dumps({"status": "fail"}))
        return

    token = "TFSESS-" + uuid.uuid4().hex[:24].upper()

    cur.execute(
        "INSERT INTO sessions_v109 (email, token) VALUES (?, ?)",
        (email, token)
    )
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "ok",
        "email": row[0],
        "plan": row[1],
        "token": token
    }))

if __name__ == "__main__":
    login(sys.argv[1], sys.argv[2])
