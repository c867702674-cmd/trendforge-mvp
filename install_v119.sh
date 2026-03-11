#!/bin/bash

echo "Installing TrendForge V119..."

mkdir -p /root/trendforge-mvp/server/sql
mkdir -p /root/trendforge-mvp/web

############################
# SQL
############################
cat > /root/trendforge-mvp/server/sql/migrate_v119.sql << 'EOF'
CREATE TABLE IF NOT EXISTS billing_orders_v119 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    plan TEXT,
    price TEXT,
    status TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
EOF

############################
# Upgrade auth/billing server
############################
cat > /root/trendforge-mvp/server/auth_server_v110.py << 'EOF'
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import hashlib
import uuid

DB = "/root/trendforge-mvp/server/trendforge.db"

app = FastAPI(title="TrendForge Auth V119")

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
        "command_center": False,
        "price": "$0/month"
    },
    "pro": {
        "daily_limit": 20,
        "listing_ai": True,
        "mj_prompt": True,
        "command_center": False,
        "price": "$39/month"
    },
    "vip": {
        "daily_limit": 999,
        "listing_ai": True,
        "mj_prompt": True,
        "command_center": True,
        "price": "$99/month"
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS billing_orders_v119 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        plan TEXT,
        price TEXT,
        status TEXT,
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
        "command_center": rule["command_center"],
        "price": rule["price"]
    }

def get_user_by_token(token: str):
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
    return row

@app.on_event("startup")
def startup():
    ensure_tables()

@app.get("/api/register_v110")
def register_v110(email: str = Query(...), pw: str = Query(...)):
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
def login_v111(email: str = Query(...), pw: str = Query(...)):
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
def me_v111(token: str = Query(...)):
    token = token.strip()
    row = get_user_by_token(token)

    if not row:
        return {"status": "fail", "error": "invalid_token"}

    return {
        "status": "ok",
        "email": row["email"],
        "plan": row["plan"]
    }

@app.get("/api/logout_v111")
def logout_v111(token: str = Query(...)):
    token = token.strip()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions_v109 WHERE token=?", (token,))
    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.get("/api/plan_v112")
def plan_v112(token: str = Query(...)):
    token = token.strip()
    row = get_user_by_token(token)

    if not row:
        return {"status": "fail", "error": "invalid_token"}

    payload = plan_payload(row["plan"])
    return {
        "status": "ok",
        "email": row["email"],
        **payload
    }

@app.get("/api/access_check_v113")
def access_check_v113(token: str = Query(...), module: str = Query(...)):
    token = token.strip()
    module = module.strip()

    row = get_user_by_token(token)
    if not row:
        return {"status": "fail", "error": "invalid_token"}

    payload = plan_payload(row["plan"])

    if module not in ["listing_ai", "mj_prompt", "command_center"]:
        return {"status": "fail", "error": "invalid_module"}

    allowed = bool(payload.get(module, False))

    return {
        "status": "ok",
        "email": row["email"],
        "plan": payload["plan"],
        "module": module,
        "allowed": allowed
    }

@app.get("/api/change_plan_v114")
def change_plan_v114(token: str = Query(...), target_plan: str = Query(...)):
    token = token.strip()
    target_plan = target_plan.strip().lower()

    if target_plan not in PLAN_RULES:
        return {"status": "fail", "error": "invalid_plan"}

    row = get_user_by_token(token)
    if not row:
        return {"status": "fail", "error": "invalid_token"}

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users_v108 SET plan=? WHERE email=?",
        (target_plan, row["email"])
    )
    conn.commit()
    conn.close()

    payload = plan_payload(target_plan)
    return {
        "status": "ok",
        "email": row["email"],
        **payload
    }

