#!/bin/bash

echo "Installing TrendForge V125..."

mkdir -p /root/trendforge-mvp/server/payments

cat > /root/trendforge-mvp/server/payments/stripe_pay_server.py << 'EOF'
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import sqlite3

DB = "/root/trendforge-mvp/server/trendforge.db"

app = FastAPI(title="TrendForge Stripe Server V125")

PRICE_RULES = {
    "pro": "$39 / month",
    "vip": "$99 / month"
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

@app.on_event("startup")
def startup():
    ensure_tables()

@app.get("/stripe/pay_page", response_class=HTMLResponse)
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

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>TrendForge Stripe Checkout</title>
      <style>
        body {{
          margin:0;
          font-family:Arial,Helvetica,sans-serif;
          background:linear-gradient(180deg,#06101f 0%, #081224 100%);
          color:#fff;
        }}
        .wrap {{
          max-width:1100px;
          margin:0 auto;
          padding:40px 20px 60px;
        }}
        .card {{
          background:#16233d;
          border-radius:26px;
          padding:30px;
        }}
        .title {{
          font-size:44px;
          font-weight:900;
          margin-bottom:12px;
        }}
        .sub {{
          font-size:20px;
          color:#c5d6f3;
          line-height:1.8;
          margin-bottom:24px;
        }}
        .grid {{
          display:grid;
          grid-template-columns:1.2fr .9fr;
          gap:22px;
        }}
        .box {{
          background:#0c1730;
          border-radius:18px;
          padding:20px;
          line-height:1.9;
          font-size:18px;
        }}
        .paybox {{
          background:#0c1730;
          border-radius:18px;
          padding:20px;
        }}
        .paycard {{
          background:#ffffff;
          color:#111;
          border-radius:16px;
          padding:18px;
          margin-bottom:16px;
        }}
        .fake-input {{
          border:1px solid #d9d9d9;
          border-radius:10px;
          padding:12px;
          font-size:16px;
          margin-top:10px;
          background:#fafafa;
        }}
        .btns {{
          display:flex;
          flex-wrap:wrap;
          gap:14px;
          margin-top:18px;
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
          background:#635bff;
          color:#fff;
        }}
        .btn-light {{
          background:#fff;
          color:#091325;
        }}
        @media (max-width: 820px) {{
          .grid {{ grid-template-columns:1fr; }}
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <div class="title">TrendForge Stripe Checkout</div>
          <div class="sub">V125 Global payment page: Stripe Checkout demo version. Next step can connect real Stripe Checkout Session.</div>

          <div class="grid">
            <div class="box">
              Order ID: #{order_id}<br>
              Email: {email}<br>
              Plan: {plan.upper()}<br>
              Price: {PRICE_RULES[plan]}<br>
              Status: PENDING<br><br>

              Global pricing:<br>
              PRO: $39 / month<br>
              VIP: $99 / month<br><br>

              This page is the demo version of Stripe international checkout. After clicking the button below, the system will simulate payment success, write billing order, and upgrade user plan.
            </div>

            <div class="paybox">
              <div class="paycard">
                <div style="font-size:26px;font-weight:900;margin-bottom:8px;">Stripe</div>
                <div style="color:#666;margin-bottom:12px;">Card payment demo</div>

                <div class="fake-input">Card number: 4242 4242 4242 4242</div>
                <div class="fake-input">Expiry: 12 / 34</div>
                <div class="fake-input">CVC: 123</div>
              </div>

              <div class="btns">
                <button class="btn-main" onclick="window.location.href='/stripe/simulate_paid?order_id={order_id}'">Simulate Stripe Success</button>
                <a class="btn btn-light" href="/subscription-v116.html">Back to Subscription</a>
                <a class="btn btn-light" href="/billing-history-v119.html">Billing History</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """

@app.get("/stripe/simulate_paid", response_class=HTMLResponse)
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
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>TrendForge Stripe Success</title>
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
          <div class="title">Stripe Payment Success (Demo)</div>
          <div class="box">
            Order ID: #{row["id"]}<br>
            Email: {row["email"]}<br>
            Plan: {row["plan"].upper()}<br>
            Price: {row["price"]}<br>
            Status: PAID<br><br>
            User subscription has been upgraded successfully.
          </div>

          <a href="/billing-history-v119.html">View Billing History</a><br>
          <a href="/dashboard-v108.html">Back to Dashboard</a><br>
          <a href="/subscription-v116.html">Back to Subscription</a>
        </div>
      </div>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "service": "trendforge-stripe-v125"}
EOF

cat > /etc/systemd/system/trendforge-stripe-v125.service << 'EOF'
[Unit]
Description=TrendForge Stripe V125 FastAPI Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/trendforge-mvp/server/payments
ExecStart=/usr/bin/python3 -m uvicorn stripe_pay_server:app --host 127.0.0.1 --port 8040
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable trendforge-stripe-v125.service

echo "V125 installation completed."
