-- TrendForge V62 Publish Board Engine
CREATE TABLE IF NOT EXISTS publish_board_v62 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    publish_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_publish_v62_column
ON publish_board_v62(board_column);

CREATE INDEX IF NOT EXISTS idx_publish_v62_status
ON publish_board_v62(publish_status);

CREATE INDEX IF NOT EXISTS idx_publish_v62_rank
ON publish_board_v62(board_rank DESC);
