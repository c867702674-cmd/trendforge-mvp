-- TrendForge V88 SaaS User System
CREATE TABLE IF NOT EXISTS users_v88 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    username TEXT,
    password_hash TEXT,
    plan_code TEXT DEFAULT 'free',
    role_code TEXT DEFAULT 'seller',
    api_token TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS access_rules_v88 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_code TEXT,
    daily_trend_limit INTEGER DEFAULT 0,
    can_view_listing_ai INTEGER DEFAULT 0,
    can_view_mj_prompt INTEGER DEFAULT 0,
    can_view_command_center INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_dashboard_v88 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT,
    username TEXT,
    plan_code TEXT,
    role_code TEXT,
    api_token TEXT,
    daily_trend_limit INTEGER DEFAULT 0,
    can_view_listing_ai INTEGER DEFAULT 0,
    can_view_mj_prompt INTEGER DEFAULT 0,
    can_view_command_center INTEGER DEFAULT 0,
    account_status TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_v88_plan ON users_v88(plan_code);
CREATE INDEX IF NOT EXISTS idx_user_dashboard_v88_plan ON user_dashboard_v88(plan_code);
