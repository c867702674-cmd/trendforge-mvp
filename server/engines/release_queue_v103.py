import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def decide_queue(product_type):
    if product_type == "poster":
        return "ASSET_REVIEW_QUEUE"
    if product_type == "mug":
        return "READY_TO_RELEASE"
    if product_type == "shirt":
        return "READY_TO_RELEASE"
    return "MANUAL_QUEUE"

def decide_priority(product_type):
    if product_type == "mug":
        return "P0"
    if product_type == "shirt":
        return "P0"
    if product_type == "poster":
        return "P1"
    return "P2"

def decide_next_step(product_type):
    if product_type == "poster":
        return "Complete final poster asset/mockup review, then move into release"
    if product_type == "mug":
        return "Operator final QA, then publish now"
    if product_type == "shirt":
        return "Operator final QA, then publish now"
    return "Manual operator review"

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, source_term, product_type, publish_title FROM publish_pack_v102"
    ).fetchall()

    inserted = 0

    for r in rows:
        queue_name = decide_queue(r["product_type"])
        priority = decide_priority(r["product_type"])
        risk_level = "SAFE"
        release_note = f"{r['publish_title']} entered {queue_name}"
        next_step = decide_next_step(r["product_type"])
        operator_owner = "operator"
        status = "READY" if queue_name == "READY_TO_RELEASE" else "WAITING"

        conn.execute(
            """
            INSERT INTO release_queue_v103
            (publish_id, source_term, product_type, queue_name, priority, risk_level, release_note, next_step, operator_owner, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["id"],
                r["source_term"],
                r["product_type"],
                queue_name,
                priority,
                risk_level,
                release_note,
                next_step,
                operator_owner,
                status
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] release_queue_v103 inserted={inserted} db={DB}")

if __name__ == '__main__':
    main()
