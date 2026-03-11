#!/usr/bin/env python3
import os, sqlite3, json
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def utc():
    return datetime.now(timezone.utc).isoformat()

def route_names(audience):
    aud = str(audience or "")
    routes = []
    if "group_main" in aud:
        routes.append(("main_public", "group_main"))
    if "group_vip" in aud:
        routes.append(("vip_private", "group_vip"))
    routes.append(("internal_review", "internal"))
    return routes

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, priority_score, audience, title, body_json, payload_json
        FROM push_ready_payloads
        ORDER BY priority_score DESC, id ASC
        LIMIT 100
        """
    ).fetchall()

    conn.execute("DELETE FROM audience_routes")
    inserted = 0

    for r in rows:
        for route_name, audience in route_names(r["audience"]):
            conn.execute(
                """
                INSERT INTO audience_routes
                (term, route_name, audience, priority_score, title, body_json, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["term"] or "",
                    route_name,
                    audience,
                    float(r["priority_score"] or 0),
                    r["title"] or "",
                    r["body_json"] or "{}",
                    r["payload_json"] or "{}",
                    utc()
                )
            )
            inserted += 1

    conn.commit()
    print(f"[OK] audience_routing_center_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