@app.get("/api/billing_preview_v115")
def billing_preview_v115(token: str = Query(...)):
    token = token.strip()
    row = get_user_by_token(token)

    if not row:
        return {"status": "fail", "error": "invalid_token"}

    current_payload = plan_payload(row["plan"])

    return {
        "status": "ok",
        "email": row["email"],
        "current_plan": current_payload["plan"],
        "current_price": current_payload["price"],
        "pro_price": PLAN_RULES["pro"]["price"],
        "vip_price": PLAN_RULES["vip"]["price"],
        "note": "Stripe / 微信 / 支付宝入口预留中"
    }

@app.get("/api/checkout_link_v115")
def checkout_link_v115(token: str = Query(...), target_plan: str = Query(...)):
    token = token.strip()
    target_plan = target_plan.strip().lower()

    row = get_user_by_token(token)
    if not row:
        return {"status": "fail", "error": "invalid_token"}

    if target_plan not in ["pro", "vip"]:
        return {"status": "fail", "error": "invalid_target_plan"}

    fake_link = f"https://trendforgepro.com/billing-checkout-v115.html?plan={target_plan}&email={row['email']}"

    return {
        "status": "ok",
        "email": row["email"],
        "target_plan": target_plan,
        "checkout_link": fake_link,
        "note": "当前为支付入口预留版，下一步可接 Stripe / 微信 / 支付宝"
    }

@app.get("/api/create_order_v119")
def create_order_v119(
    email: str = Query(...),
    plan: str = Query(...),
    price: str = Query(...)
):
    email = email.strip().lower()
    plan = plan.strip().lower()
    price = price.strip()

    if not email or not plan or not price:
        return {"status": "fail", "error": "missing_params"}

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO billing_orders_v119 (email, plan, price, status)
        VALUES (?, ?, ?, ?)
        """,
        (email, plan, price, "created")
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "order_id": order_id,
        "email": email,
        "plan": plan,
        "price": price
    }

@app.get("/api/billing_history_v119")
def billing_history_v119(email: str = Query(...)):
    email = email.strip().lower()

    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id, email, plan, price, status, created_at
        FROM billing_orders_v119
        WHERE email=?
        ORDER BY id DESC
        LIMIT 50
        """,
        (email,)
    ).fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "email": r["email"],
            "plan": r["plan"],
            "price": r["price"],
            "status": r["status"],
            "created_at": r["created_at"]
        })

    return {
        "status": "ok",
        "email": email,
        "items": items
    }

@app.get("/api/health_v111")
def health_v111():
    return {"status": "ok", "service": "trendforge-auth-v119"}
EOF

