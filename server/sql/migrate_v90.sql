-- TrendForge V90 Billing System
CREATE TABLE IF NOT EXISTS billing_plans_v90 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_code TEXT UNIQUE,
    plan_name TEXT,
    monthly_price_usd REAL DEFAULT 0,
    yearly_price_usd REAL DEFAULT 0,
    can_view_listing_ai INTEGER DEFAULT 0,
    can_view_mj_prompt INTEGER DEFAULT 0,
    can_view_command_center INTEGER DEFAULT 0,
    daily_trend_limit INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscriptions_v90 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT,
    plan_code TEXT,
    payment_provider TEXT,
    billing_cycle TEXT,
    subscription_status TEXT,
    amount_usd REAL DEFAULT 0,
    renew_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS billing_dashboard_v90 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT,
    username TEXT,
    current_plan TEXT,
    payment_provider TEXT,
    billing_cycle TEXT,
    subscription_status TEXT,
    amount_usd REAL DEFAULT 0,
    renew_at TEXT,
    daily_trend_limit INTEGER DEFAULT 0,
    can_view_listing_ai INTEGER DEFAULT 0,
    can_view_mj_prompt INTEGER DEFAULT 0,
    can_view_command_center INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_v90_status ON subscriptions_v90(subscription_status);
CREATE INDEX IF NOT EXISTS idx_billing_dashboard_v90_plan ON billing_dashboard_v90(current_plan);
