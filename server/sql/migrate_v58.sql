-- TrendForge V58 Risk / IP Scan Engine
-- file: /root/trendforge-mvp/server/sql/migrate_v58.sql

CREATE TABLE IF NOT EXISTS risk_ip_scan_results_v58 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_term TEXT,
    candidate_term TEXT,
    normalized_term TEXT,
    safe_term TEXT,
    rewrite_suggestion TEXT,
    risk_level TEXT,              -- SAFE / REVIEW / BLOCK
    risk_score INTEGER DEFAULT 0,
    flags_json TEXT,
    duplicate_group TEXT,
    source_type TEXT,
    source_score REAL DEFAULT 0,
    source_payload_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_v58_source_term
ON risk_ip_scan_results_v58(source_term);

CREATE INDEX IF NOT EXISTS idx_risk_v58_candidate_term
ON risk_ip_scan_results_v58(candidate_term);

CREATE INDEX IF NOT EXISTS idx_risk_v58_risk_level
ON risk_ip_scan_results_v58(risk_level);

CREATE INDEX IF NOT EXISTS idx_risk_v58_normalized
ON risk_ip_scan_results_v58(normalized_term);

CREATE INDEX IF NOT EXISTS idx_risk_v58_duplicate_group
ON risk_ip_scan_results_v58(duplicate_group);