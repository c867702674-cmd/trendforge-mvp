#!/bin/bash

echo "Installing TrendForge V112..."

mkdir -p /root/trendforge-mvp/server
mkdir -p /root/trendforge-mvp/server/sql
mkdir -p /root/trendforge-mvp/web

############################
# SQL
############################
cat > /root/trendforge-mvp/server/sql/migrate_v112.sql << 'EOF'
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
# FastAPI auth server (upgrade to V112 capability, file name kept stable)
############################
cat > /root/trendforge-mvp/server/auth_server_v110.py << 'EOF'
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import hashlib
import uuid

DB = "/root/trendforge-mvp/server/trendforge.db"

app = FastAPI(title="TrendForge Auth V112")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLAN_RULES = {
    "free": {
        "daily_limit": 3,
        "listing_ai": False,
        "mj_prompt": False,
        "command_center": False
    },
    "pro": {
        "daily_limit": 20,
        "listing_ai": True,
        "mj_prompt": True,
        "command_center": False
    },
    "vip": {
        "daily_limit": 999,
        "listing_ai": True,
        "mj_prompt": True,
        "command_center": True
    }
}

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

def plan_payload(plan: str):
    plan = (plan or "free").lower()
    rule = PLAN_RULES.get(plan, PLAN_RULES["free"])
    return {
        "plan": plan,
        "daily_limit": rule["daily_limit"],
        "listing_ai": rule["listing_ai"],
        "mj_prompt": rule["mj_prompt"],
        "command_center": rule["command_center"]
    }

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

@app.get("/api/plan_v112")
def plan_v112(
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

    payload = plan_payload(row["plan"])
    return {
        "status": "ok",
        "email": row["email"],
        **payload
    }

@app.get("/api/upgrade_preview_v112")
def upgrade_preview_v112(
    target_plan: str = Query(...)
):
    target_plan = target_plan.strip().lower()
    if target_plan not in PLAN_RULES:
        return {"status": "fail", "error": "invalid_plan"}

    payload = plan_payload(target_plan)
    return {
        "status": "ok",
        **payload
    }

@app.get("/api/health_v111")
def health_v111():
    return {"status": "ok", "service": "trendforge-auth-v112"}
EOF

############################
# dashboard page upgraded to plan capability view
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

<div id="userbox" style="background:#16233d;padding:20px;border-radius:16px;max-width:780px;margin-bottom:20px;">
加载中...
</div>

<div id="planbox" style="background:#16233d;padding:20px;border-radius:16px;max-width:780px;margin-bottom:20px;">
加载套餐能力中...
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
    clearLocal();
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

async function loadPlan(){
  const token = localStorage.getItem("tf_token");
  if(!token){
    location.href = "/login-v108.html";
    return;
  }

  const res = await fetch("/api/plan_v112?token=" + encodeURIComponent(token));
  const data = await res.json();

  if(data.status !== "ok"){
    document.getElementById("planbox").innerHTML = "套餐能力加载失败";
    return;
  }

  document.getElementById("planbox").innerHTML = `
    <div style="font-size:24px;font-weight:bold;margin-bottom:12px;">套餐能力</div>
    <div style="margin-bottom:8px;">当前套餐：${data.plan}</div>
    <div style="margin-bottom:8px;">每日趋势额度：${data.daily_limit}</div>
    <div style="margin-bottom:8px;">Listing AI：${data.listing_ai ? 'YES' : 'NO'}</div>
    <div style="margin-bottom:8px;">MJ Prompt：${data.mj_prompt ? 'YES' : 'NO'}</div>
    <div>Command Center：${data.command_center ? 'YES' : 'NO'}</div>
  `;
}

function clearLocal(){
  localStorage.removeItem("tf_token");
  localStorage.removeItem("tf_email");
  localStorage.removeItem("tf_plan");
}

async function logout(){
  const token = localStorage.getItem("tf_token");
  if(token){
    try{
      await fetch("/api/logout_v111?token=" + encodeURIComponent(token));
    }catch(e){}
  }
  clearLocal();
  location.href = "/login-v108.html";
}

loadMe();
loadPlan();
</script>
</body>
</html>
EOF

echo "TrendForge V112 files installed successfully."
