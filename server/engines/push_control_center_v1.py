#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT audience, ok, dry_run, http_status, response_text
        FROM feishu_push_results
        ORDER BY id DESC
        LIMIT 300
        """
    ).fetchall()

    total = len(rows)
    ok_count = sum(1 for r in rows if int(r["ok"] or 0) == 1)
    dry_count = sum(1 for r in rows if int(r["dry_run"] or 0) == 1)
    fail_count = total - ok_count

    by_audience = {}
    by_status = {}

    for r in rows:
        aud = str(r["audience"] or "unknown")
        by_audience[aud] = by_audience.get(aud, 0) + 1
        st = str(r["http_status"] or 0)
        by_status[st] = by_status.get(st, 0) + 1

    payload = {
        "generated_at": utc(),
        "summary": {
            "total": total,
            "ok": ok_count,
            "dry_run": dry_count,
            "failed": fail_count
        },
        "by_audience": by_audience,
        "by_status": by_status,
        "recent": [dict(r) for r in rows[:50]]
    }

    conn.execute("DELETE FROM push_control_snapshots")
    conn.execute(
        "INSERT INTO push_control_snapshots (snapshot_name, payload_json, created_at) VALUES (?, ?, ?)",
        ("latest", json.dumps(payload, ensure_ascii=False), utc())
    )
    conn.commit()
    print(f"[OK] push_control_center_v1 wrote snapshot db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
