-- TrendForge V89 Trend Data Engine
CREATE TABLE IF NOT EXISTS trend_data_v89 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT,
    source_term TEXT,
    market_code TEXT DEFAULT 'US',
    product_type TEXT,
    trend_score REAL DEFAULT 0,
    growth_rate REAL DEFAULT 0,
    competition_level TEXT,
    action_level TEXT,
    source_url TEXT,
    payload_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_trend_data_v89_source ON trend_data_v89(source_name);
CREATE INDEX IF NOT EXISTS idx_trend_data_v89_score ON trend_data_v89(trend_score DESC);
