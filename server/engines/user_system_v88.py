#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, secrets, hashlib

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

SEED_USERS = [
    {"email": "demo_free@trendforge.ai", "username": "demo_free", "password": "TrendForge123", "plan_code": "free", "role_code": "seller"},
    {"email": "demo_pro@trendforge.ai", "username": "demo_pro", "password": "TrendForge123", "plan_code": "pro", "role_code": "seller"},
    {"email": "demo_vip@trendforge.ai", "username": "demo_vip", "password": "TrendForge123", "plan_code": "vip", "role_code": "seller"},
]

ACCESS_RULES = [
    {"plan_code": "free", "daily_trend_limit": 3, "can_view_listing_ai": 0, "can_view_mj_prompt": 0, "can_view_command_center": 0},
    {"plan_code": "pro", "daily_trend_limit": 20, "can_view_listing_ai": 1, "can_view_mj_prompt": 1, "can_view_command_center": 0},
    {"plan_code": "vip", "daily_trend_limit": 999, "can_view_listing_ai": 1, "can_view_mj_prompt": 1, "can_view_command_center": 1},
]

def sha256_text(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def token_for_user(email: str) -> str:
    prefix = email.split("@")[0].upper()
    return f"TF-{prefix}-{secrets.token_hex(8).upper()}"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM access_rules_v88")
    for rule in ACCESS_RULES:
        conn.execute(
            '''
            INSERT INTO access_rules_v88
            (plan_code, daily_trend_limit, can_view_listing_ai, can_view_mj_prompt, can_view_command_center)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                rule["plan_code"],
                rule["daily_trend_limit"],
                rule["can_view_listing_ai"],
                rule["can_view_mj_prompt"],
                rule["can_view_command_center"],
            ),
        )

    inserted_users = 0
    for user in SEED_USERS:
        email = user["email"]
        existed = conn.execute("SELECT id FROM users_v88 WHERE email = ?", (email,)).fetchone()
        if existed:
            conn.execute(
                '''
                UPDATE users_v88
                SET username = ?, password_hash = ?, plan_code = ?, role_code = ?, is_active = 1
                WHERE email = ?
                ''',
                (
                    user["username"],
                    sha256_text(user["password"]),
                    user["plan_code"],
                    user["role_code"],
                    email,
                ),
            )
        else:
            conn.execute(
                '''
                INSERT INTO users_v88
                (email, username, password_hash, plan_code, role_code, api_token, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                ''',
                (
                    email,
                    user["username"],
                    sha256_text(user["password"]),
                    user["plan_code"],
                    user["role_code"],
                    token_for_user(email),
                ),
            )
            inserted_users += 1

    conn.execute("DELETE FROM user_dashboard_v88")
    users = conn.execute("SELECT * FROM users_v88 ORDER BY id ASC").fetchall()
    for u in users:
        rule = conn.execute("SELECT * FROM access_rules_v88 WHERE plan_code = ?", (u["plan_code"],)).fetchone()
        status = "ACTIVE" if int(u["is_active"] or 0) == 1 else "DISABLED"
        conn.execute(
            '''
            INSERT INTO user_dashboard_v88
            (user_id, email, username, plan_code, role_code, api_token, daily_trend_limit,
             can_view_listing_ai, can_view_mj_prompt, can_view_command_center, account_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                u["id"], u["email"], u["username"], u["plan_code"], u["role_code"], u["api_token"],
                rule["daily_trend_limit"] if rule else 0,
                rule["can_view_listing_ai"] if rule else 0,
                rule["can_view_mj_prompt"] if rule else 0,
                rule["can_view_command_center"] if rule else 0,
                status,
            ),
        )

    total_dash = conn.execute("SELECT COUNT(*) AS c FROM user_dashboard_v88").fetchone()["c"]
    conn.commit()
    conn.close()
    print(f"[OK] user_system_v88 inserted_users={inserted_users} dashboard_rows={total_dash} db={DB_PATH}")

if __name__ == "__main__":
    main()
