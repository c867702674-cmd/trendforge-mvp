import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def stage_from_queue(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "READY_PUSH"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "ASSET_CHECK"
    return "MANUAL_REVIEW"

def advice_from_queue(queue_name, product_type):
    if queue_name == "READY_TO_RELEASE":
        return f"{product_type} can move into final publish after operator QA"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return f"{product_type} needs final asset/mockup review before publish"
    return f"{product_type} requires manual operator review"

def blocker_from_queue(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "none"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "asset review pending"
    return "manual verification pending"

def exec_action(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "Run final QA -> confirm listing -> push live"
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "Finish asset review -> approve mockup -> move to release"
    return "Manual inspection -> approve or reject"

def final_note(queue_name):
    if queue_name == "READY_TO_RELEASE":
        return "This item is near-commercial-ready."
    if queue_name == "ASSET_REVIEW_QUEUE":
        return "This item is waiting for asset completion before commercial release."
    return "This item is held for manual review."

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, queue_name, operator_owner, status FROM release_queue_v103"
    ).fetchall()

    inserted = 0

    for r in rows:
        stage_name = stage_from_queue(r["queue_name"])
        action_advice = advice_from_queue(r["queue_name"], r["product_type"])
        blocker_reason = blocker_from_queue(r["queue_name"])
        owner = r["operator_owner"]
        executable_action = exec_action(r["queue_name"])
        note = final_note(r["queue_name"])

        conn.execute(
            """
            INSERT INTO operator_console_v104
            (queue_id, source_term, product_type, stage_name, action_advice, blocker_reason, owner, executable_action, final_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                r["product_type"],
                stage_name,
                action_advice,
                blocker_reason,
                owner,
                executable_action,
                note,
                r["status"]
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] operator_console_v104 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
