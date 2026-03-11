CREATE TABLE IF NOT EXISTS operator_console_v104 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
queue_id INTEGER,
source_term TEXT,
product_type TEXT,
stage_name TEXT,
action_advice TEXT,
blocker_reason TEXT,
owner TEXT,
executable_action TEXT,
final_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
