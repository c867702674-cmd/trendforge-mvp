#!/usr/bin/env python3
import os, sqlite3, json, urllib.request, urllib.error
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")
DRY_RUN = str(os.getenv("FEISHU_DRY_RUN", "1")).strip() not in ("0", "false", "False")

WEBHOOKS = {
    "group_main": os.getenv("FEISHU_WEBHOOK_MAIN", "").strip(),
    "group_vip": os.getenv("FEISHU_WEBHOOK_VIP", "").strip(),
    "internal": os.getenv("FEISHU_WEBHOOK_INTERNAL", "").strip(),
}

def utc():
    return datetime.now(timezone.utc).isoformat()

def choose_webhook(audience):
    aud = str(audience or "")
    if aud == "group_vip":
        return WEBHOOKS["group_vip"]
    if aud == "internal":
        return WEBHOOKS["internal"]
    return WEBHOOKS["group_main"]

def send_text(webhook, title, body):
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"{title}\n{body}"
        }
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.getcode(), resp.read().decode("utf-8", errors="ignore")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT term, audience, title, body_json, priority_score
        FROM audience_routes
        ORDER BY priority_score DESC, id ASC
        LIMIT 120
        """
    ).fetchall()

    inserted = 0
    for r in rows:
        audience = str(r["audience"] or "")
        webhook = choose_webhook(audience)
        body_json = {}
        try:
            body_json = json.loads(r["body_json"] or "{}")
        except Exception:
            body_json = {}

        body = f"listing: {body_json.get('listing_title', '-')}"

        ok, status, resp_text = 1, 0, "dry_run"
        if not DRY_RUN and webhook:
            try:
                status, resp_text = send_text(webhook, r["title"] or "", body)
                ok = 1 if status == 200 else 0
            except urllib.error.HTTPError as e:
                ok = 0
                status = e.code
                resp_text = e.read().decode("utf-8", errors="ignore")
            except Exception as e:
                ok = 0
                status = 0
                resp_text = str(e)
        else:
            ok = 1
            status = 0
            if not webhook:
                resp_text = "no_webhook_configured"
            else:
                resp_text = "dry_run"

        conn.execute(
            """
            INSERT INTO feishu_push_results
            (term, audience, title, ok, dry_run, http_status, response_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["term"] or "",
                audience,
                r["title"] or "",
                ok,
                1 if DRY_RUN else 0,
                status,
                resp_text[:4000],
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] feishu_auto_push_v1 inserted={inserted} dry_run={1 if DRY_RUN else 0} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
