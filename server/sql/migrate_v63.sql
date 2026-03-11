-- TrendForge V63 Ops Dashboard Engine
CREATE TABLE IF NOT EXISTS ops_dashboard_v63 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publish_board_id INTEGER,
    launch_queue_id INTEGER,
    execution_pack_id INTEGER,
    listing_id INTEGER,
    source_term TEXT,
    safe_term TEXT,
    risk_level TEXT,
    product_type TEXT,
    title_en TEXT,
    sku_code TEXT,
    priority_tier TEXT,
    schedule_bucket TEXT,
    publish_status TEXT,
    board_column TEXT,
    board_rank REAL DEFAULT 0,
    ops_stage TEXT,
    action_hint TEXT,
    dashboard_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ops_v63_stage
ON ops_dashboard_v63(ops_stage);

CREATE INDEX IF NOT EXISTS idx_ops_v63_product
ON ops_dashboard_v63(product_type);

CREATE INDEX IF NOT EXISTS idx_ops_v63_score
ON ops_dashboard_v63(dashboard_score DESC);
