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

    trend_count = count_table(conn, "trend_data_v89")
    prompt_count = count_table(conn, "mj_prompt_v97")
    mockup_count = count_table(conn, "mockup_pack_v98")
    listing_count = count_table(conn, "listing_pack_v101")
    publish_count = count_table(conn, "publish_pack_v102")
    user_count = count_table(conn, "user_system_v88")

    rows = [
        ("hero", "北美 POD 趋势商业引擎", str(trend_count), "把趋势、Prompt、Mockup、Listing、发布收口为一套真正可执行的商业闭环。", "ACTIVE", 1),
        ("metric", "趋势数据", str(trend_count), "Google Trends / Etsy / Amazon 多源趋势入口", "ACTIVE", 2),
        ("metric", "Prompt能力", str(prompt_count), "Midjourney Prompt 自动生成", "ACTIVE", 3),
        ("metric", "Mockup能力", str(mockup_count), "Hero / Scene / White BG / Detail 模型包", "ACTIVE", 4),
        ("metric", "Listing草稿", str(listing_count), "自动生成可上架 Listing 包", "ACTIVE", 5),
        ("metric", "发布包", str(publish_count), "发布前最终收口 Publish Pack", "ACTIVE", 6),
        ("feature", "DO_NOW 趋势发现", "实时发现", "为中国 POD 卖家快速发现北美市场值得立刻执行的主题词与产品方向。", "ACTIVE", 7),
        ("feature", "AI 创意执行", "自动生成", "自动产出 Prompt、Mockup 思路、出图 Brief、Creative Pack。", "ACTIVE", 8),
        ("feature", "商品上架链路", "直接收口", "从趋势到 Listing、再到 Publish Queue 与 Operator Console，形成完整执行路径。", "ACTIVE", 9),
        ("feature", "SaaS 商业化能力", str(user_count), "包含用户系统、权限、套餐、订阅与自动化推送能力。", "ACTIVE", 10),
        ("plan", "Free", "$0", "适合体验版用户：少量趋势查看。", "ACTIVE", 11),
        ("plan", "Pro", "$39/mo", "适合个人卖家：趋势 + Prompt + Mockup + Listing。", "ACTIVE", 12),
        ("plan", "VIP", "$99/mo", "适合重度卖家/团队：完整商业链路 + Command Center。", "ACTIVE", 13),
        ("cta", "立即开始", "TrendForge 商业版", "下一步建议：把本页替换为正式首页入口，并接入登录/套餐跳转。", "ACTIVE", 14),
    ]

    conn.execute("DELETE FROM homepage_v107")

    for row in rows:
        conn.execute(
            """
            INSERT INTO homepage_v107
            (section_key, section_title, section_value, section_desc, status, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            row
        )

    conn.commit()
    conn.close()
    print(f"[OK] homepage_v107 inserted={len(rows)} db={DB}")

if __name__ == "__main__":
    main()
