#!/bin/bash

echo "Installing TrendForge V124..."

mkdir -p /root/trendforge-mvp/server/payments
mkdir -p /root/trendforge-mvp/web/payments

cat > /root/trendforge-mvp/server/payments/wechat_pay_server.py << 'EOF'
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import sqlite3
import qrcode
import base64
from io import BytesIO

DB = "/root/trendforge-mvp/server/trendforge.db"

app = FastAPI(title="TrendForge WeChat Pay Server V124")

PRICE_RULES = {
    "pro": "¥99 / month",
    "vip": "¥299 / month"
}

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables():
    conn = get_conn()
    cur = conn.cursor()

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users_v108 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        plan TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def make_qr_base64(text: str) -> str:
    img = qrcode.make(text)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

@app.on_event("startup")
def startup():
    ensure_tables()

@app.get("/wechat/pay_page", response_class=HTMLResponse)
def pay_page(
    email: str = Query(...),
    plan: str = Query(...)
):
    email = email.strip().lower()
    plan = plan.strip().lower()

    if plan not in PRICE_RULES:
        return "<h1>invalid plan</h1>"

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO billing_orders_v119 (email, plan, price, status)
        VALUES (?, ?, ?, ?)
        """,
        (email, plan, PRICE_RULES[plan], "pending")
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    fake_pay_text = f"TrendForge WeChat QR | order={order_id} | email={email} | plan={plan} | price={PRICE_RULES[plan]}"
    qr_b64 = make_qr_base64(fake_pay_text)

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>TrendForge 微信支付</title>
      <style>
        body {{
          margin:0;
          font-family:Arial,Helvetica,sans-serif;
          background:linear-gradient(180deg,#06101f 0%, #081224 100%);
          color:#fff;
        }}
        .wrap {{
          max-width:900px;
          margin:0 auto;
          padding:40px 20px 60px;
        }}
        .card {{
          background:#16233d;
          border-radius:26px;
          padding:30px;
        }}
        .title {{
          font-size:42px;
          font-weight:900;
          margin-bottom:16px;
        }}
        .sub {{
          font-size:20px;
          color:#c5d6f3;
          line-height:1.8;
          margin-bottom:24px;
        }}
        .grid {{
          display:grid;
          grid-template-columns:1fr 320px;
          gap:22px;
        }}
        .box {{
          background:#0c1730;
          border-radius:18px;
          padding:18px;
          line-height:1.9;
          font-size:18px;
        }}
        .qrbox {{
          background:#fff;
          border-radius:18px;
          padding:16px;
          text-align:center;
        }}
        .qrbox img {{
          width:100%;
          max-width:260px;
          height:auto;
        }}
        .btns {{
          display:flex;
          flex-wrap:wrap;
          gap:14px;
          margin-top:20px;
        }}
        button, a.btn {{
          border:none;
          border-radius:16px;
          padding:14px 18px;
          font-size:18px;
          font-weight:800;
          cursor:pointer;
          text-decoration:none;
        }}
        .btn-main {{
          background:#3bb54a;
          color:#fff;
        }}
        .btn-light {{
          background:#fff;
          color:#091325;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <div class="title">TrendForge 微信支付</div>
          <div class="sub">V124 微信支付演示版：扫码后点击“模拟支付成功”，将自动写入订单并升级套餐。</div>

          <div class="grid">
            <div class="box">
              订单号：#{order_id}<br>
              邮箱：{email}<br>
              套餐：{plan.upper()}<br>
              价格：{PRICE_RULES[plan]}<br>
              状态：PENDING
            </div>

            <div class="qrbox">
              <img src="data:image/png;base64,{qr_b64}" alt="微信二维码" />
              <div style="margin-top:12px;color:#091325;font-weight:800;">微信扫码支付（演示版）</div>
            </div>
          </div>

          <div class="btns">
            <button class="btn-main" onclick="window.location.href='/wechat/simulate_paid?order_id={order_id}'">模拟支付成功</button>
            <a class="btn btn-light" href="/subscription-v116.html">返回订阅页</a>
            <a class="btn btn-light" href="/billing-history-v119.html">Billing History</a>
          </div>
        </div>
      </div>
    </body>
    </html>
    """

@app.get("/wechat/simulate_paid", response_class=HTMLResponse)
def simulate_paid(order_id: int = Query(...)):
    conn = get_conn()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT id, email, plan, price, status
        FROM billing_orders_v119
        WHERE id=?
        """,
        (order_id,)
    ).fetchone()

    if not row:
        conn.close()
        return "<h1>order not found</h1>"

    cur.execute(
        "UPDATE billing_orders_v119 SET status='paid' WHERE id=?",
        (order_id,)
    )

    if row["plan"] in ["pro", "vip"]:
        cur.execute(
            "UPDATE users_v108 SET plan=? WHERE email=?",
            (row["plan"], row["email"])
        )

    conn.commit()
    conn.close()

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>TrendForge 微信支付成功</title>
      <style>
        body {{
          margin:0;
          font-family:Arial,Helvetica,sans-serif;
          background:linear-gradient(180deg,#06101f 0%, #081224 100%);
          color:#fff;
        }}
        .wrap {{
          max-width:800px;
          margin:0 auto;
          padding:40px 20px 60px;
        }}
        .card {{
          background:#16233d;
          border-radius:26px;
          padding:30px;
        }}
        .ok {{
          display:inline-block;
          background:#2f8f4e;
          padding:10px 18px;
          border-radius:999px;
          font-weight:800;
          margin-bottom:18px;
        }}
        .title {{
          font-size:38px;
          font-weight:900;
          margin-bottom:16px;
        }}
        .box {{
          background:#0c1730;
          border-radius:18px;
          padding:18px;
          line-height:1.9;
          font-size:18px;
          margin-bottom:18px;
        }}
        a {{
          color:#9ecbff;
          font-size:18px;
          line-height:2;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <div class="ok">PAY SUCCESS</div>
          <div class="title">微信支付成功（演示）</div>
          <div class="box">
            订单号：#{row["id"]}<br>
            邮箱：{row["email"]}<br>
            套餐：{row["plan"].upper()}<br>
            价格：{row["price"]}<br>
            状态：PAID<br><br>
            用户套餐已同步升级。
          </div>

          <a href="/billing-history-v119.html">查看 Billing History</a><br>
          <a href="/dashboard-v108.html">返回 Dashboard</a><br>
          <a href="/subscription-v116.html">返回订阅页</a>
        </div>
      </div>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "service": "trendforge-wechat-v124"}
EOF

cat > /etc/systemd/system/trendforge-wechat-v124.service << 'EOF'
[Unit]
Description=TrendForge WeChat V124 FastAPI Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/trendforge-mvp/server/payments
ExecStart=/usr/bin/python3 -m uvicorn wechat_pay_server:app --host 127.0.0.1 --port 8030
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable trendforge-wechat-v124.service

echo "V124 installation completed."
