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
