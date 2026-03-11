#!/bin/bash

echo "Installing TrendForge V109..."

mkdir -p server/sql
mkdir -p server/api
mkdir -p web

########################
# SQL
########################
cat > server/sql/migrate_v109.sql << 'EOF'
CREATE TABLE IF NOT EXISTS sessions_v109 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT,
token TEXT UNIQUE,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

########################
# REGISTER API
########################
cat > server/api/register_v109.py << 'EOF'
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
EOF

########################
# LOGIN API
########################
cat > server/api/login_v109.py << 'EOF'
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
EOF

########################
# ME API
########################
cat > server/api/me_v109.py << 'EOF'
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
EOF

########################
# LOGIN PAGE
########################
cat > web/login-v108.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge 登录</title>
</head>
<body style="background:#081224;color:white;font-family:Arial;padding:40px;">
<h1>TrendForge 登录</h1>

<input id="email" placeholder="电子邮件" style="padding:10px;margin:6px;width:260px;"><br>
<input id="pw" placeholder="密码" type="password" style="padding:10px;margin:6px;width:260px;"><br>

<button onclick="login()" style="padding:10px 18px;margin-top:10px;">登录</button>

<p style="margin-top:18px;">
  <a href="/register-v108.html" style="color:#9ecbff;">没有账号？去注册</a>
</p>

<script>
async function login(){
  const email = document.getElementById("email").value.trim();
  const pw = document.getElementById("pw").value.trim();

  if(!email || !pw){
    alert("请输入邮箱和密码");
    return;
  }

  const res = await fetch("/api/login_v109?email=" + encodeURIComponent(email) + "&pw=" + encodeURIComponent(pw));
  const data = await res.json();

  if(data.status === "ok"){
    localStorage.setItem("tf_token", data.token);
    localStorage.setItem("tf_email", data.email);
    localStorage.setItem("tf_plan", data.plan);
    alert("登录成功");
    location.href = "/dashboard-v108.html";
  }else{
    alert("登录失败");
  }
}
</script>
</body>
</html>
EOF

########################
# REGISTER PAGE
########################
cat > web/register-v108.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge Register</title>
</head>
<body style="background:#081224;color:white;font-family:Arial;padding:40px;">
<h1>TrendForge Register</h1>

<input id="email" placeholder="email" style="padding:10px;margin:6px;width:260px;"><br>
<input id="pw" placeholder="password" type="password" style="padding:10px;margin:6px;width:260px;"><br>

<button onclick="reg()" style="padding:10px 18px;margin-top:10px;">Register</button>

<p style="margin-top:18px;">
  <a href="/login-v108.html" style="color:#9ecbff;">已有账号？去登录</a>
</p>

<script>
async function reg(){
  const email = document.getElementById("email").value.trim();
  const pw = document.getElementById("pw").value.trim();

  if(!email || !pw){
    alert("please input email and password");
    return;
  }

  const res = await fetch("/api/register_v109?email=" + encodeURIComponent(email) + "&pw=" + encodeURIComponent(pw));
  const data = await res.json();

  if(data.status === "ok"){
    alert("register success, please login");
    location.href = "/login-v108.html";
  }else{
    alert("register fail: " + (data.error || ""));
  }
}
</script>
</body>
</html>
EOF

########################
# DASHBOARD PAGE
########################
cat > web/dashboard-v108.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TrendForge Dashboard</title>
</head>
<body style="background:#081224;color:white;font-family:Arial;padding:40px;">
<h1>用户仪表盘</h1>

<div id="userbox" style="background:#16233d;padding:20px;border-radius:16px;max-width:700px;margin-bottom:20px;">
加载中...
</div>

<ul>
<li><a href="/home-portal-v106.html" style="color:#9ecbff;">指挥中心</a></li>
<li><a href="/commercial-dashboard-v105.html" style="color:#9ecbff;">系统概述</a></li>
<li><a href="/index-v107.html" style="color:#9ecbff;">首页</a></li>
</ul>

<button onclick="logout()" style="padding:10px 18px;margin-top:20px;">退出登录</button>

<script>
async function loadMe(){
  const token = localStorage.getItem("tf_token");
  if(!token){
    location.href = "/login-v108.html";
    return;
  }

  const res = await fetch("/api/me_v109?token=" + encodeURIComponent(token));
  const data = await res.json();

  if(data.status !== "ok"){
    localStorage.removeItem("tf_token");
    localStorage.removeItem("tf_email");
    localStorage.removeItem("tf_plan");
    location.href = "/login-v108.html";
    return;
  }

  document.getElementById("userbox").innerHTML = `
    <div style="font-size:28px;font-weight:bold;margin-bottom:12px;">欢迎回来</div>
    <div style="margin-bottom:8px;">邮箱：${data.email}</div>
    <div style="margin-bottom:8px;">套餐：${data.plan}</div>
    <div>状态：ACTIVE</div>
  `;
}

function logout(){
  localStorage.removeItem("tf_token");
  localStorage.removeItem("tf_email");
  localStorage.removeItem("tf_plan");
  location.href = "/login-v108.html";
}

loadMe();
</script>
</body>
</html>
EOF

echo "TrendForge V109 files installed successfully."
