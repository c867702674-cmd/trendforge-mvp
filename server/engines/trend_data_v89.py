#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sqlite3, json, math

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
TABLE_OUT = "trend_data_v89"

GOOGLE_TRENDS_SEED = [
    {"term":"minimalist cat poster", "product_type":"poster", "base":88, "growth":42},
    {"term":"nurse coffee mug", "product_type":"mug", "base":91, "growth":55},
    {"term":"retro golf typography shirt", "product_type":"shirt", "base":93, "growth":58},
    {"term":"teacher tote bag poster", "product_type":"poster", "base":79, "growth":28},
    {"term":"western cowgirl mug", "product_type":"mug", "base":86, "growth":39},
]

ETSY_TRENDING_SEED = [
    {"term":"gift migxsaf nurse graphic crewneck mug", "product_type":"mug", "sales":320, "price":19.99},
    {"term":"retro dazzlewall 3pcs minimalist line poster", "product_type":"poster", "sales":180, "price":14.99},
    {"term":"minimalist retro golf typography shirt", "product_type":"shirt", "sales":410, "price":24.99},
    {"term":"teacher tote bag printable wall art", "product_type":"poster", "sales":135, "price":12.99},
    {"term":"cowgirl western mug gift", "product_type":"mug", "sales":290, "price":18.99},
]

AMAZON_MOVERS_SEED = [
    {"term":"nurse tumbler gift", "product_type":"mug", "rank_jump":64},
    {"term":"retro golf shirt", "product_type":"shirt", "rank_jump":72},
    {"term":"minimalist line art wall decor", "product_type":"poster", "rank_jump":51},
]

def competition_level(score: float) -> str:
    if score >= 92:
        return "high"
    if score >= 82:
        return "medium"
    return "low"

def action_level(score: float, growth: float, comp: str) -> str:
    if score >= 90 and growth >= 40:
        return "DO_NOW"
    if score >= 80:
        return "WATCH"
    return "IGNORE"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(f"DELETE FROM {TABLE_OUT}")
    inserted = 0

    for row in GOOGLE_TRENDS_SEED:
        score = float(row["base"])
        growth = float(row["growth"])
        comp = competition_level(score)
        action = action_level(score, growth, comp)
        payload = {
            "source":"google_trends_seed",
            "interest_over_time":"simulated",
            "notes":"replace with pytrends in production"
        }
        conn.execute(f'''
            INSERT INTO {TABLE_OUT}
            (source_name, source_term, market_code, product_type, trend_score, growth_rate,
             competition_level, action_level, source_url, payload_json)
            VALUES (?, ?, 'US', ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "google_trends", row["term"], row["product_type"], score, growth,
            comp, action,
            f"https://trends.google.com/trends/explore?q={row['term'].replace(' ', '%20')}",
            json.dumps(payload, ensure_ascii=False)
        ))
        inserted += 1

    for row in ETSY_TRENDING_SEED:
        score = min(95.0, 60 + math.log(max(row["sales"],1), 1.5))
        growth = min(60.0, row["sales"] / 8)
        comp = competition_level(score)
        action = action_level(score, growth, comp)
        payload = {
            "source":"etsy_seed",
            "sales":row["sales"],
            "price":row["price"],
            "notes":"replace with Etsy API/listing scrape in production"
        }
        conn.execute(f'''
            INSERT INTO {TABLE_OUT}
            (source_name, source_term, market_code, product_type, trend_score, growth_rate,
             competition_level, action_level, source_url, payload_json)
            VALUES (?, ?, 'US', ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "etsy_trending", row["term"], row["product_type"], round(score, 2), round(growth, 2),
            comp, action,
            f"https://www.etsy.com/search?q={row['term'].replace(' ', '%20')}",
            json.dumps(payload, ensure_ascii=False)
        ))
        inserted += 1

    for row in AMAZON_MOVERS_SEED:
        score = min(94.0, 65 + row["rank_jump"] * 0.35)
        growth = min(55.0, row["rank_jump"] * 0.6)
        comp = competition_level(score)
        action = action_level(score, growth, comp)
        payload = {
            "source":"amazon_movers_seed",
            "rank_jump":row["rank_jump"],
            "notes":"replace with real movers data in production"
        }
        conn.execute(f'''
            INSERT INTO {TABLE_OUT}
            (source_name, source_term, market_code, product_type, trend_score, growth_rate,
             competition_level, action_level, source_url, payload_json)
            VALUES (?, ?, 'US', ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "amazon_movers", row["term"], row["product_type"], round(score, 2), round(growth, 2),
            comp, action,
            "https://www.amazon.com/gp/movers-and-shakers",
            json.dumps(payload, ensure_ascii=False)
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] trend_data_v89 inserted={inserted} db={DB_PATH}")

if __name__ == "__main__":
    main()
