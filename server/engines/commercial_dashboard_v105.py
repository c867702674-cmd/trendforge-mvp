import sqlite3

DB='/root/trendforge-mvp/server/trendforge.db'

def count_table(conn, table_name):
    try:
        row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
        return row[0] if row else 0
    except:
        return 0

def main():
    conn = sqlite3.connect(DB)

    sections = [
        ("Trend Data Engine", str(count_table(conn, "trend_data_v89")), "Google Trends / Etsy / Amazon 数据入口", "ACTIVE"),
        ("MJ Prompt Engine", str(count_table(conn, "mj_prompt_v97")), "Midjourney Prompt 自动生成", "ACTIVE"),
        ("Mockup Pack Engine", str(count_table(conn, "mockup_pack_v98")), "Hero / Scene / White BG / Detail 模型包", "ACTIVE"),
        ("Image Brief Engine", str(count_table(conn, "image_brief_v99")), "出图执行 Brief", "ACTIVE"),
        ("Creative Pack Engine", str(count_table(conn, "creative_pack_v100")), "商业创意收口包", "ACTIVE"),
        ("Listing Pack Engine", str(count_table(conn, "listing_pack_v101")), "可上架 Listing 包", "ACTIVE"),
        ("Publish Pack Engine", str(count_table(conn, "publish_pack_v102")), "最终发布包", "ACTIVE"),
        ("Release Queue Engine", str(count_table(conn, "release_queue_v103")), "发布队列管理", "ACTIVE"),
        ("Operator Console", str(count_table(conn, "operator_console_v104")), "运营执行台", "ACTIVE"),
        ("Billing System", str(count_table(conn, "billing_system_v90")), "商业付费系统", "ACTIVE"),
        ("User System", str(count_table(conn, "user_system_v88")), "SaaS 用户体系", "ACTIVE"),
        ("Automation Hub", str(count_table(conn, "automation_hub_v92")), "自动化规则中心", "ACTIVE"),
    ]

    conn.execute("DELETE FROM commercial_dashboard_v105")

    for s in sections:
        conn.execute(
            """
            INSERT INTO commercial_dashboard_v105
            (section_name, section_value, section_note, status)
            VALUES (?, ?, ?, ?)
            """,
            s
        )

    conn.commit()
    conn.close()
    print(f"[OK] commercial_dashboard_v105 inserted={len(sections)} db={DB}")

if __name__ == '__main__':
    main()
