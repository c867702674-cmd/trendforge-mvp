
CREATE TABLE IF NOT EXISTS subscriptions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_email TEXT,
 plan TEXT,
 status TEXT,
 renew_date TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_email
ON subscriptions(user_email);
