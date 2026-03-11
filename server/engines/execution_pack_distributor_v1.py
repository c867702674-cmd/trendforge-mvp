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
        SELECT c.term,
               c.opportunity_score,
               c.recommended_title,
               c.image_prompt,
               c.design_direction
        FROM opportunity_cards c
        ORDER BY c.opportunity_score DESC, c.id ASC
        LIMIT 100
        """
    ).fetchall()

    conn.execute("DELETE FROM execution_pack_distributions")
    inserted = 0

    for r in rows:
        term = str(r["term"] or "").strip()
        score = float(r["opportunity_score"] or 0)
        tasks = [
            "确认趋势相关性",
            "生成设计草图",
            "输出商品图",
            "生成Listing标题与描述",
            "上架并记录测试数据"
        ]
        payload = {
            "design_direction": r["design_direction"] or "",
            "source": "opportunity_cards"
        }

        conn.execute(
            """
            INSERT INTO execution_pack_distributions
            (term, pack_title, pack_score, task_list_json, listing_title, image_prompt, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term,
                f"Execution Pack · {term}",
                score,
                json.dumps(tasks, ensure_ascii=False),
                r["recommended_title"] or "",
                r["image_prompt"] or "",
                json.dumps(payload, ensure_ascii=False),
                utc()
            )
        )
        inserted += 1

    conn.commit()
    print(f"[OK] execution_pack_distributor_v1 inserted={inserted} db={DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
