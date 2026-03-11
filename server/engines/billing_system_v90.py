#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, datetime

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

PLANS = [
    {
        "plan_code": "free",
        "plan_name": "Free",
        "monthly_price_usd": 0,
        "yearly_price_usd": 0,
        "can_view_listing_ai": 0,
        "can_view_mj_prompt": 0,
        "can_view_command_center": 0,
        "daily_trend_limit": 3,
    },
    {
        "plan_code": "pro",
        "plan_name": "Pro",
        "monthly_price_usd": 39,
        "yearly_price_usd": 390,
        "can_view_listing_ai": 1,
        "can_view_mj_prompt": 1,
        "can_view_command_center": 0,
        "daily_trend_limit": 20,
    },
    {
        "plan_code": "vip",
        "plan_name": "VIP",
        "monthly_price_usd": 99,
        "yearly_price_usd": 990,
        "can_view_listing_ai": 1,
        "can_view_mj_prompt": 1,
        "can_view_command_center": 1,
        "daily_trend_limit": 999,
    },
]

SUBS = [
    {"email": "demo_free@trendforge.ai", "plan_code": "free", "payment_provider": "none", "billing_cycle": "monthly", "subscription_status": "trial", "amount_usd": 0},
    {"email": "demo_pro@trendforge.ai", "plan_code": "pro", "payment_provider": "stripe", "billing_cycle": "monthly", "subscription_status": "active", "amount_usd": 39},
    {"email": "demo_vip@trendforge.ai", "plan_code": "vip", "payment_provider": "stripe", "billing_cycle": "monthly", "subscription_status": "active", "amount_usd": 99},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM billing_plans_v90")
    for p in PLANS:
        conn.execute(
            '''
            INSERT INTO billing_plans_v90
            (plan_code, plan_name, monthly_price_usd, yearly_price_usd,
             can_view_listing_ai, can_view_mj_prompt, can_view_command_center, daily_trend_limit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                p["plan_code"], p["plan_name"], p["monthly_price_usd"], p["yearly_price_usd"],
                p["can_view_listing_ai"], p["can_view_mj_prompt"], p["can_view_command_center"], p["daily_trend_limit"]
            )
        )

    conn.execute("DELETE FROM subscriptions_v90")
    today = datetime.date.today()
    for s in SUBS:
        user = conn.execute("SELECT id, email FROM users_v88 WHERE email = ?", (s["email"],)).fetchone()
        renew_at = today + datetime.timedelta(days=30)
        conn.execute(
            '''
            INSERT INTO subscriptions_v90
            (user_id, email, plan_code, payment_provider, billing_cycle, subscription_status, amount_usd, renew_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                user["id"] if user else None, s["email"], s["plan_code"], s["payment_provider"], s["billing_cycle"],
                s["subscription_status"], s["amount_usd"], renew_at.isoformat()
            )
        )

    conn.execute("DELETE FROM billing_dashboard_v90")
    rows = conn.execute(
        '''
        SELECT u.id AS user_id, u.email, u.username,
               s.plan_code, s.payment_provider, s.billing_cycle, s.subscription_status, s.amount_usd, s.renew_at,
               p.daily_trend_limit, p.can_view_listing_ai, p.can_view_mj_prompt, p.can_view_command_center
        FROM users_v88 u
        LEFT JOIN subscriptions_v90 s ON u.email = s.email
        LEFT JOIN billing_plans_v90 p ON s.plan_code = p.plan_code
        ORDER BY u.id ASC
        '''
    ).fetchall()

    inserted = 0
    for r in rows:
        conn.execute(
            '''
            INSERT INTO billing_dashboard_v90
            (user_id, email, username, current_plan, payment_provider, billing_cycle, subscription_status,
             amount_usd, renew_at, daily_trend_limit, can_view_listing_ai, can_view_mj_prompt, can_view_command_center)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                r["user_id"], r["email"], r["username"], r["plan_code"], r["payment_provider"], r["billing_cycle"],
                r["subscription_status"], r["amount_usd"] or 0, r["renew_at"], r["daily_trend_limit"] or 0,
                r["can_view_listing_ai"] or 0, r["can_view_mj_prompt"] or 0, r["can_view_command_center"] or 0
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] billing_system_v90 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
