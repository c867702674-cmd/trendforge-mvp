import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def count_table(conn, table_name):
    try:
        row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return row[0] if row else 0
    except:
        return 0

def main():
    conn = sqlite3.connect(DB)

    blocks = [
        ("overview", "趋势数据", str(count_table(conn, "trend_data_v89")), "Google Trends / Etsy / Amazon 趋势入口", "ACTIVE", 1),
        ("overview", "Prompt能力", str(count_table(conn, "mj_prompt_v97")), "Midjourney Prompt 自动生成", "ACTIVE", 2),
        ("overview", "Mockup能力", str(count_table(conn, "mockup_pack_v98")), "Hero / Scene / White BG / Detail 模型包", "ACTIVE", 3),
        ("overview", "创意执行", str(count_table(conn, "creative_pack_v100")), "Creative Pack 商业执行包", "ACTIVE", 4),
        ("listing", "Listing草稿", str(count_table(conn, "listing_pack_v101")), "可直接上架使用的 Listing Pack", "ACTIVE", 5),
        ("listing", "发布准备", str(count_table(conn, "publish_pack_v102")), "Publish Pack 最终发布包", "ACTIVE", 6),
        ("ops", "发布队列", str(count_table(conn, "release_queue_v103")), "Release Queue 发布队列", "ACTIVE", 7),
        ("ops", "运营操作台", str(count_table(conn, "operator_console_v104")), "Operator Console 运营执行台", "ACTIVE", 8),
        ("saas", "用户系统", str(count_table(conn, "user_system_v88")), "Free / Pro / VIP 用户体系", "ACTIVE", 9),
        ("saas", "计费系统", str(count_table(conn, "billing_system_v90")), "订阅 / 套餐 / 支付通道", "ACTIVE", 10),
        ("automation", "自动化中心", str(count_table(conn, "automation_hub_v92")), "规则驱动自动化", "ACTIVE", 11),
        ("automation", "推送中心", str(count_table(conn, "push_center_v91")), "Feishu / Email 自动推送", "ACTIVE", 12),
    ]

    conn.execute("DELETE FROM home_portal_v106")

    for row in blocks:
        conn.execute(
            """
            INSERT INTO home_portal_v106
            (block_name, block_title, block_value, block_note, status, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            row
        )

    conn.commit()
    conn.close()
    print(f"[OK] home_portal_v106 inserted={len(blocks)} db={DB}")

if __name__ == '__main__':
    main()