############################
# Billing history page
############################
cat > /root/trendforge-mvp/web/billing-history-v119.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TrendForge Billing History V119</title>
  <style>
    * { box-sizing:border-box; }
    body{
      margin:0;
      font-family:Arial,Helvetica,sans-serif;
      background:linear-gradient(180deg,#06101f 0%, #081224 100%);
      color:#fff;
    }
    .wrap{
      max-width:1180px;
      margin:0 auto;
      padding:36px 24px 70px;
    }
    .hero{
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:20px;
      flex-wrap:wrap;
      margin-bottom:24px;
    }
    .brand{
      font-size:50px;
      font-weight:900;
      margin-bottom:12px;
    }
    .sub{
      color:#9db3d9;
      font-size:19px;
      line-height:1.7;
      max-width:760px;
    }
    .badge{
      background:#173154;
      border:1px solid rgba(120,180,255,.25);
      padding:12px 18px;
      border-radius:999px;
      font-size:14px;
      font-weight:800;
      color:#dbeaff;
    }
    .panel{
      background:#16233d;
      border-radius:24px;
      padding:26px;
      margin-bottom:22px;
    }
    .title{
      font-size:30px;
      font-weight:900;
      margin-bottom:16px;
    }
    .searchbox{
      display:flex;
      gap:12px;
      flex-wrap:wrap;
      margin-bottom:18px;
    }
    input{
      flex:1;
      min-width:260px;
      padding:14px 16px;
      border:none;
      border-radius:14px;
      font-size:17px;
    }
    button{
      border:none;
      border-radius:14px;
      padding:14px 18px;
      font-size:17px;
      font-weight:800;
      cursor:pointer;
      background:#5c8fff;
      color:#fff;
    }
    .result{
      background:#0c1730;
      border-radius:18px;
      padding:16px;
      margin-bottom:16px;
      line-height:1.8;
      color:#eef4ff;
    }
    .order{
      background:#0c1730;
      border-radius:18px;
      padding:18px;
      margin-bottom:14px;
    }
    .order-title{
      font-size:24px;
      font-weight:900;
      margin-bottom:10px;
    }
    .row{
      margin-bottom:6px;
      color:#eef4ff;
      line-height:1.7;
    }
    a{
      color:#9ecbff;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div>
        <div class="brand">TrendForge</div>
        <div class="sub">
          V119 Billing History 页面版：展示支付模拟后写入的订单记录，形成真正的订单历史页。
        </div>
      </div>
      <div class="badge">Billing History</div>
    </div>

    <div class="panel">
      <div class="title">查询订单记录</div>
      <div class="searchbox">
        <input id="emailInput" placeholder="输入邮箱，例如 867702614@qq.com" />
        <button onclick="loadOrders()">查询订单</button>
      </div>
      <div class="result" id="summaryBox">等待查询...</div>
      <div id="ordersWrap"></div>
      <div style="margin-top:18px;line-height:2;">
        <a href="/subscription-v116.html">返回订阅页</a><br/>
        <a href="/dashboard-v108.html">返回 Dashboard</a>
      </div>
    </div>
  </div>

  <script>
    function guessEmailFromLocal(){
      const e = localStorage.getItem("tf_email");
      if(e){
        document.getElementById("emailInput").value = e;
      }
    }

    async function loadOrders(){
      const email = (document.getElementById("emailInput").value || "").trim().toLowerCase();
      if(!email){
        document.getElementById("summaryBox").innerText = "请先输入邮箱";
        return;
      }

      const res = await fetch("/api/billing_history_v119?email=" + encodeURIComponent(email));
      const data = await res.json();

      if(data.status !== "ok"){
        document.getElementById("summaryBox").innerText = "订单记录加载失败";
        return;
      }

      document.getElementById("summaryBox").innerHTML =
        "查询邮箱：" + data.email + "<br>" +
        "订单数量：" + data.items.length;

      const wrap = document.getElementById("ordersWrap");
      wrap.innerHTML = "";

      if(data.items.length === 0){
        wrap.innerHTML = '<div class="order"><div class="order-title">暂无订单</div><div class="row">这个邮箱还没有支付模拟记录。</div></div>';
        return;
      }

      data.items.forEach(item => {
        const div = document.createElement("div");
        div.className = "order";
        div.innerHTML = `
          <div class="order-title">Order #${item.id}</div>
          <div class="row">邮箱：${item.email}</div>
          <div class="row">套餐：${item.plan.toUpperCase()}</div>
          <div class="row">价格：${item.price}</div>
          <div class="row">状态：${item.status}</div>
          <div class="row">创建时间：${item.created_at}</div>
        `;
        wrap.appendChild(div);
      });
    }

    guessEmailFromLocal();
  </script>
</body>
</html>
EOF

############################
# Checkout page upgraded with order create
############################
cat > /root/trendforge-mvp/web/billing-checkout-v115.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TrendForge Billing Checkout V119</title>
  <style>
    * { box-sizing:border-box; }
    body{
      margin:0;
      font-family:Arial,Helvetica,sans-serif;
      background:linear-gradient(180deg,#06101f 0%, #081224 100%);
      color:#fff;
    }
    .wrap{
      max-width:1120px;
      margin:0 auto;
      padding:36px 24px 70px;
    }
    .hero{
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:20px;
      flex-wrap:wrap;
      margin-bottom:24px;
    }
    .brand{
      font-size:52px;
      font-weight:900;
      margin-bottom:14px;
      line-height:1;
    }
    .sub{
      color:#9db3d9;
      font-size:20px;
      line-height:1.7;
      max-width:780px;
    }
    .badge{
      background:#173154;
      border:1px solid rgba(120,180,255,.25);
      padding:12px 18px;
      border-radius:999px;
      font-size:15px;
      font-weight:800;
      color:#dbeaff;
      white-space:nowrap;
    }
    .grid{
      display:grid;
      grid-template-columns:1.2fr .8fr;
      gap:22px;
    }
    .panel{
      background:#16233d;
      border-radius:24px;
      padding:26px;
      box-shadow:0 10px 28px rgba(0,0,0,.18);
    }
    .title{
      font-size:30px;
      font-weight:900;
      margin-bottom:18px;
    }
    .summary-box{
      background:#0c1730;
      border-radius:18px;
      padding:18px;
      margin-bottom:16px;
    }
    .row{
      display:flex;
      justify-content:space-between;
      gap:16px;
      padding:10px 0;
      border-bottom:1px solid rgba(255,255,255,.06);
      font-size:18px;
    }
    .row:last-child{ border-bottom:none; }
    .label{ color:#9db3d9; }
    .value{
      font-weight:800;
      text-align:right;
      word-break:break-word;
    }
    .pay-list{
      display:grid;
      gap:14px;
      margin-top:12px;
    }
    .pay-item{
      background:#0c1730;
      border:1px solid rgba(255,255,255,.06);
      border-radius:18px;
      padding:18px;
    }
    .pay-name{
      font-size:22px;
      font-weight:900;
      margin-bottom:8px;
    }
    .pay-desc{
      color:#c7d7f5;
      line-height:1.8;
      font-size:16px;
    }
    .cta{
      margin-top:18px;
      display:flex;
      flex-direction:column;
      gap:14px;
    }
    .btn{
      border:none;
      border-radius:16px;
      padding:15px 18px;
      font-size:18px;
      font-weight:800;
      cursor:pointer;
    }
    .btn-main{
      background:#5c8fff;
      color:#fff;
    }
    .btn-light{
      background:#fff;
      color:#091325;
    }
    .note{
      margin-top:16px;
      background:#0c1730;
      border-radius:18px;
      padding:18px;
      color:#eef4ff;
      line-height:1.85;
      font-size:16px;
    }
    .links{
      margin-top:16px;
      line-height:2;
    }
    .links a{
      color:#9ecbff;
    }
    @media (max-width: 900px){
      .grid{ grid-template-columns:1fr; }
    }
    @media (max-width: 640px){
      .wrap{ padding:22px 14px 50px; }
      .brand{ font-size:38px; }
      .sub{ font-size:17px; }
      .row{ flex-direction:column; }
      .value{ text-align:left; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div>
        <div class="brand">TrendForge</div>
        <div class="sub">
          V119 Checkout + 订单记录版：支付模拟后将自动写入订单记录，为 Billing History 页面提供真实数据来源。
        </div>
      </div>
      <div class="badge" id="topBadge">Checkout Ready</div>
    </div>

    <div class="grid">
      <div class="panel">
        <div class="title">订单摘要</div>
        <div class="summary-box">
          <div class="row"><div class="label">订阅邮箱</div><div class="value" id="emailValue">加载中...</div></div>
          <div class="row"><div class="label">目标套餐</div><div class="value" id="planValue">加载中...</div></div>
          <div class="row"><div class="label">订阅价格</div><div class="value" id="priceValue">加载中...</div></div>
          <div class="row"><div class="label">账单周期</div><div class="value">Monthly</div></div>
          <div class="row"><div class="label">当前状态</div><div class="value">支付入口预留版</div></div>
        </div>

        <div class="title" style="font-size:26px;">套餐权益摘要</div>
        <div class="note" id="benefitBox">加载套餐权益中...</div>
      </div>

      <div class="panel">
        <div class="title">支付方式</div>

        <div class="pay-list">
          <div class="pay-item">
            <div class="pay-name">Stripe</div>
            <div class="pay-desc">国际信用卡支付入口预留。下一步可直接接 Stripe Checkout Session。</div>
          </div>
          <div class="pay-item">
            <div class="pay-name">微信支付</div>
            <div class="pay-desc">面向中国客户的支付入口预留。后续可接微信 Native / H5 支付。</div>
          </div>
          <div class="pay-item">
            <div class="pay-name">支付宝</div>
            <div class="pay-desc">面向中国客户的支付入口预留。后续可接支付宝当面付 / 网页支付。</div>
          </div>
        </div>

        <div class="cta">
          <button class="btn btn-main" onclick="fakePay()">模拟进入支付流程并写入订单</button>
          <button class="btn btn-light" onclick="goBack()">返回订阅页</button>
        </div>

        <div class="note" id="payResult">
          当前为 Checkout + 订单记录版。下一步可以接真实支付和订单状态流转。
        </div>

        <div class="links">
          <a href="/billing-history-v119.html">查看 Billing History</a><br/>
          <a href="/subscription-v116.html">返回订阅页</a><br/>
          <a href="/dashboard-v108.html">返回 Dashboard</a>
        </div>
      </div>
    </div>
  </div>

  <script>
    function getQuery(name){
      const url = new URL(window.location.href);
      return url.searchParams.get(name) || "";
    }

    function planPrice(plan){
      if(plan === "pro") return "$39/month";
      if(plan === "vip") return "$99/month";
      return "$0/month";
    }

    function planBenefits(plan){
      if(plan === "vip"){
        return `
          目标套餐：VIP<br>
          每日趋势额度：999<br>
          Listing AI：YES<br>
          MJ Prompt：YES<br>
          Command Center：YES<br>
          适合团队化、商业化、高频运转场景。
        `;
      }
      if(plan === "pro"){
        return `
          目标套餐：PRO<br>
          每日趋势额度：20<br>
          Listing AI：YES<br>
          MJ Prompt：YES<br>
          Command Center：NO<br>
          适合个人高频上新卖家。
        `;
      }
      return `
          目标套餐：FREE<br>
          每日趋势额度：3<br>
          Listing AI：NO<br>
          MJ Prompt：NO<br>
          Command Center：NO<br>
          适合体验与试跑账号。
      `;
    }

    function render(){
      const plan = (getQuery("plan") || "free").toLowerCase();
      const email = getQuery("email") || "unknown@example.com";

      document.getElementById("emailValue").innerText = email;
      document.getElementById("planValue").innerText = plan.toUpperCase();
      document.getElementById("priceValue").innerText = planPrice(plan);
      document.getElementById("benefitBox").innerHTML = planBenefits(plan);
      document.getElementById("topBadge").innerText = "Checkout: " + plan.toUpperCase();
    }

    async function fakePay(){
      const plan = (getQuery("plan") || "free").toLowerCase();
      const email = getQuery("email") || "unknown@example.com";
      const price = planPrice(plan);

      const res = await fetch(
        "/api/create_order_v119?email=" + encodeURIComponent(email) +
        "&plan=" + encodeURIComponent(plan) +
        "&price=" + encodeURIComponent(price)
      );
      const data = await res.json();

      if(data.status === "ok"){
        document.getElementById("payResult").innerHTML =
          "已进入模拟支付流程，并成功写入订单记录。<br>" +
          "订单号：#" + data.order_id + "<br>" +
          "目标套餐：" + data.plan.toUpperCase() + "<br>" +
          "订阅邮箱：" + data.email + "<br>" +
          "价格：" + data.price + "<br>" +
          "下一步可接 Stripe / 微信 / 支付宝真实下单逻辑。";
      } else {
        document.getElementById("payResult").innerHTML = "订单写入失败";
      }
    }

    function goBack(){
      window.location.href = "/subscription-v116.html";
    }

    render();
  </script>
</body>
</html>
EOF

echo "TrendForge V119 files installed successfully."
