import sqlite3, json, sys

DB='/root/trendforge-mvp/server/trendforge.db'

def me(token):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT u.email, u.plan
        FROM sessions_v109 s
        JOIN users_v108 u ON s.email = u.email
        WHERE s.token = ?
        ORDER BY s.id DESC
        LIMIT 1
        """,
        (token,)
    ).fetchone()

    conn.close()

    if row:
        print(json.dumps({"status": "ok", "email": row[0], "plan": row[1]}))
    else:
        print(json.dumps({"status": "fail"}))

if __name__ == "__main__":
    me(sys.argv[1])
