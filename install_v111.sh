#!/bin/bash

echo "Installing TrendForge V111..."

mkdir -p /root/trendforge-mvp/server
mkdir -p /root/trendforge-mvp/server/sql
mkdir -p /root/trendforge-mvp/web

############################
# SQL
############################
cat > /root/trendforge-mvp/server/sql/migrate_v111.sql << 'EOF'
CREATE TABLE IF NOT EXISTS users_v108 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    plan TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions_v109 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    token TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

############################
# FastAPI auth server (V111 ability, file keeps v110 for stability)
############################
cat > /root/trendforge-mvp/server/auth_server_v110.py << 'EOF'
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import hashlib
import uuid

DB = "/root/trendforge-mvp/server/trendforge.db"

app = FastAPI(title="TrendForge Auth V111")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def ensure_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users_v108 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        plan TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions_v109 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        token TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    ensure_tables()

@app.get("/api/register_v110")
def register_v110(
    email: str = Query(...),
    pw: str = Query(...)
):
    email = email.strip().lower()
    pw = pw.strip()

    if not email or not pw:
        return {"status": "fail", "error": "email_or_password_empty"}

    conn = get_conn()
    cur = conn.cursor()

    exists = cur.execute(
        "SELECT id FROM users_v108 WHERE email=?",
        (email,)
    ).fetchone()

    if exists:
        conn.close()
        return {"status": "fail", "error": "email_exists"}

    cur.execute(
        "INSERT INTO users_v108 (email, password, plan) VALUES (?, ?, ?)",
        (email, hash_pw(pw), "free")
    )
    conn.commit()
    conn.close()

    return {"status": "ok", "email": email, "plan": "free"}

@app.get("/api/login_v111")
def login_v111(
    email: str = Query(...),
    pw: str = Query(...)
):
    email = email.strip().lower()
    pw = pw.strip()

    if not email or not pw:
        return {"status": "fail", "error": "email_or_password_empty"}

    conn = get_conn()
    cur = conn.cursor()

    row = cur.execute(
        "SELECT email, plan FROM users_v108 WHERE email=? AND password=?",
        (email, hash_pw(pw))
    ).fetchone()

    if not row:
        conn.close()
        return {"status": "fail", "error": "invalid_credentials"}

    token = "TFSESS-" + uuid.uuid4().hex[:24].upper()

    cur.execute(
        "INSERT INTO sessions_v109 (email, token) VALUES (?, ?)",
        (row["email"], token)
    )
    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "email": row["email"],
        "plan": row["plan"],
        "token": token
    }

@app.get("/api/me_v111")
def me_v111(
    token: str = Query(...)
):
    token = token.strip()

    conn = get_conn()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT u.email, u.plan
        FROM sessions_v109 s
        JOIN users_v108 u ON s.email = u.email
        WHERE s.token=?
        ORDER BY s.id DESC
        LIMIT 1
        """,
        (token,)
    ).fetchone()

    conn.close()

    if not row:
        return {"status": "fail", "error": "invalid_token"}

    return {
        "status": "ok",
        "email": row["email"],
        "plan": row["plan"]
    }

@app.get("/api/logout_v111")
def logout_v111(
    token: str = Query(...)
):
    token = token.strip()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM sessions_v109 WHERE token=?", (token,))
    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.get("/api/health_v111")
def health_v111():
    return {"status": "ok", "service": "trendforge-auth-v111"}
EOF

############################
# login page
############################
cat > /root/trendforge-mvp/web/login-v108.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
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

  const res = await fetch("/api/login_v111?email=" + encodeURIComponent(email) + "&pw=" + encodeURIComponent(pw));
  const data = await res.json();

  if(data.status === "ok"){
    localStorage.setItem("tf_token", data.token);
    localStorage.setItem("tf_email", data.email);
    localStorage.setItem("tf_plan", data.plan);
    alert("登录成功");
    location.href = "/dashboard-v108.html";
  }else{
    alert("登录失败：" + (data.error || ""));
  }
}
</script>
</body>
</html>
EOF

############################
# register page (keep successful V110 register)
############################
cat > /root/trendforge-mvp/web/register-v108.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrendForge 注册</title>
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

  const res = await fetch("/api/register_v110?email=" + encodeURIComponent(email) + "&pw=" + encodeURIComponent(pw));
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

############################
# dashboard page
############################
cat > /root/trendforge-mvp/web/dashboard-v108.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
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

  const res = await fetch("/api/me_v111?token=" + encodeURIComponent(token));
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

async function logout(){
  const token = localStorage.getItem("tf_token");
  if(token){
    try{
      await fetch("/api/logout_v111?token=" + encodeURIComponent(token));
    }catch(e){}
  }

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

echo "TrendForge V111 files installed successfully."
