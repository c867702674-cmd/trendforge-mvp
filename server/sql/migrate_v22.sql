
-- TrendForge V22 schema additions
CREATE TABLE IF NOT EXISTS global_trend_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    source TEXT,
    term TEXT,
    score REAL,
    meta_json TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_global_signals_term ON global_trend_signals(term);
