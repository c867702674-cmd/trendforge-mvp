import sqlite3, json, hashlib, sys

DB='/root/trendforge-mvp/server/trendforge.db'

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def register(email, pw):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users_v108 (email, password, plan) VALUES (?, ?, ?)",
            (email, hash_pw(pw), "free")
        )
        conn.commit()
        print(json.dumps({"status": "ok", "email": email, "plan": "free"}))
    except Exception as e:
        print(json.dumps({"status": "fail", "error": str(e)}))
    finally:
        conn.close()

if __name__ == "__main__":
    register(sys.argv[1], sys.argv[2])
