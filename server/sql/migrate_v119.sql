CREATE TABLE IF NOT EXISTS billing_orders_v119 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    plan TEXT,
    price TEXT,
    status TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
