
#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DOCS_DIR = "/root/trendforge-mvp/server/docs"

def utc():
    return datetime.now(timezone.utc).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    src = os.path.join(DOCS_DIR, "seller_dashboard_v28_api.json")
    payload = {}
    if os.path.exists(src):
        with open(src, "r", encoding="utf-8") as f:
            try:
                payload = json.load(f)
            except Exception:
                payload = {}

    conn.execute("DELETE FROM web_dashboard_bundles")
    conn.execute(
        "INSERT INTO web_dashboard_bundles (bundle_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("seller_dashboard_v29", json.dumps(payload, ensure_ascii=False), utc())
    )

    conn.commit()
    print(f"[OK] web_dashboard_bundle_engine_v1 wrote bundle db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
