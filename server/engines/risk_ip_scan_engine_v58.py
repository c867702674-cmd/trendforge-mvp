#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TrendForge V58 Risk / IP Scan Engine
file: /root/trendforge-mvp/server/risk_ip_scan_engine_v58.py
"""

import json
import os
import re
import sqlite3
import unicodedata
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Tuple

BASE_DIR = "/root/trendforge-mvp/server"
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")
INPUT_JSON = os.path.join(BASE_DIR, "docs", "trend_expansion_v57.json")

RISK_TABLE = "risk_ip_scan_results_v58"


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_ascii(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_unicode_noise(text: str) -> bool:
    if not text:
        return False
    try:
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        # 如果原文和 ascii 清洗后差异很大，视为可能存在乱码/异常字符
        raw_letters = re.sub(r"\s+", "", text)
        ascii_letters = re.sub(r"\s+", "", ascii_text)
        if raw_letters and len(ascii_letters) / max(len(raw_letters), 1) < 0.75:
            return True
        if re.search(r"[^\x00-\x7F]", text):
            # 存在非ASCII并且不是正常大量中文场景（当前候选词本身主要应为英文）
            return True
    except Exception:
        return True
    return False


def safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def title_case_words(text: str) -> str:
    return " ".join(w.capitalize() for w in clean_spaces(text).split())


def extract_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    尽量兼容不同 JSON 结构
    """
    if isinstance(payload, list):
        return payload

    for key in ["items", "data", "results", "rows"]:
        val = payload.get(key)
        if isinstance(val, list):
            return val

    return []


EVENT_TERMS = {
    "olympics", "olympic", "paralympics", "paralympic",
    "world cup", "super bowl", "nba finals", "final four",
    "stanley cup", "wimbledon", "march madness",
    "uefa", "fifa", "nfl", "nba", "nhl", "mlb"
}

BRAND_IP_TERMS = {
    "disney", "pixar", "marvel", "dc", "star wars", "pokemon",
    "hello kitty", "sanrio", "harry potter", "hogwarts",
    "barbie", "nike", "adidas", "gucci", "louis vuitton",
    "tesla", "minecraft", "fortnite", "spongebob", "simpsons",
    "naruto", "one piece", "dragon ball", "jurassic park",
    "peppa pig", "mickey", "minnie", "batman", "superman",
    "spider-man", "spiderman", "avengers"
}

POLITICAL_SENSITIVE = {
    "trump", "biden", "putin", "xi jinping", "election",
    "maga", "democrat", "republican"
}

ADULT_VIOLENCE_SENSITIVE = {
    "nude", "sex", "xxx", "porn", "blood", "gore", "kill", "weapon"
}

GENERIC_REWRITE_MAP = {
    "olympics": "international sports",
    "olympic": "international sports",
    "paralympics": "adaptive sports",
    "paralympic": "adaptive sports",
    "world cup": "global football",
    "super bowl": "championship football",
    "nba": "pro basketball",
    "nfl": "pro football",
    "nhl": "pro hockey",
    "mlb": "pro baseball",
    "disney": "storybook",
    "marvel": "comic hero",
    "dc": "comic hero",
    "star wars": "space fantasy",
    "pokemon": "monster fantasy",
    "hello kitty": "cute cartoon cat",
    "sanrio": "cute cartoon style",
    "harry potter": "magic school fantasy",
    "hogwarts": "magic school fantasy",
    "barbie": "fashion doll style",
    "nike": "athletic style",
    "adidas": "sport style",
    "tesla": "electric car style",
    "minecraft": "blocky game style",
    "fortnite": "battle game style",
    "batman": "dark hero style",
    "superman": "heroic comic style",
    "spider-man": "web hero style",
    "spiderman": "web hero style",
    "avengers": "superhero team style",
}


def find_phrase_hits(text: str, phrase_set: set) -> List[str]:
    hits = []
    lower = f" {text.lower()} "
    for phrase in phrase_set:
        if f" {phrase} " in lower or phrase in lower:
            hits.append(phrase)
    return sorted(set(hits))


def build_flags(candidate_term: str) -> Tuple[List[str], int]:
    flags = []
    score = 0
    term_norm = normalize_ascii(candidate_term)

    event_hits = find_phrase_hits(term_norm, EVENT_TERMS)
    if event_hits:
        flags.append("event_term")
        score += 45

    brand_hits = find_phrase_hits(term_norm, BRAND_IP_TERMS)
    if brand_hits:
        flags.append("brand_ip_term")
        score += 55

    political_hits = find_phrase_hits(term_norm, POLITICAL_SENSITIVE)
    if political_hits:
        flags.append("political_sensitive")
        score += 40

    adult_hits = find_phrase_hits(term_norm, ADULT_VIOLENCE_SENSITIVE)
    if adult_hits:
        flags.append("adult_or_violence_sensitive")
        score += 50

    if has_unicode_noise(candidate_term):
        flags.append("unicode_noise")
        score += 30

    if re.search(r"[^A-Za-z0-9\s\-\&']", candidate_term or ""):
        # 非常规字符
        flags.append("special_characters")
        score += 10

    # 四位年份存在时，如果又叠加事件词，更值得警惕
    if re.search(r"\b20\d{2}\b", term_norm) and ("event_term" in flags or "brand_ip_term" in flags):
        flags.append("time_sensitive_named_event")
        score += 15

    # 过长一般需要复核
    if len(term_norm.split()) >= 8:
        flags.append("long_phrase_review")
        score += 10

    # 太短也可能不稳定
    if len(term_norm.split()) <= 1:
        flags.append("too_short_review")
        score += 8

    return sorted(set(flags)), score


def remove_sensitive_phrases(term: str) -> str:
    result = normalize_ascii(term)

    for src, dst in GENERIC_REWRITE_MAP.items():
        result = re.sub(rf"\b{re.escape(src)}\b", dst, result)

    # 去掉年份
    result = re.sub(r"\b20\d{2}\b", "", result)

    # 清掉一些容易重复的无意义连接
    result = re.sub(r"\b(the|official|licensed)\b", "", result)

    result = re.sub(r"\s+", " ", result).strip()

    # 再修一层，如果仍出现高风险词，直接清掉
    blocked_words = sorted(
        list(EVENT_TERMS | BRAND_IP_TERMS | POLITICAL_SENSITIVE | ADULT_VIOLENCE_SENSITIVE),
        key=lambda x: len(x),
        reverse=True
    )
    for bw in blocked_words:
        result = re.sub(rf"\b{re.escape(bw)}\b", "", result)

    result = re.sub(r"\s+", " ", result).strip(" -_")

    return clean_spaces(result)


def fallback_generic(term: str) -> str:
    norm = normalize_ascii(term)
    product_type = None
    for p in ["shirt", "hoodie", "sweatshirt", "mug", "poster", "tote", "sticker"]:
        if re.search(rf"\b{p}\b", norm):
            product_type = p
            break

    if "winter" in norm:
        base = "minimalist winter sports"
    elif "city" in norm or "michigan" in norm:
        base = "retro hometown pride"
    else:
        base = "minimalist inspirational"

    return f"{base} {product_type}".strip() if product_type else base


def make_safe_term(candidate_term: str, flags: List[str]) -> str:
    rewritten = remove_sensitive_phrases(candidate_term)
    if not rewritten or len(rewritten.split()) < 2:
        rewritten = fallback_generic(candidate_term)

    # 避免双空格
    rewritten = clean_spaces(rewritten)

    # 只保留合理字符
    rewritten = re.sub(r"[^a-z0-9\s\-]", " ", rewritten.lower())
    rewritten = clean_spaces(rewritten)

    if not rewritten:
        rewritten = "generic pod design"

    return rewritten


def decide_risk_level(flags: List[str], risk_score: int) -> str:
    if "brand_ip_term" in flags:
        return "BLOCK"
    if "adult_or_violence_sensitive" in flags:
        return "BLOCK"
    if "political_sensitive" in flags and risk_score >= 40:
        return "BLOCK"
    if "event_term" in flags and "time_sensitive_named_event" in flags:
        return "BLOCK"
    if risk_score >= 70:
        return "BLOCK"
    if risk_score >= 25:
        return "REVIEW"
    return "SAFE"


def connect_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def clear_old_rows(conn: sqlite3.Connection):
    conn.execute(f"DELETE FROM {RISK_TABLE}")
    conn.commit()


def insert_rows(conn: sqlite3.Connection, rows: List[Dict[str, Any]]):
    sql = f"""
    INSERT INTO {RISK_TABLE} (
        source_term,
        candidate_term,
        normalized_term,
        safe_term,
        rewrite_suggestion,
        risk_level,
        risk_score,
        flags_json,
        duplicate_group,
        source_type,
        source_score,
        source_payload_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    data = []
    for row in rows:
        data.append((
            row["source_term"],
            row["candidate_term"],
            row["normalized_term"],
            row["safe_term"],
            row["rewrite_suggestion"],
            row["risk_level"],
            row["risk_score"],
            safe_json_dumps(row["flags"]),
            row["duplicate_group"],
            row["source_type"],
            row["source_score"],
            safe_json_dumps(row["source_payload"]),
        ))
    conn.executemany(sql, data)
    conn.commit()


def main():
    payload = load_json(INPUT_JSON)
    items = extract_items(payload)

    if not items:
        raise RuntimeError("No items found in trend_expansion_v57.json")

    processed: List[Dict[str, Any]] = []

    # 先收集 normalized，做重复组
    normalized_list = []
    raw_candidates = []

    for item in items:
        source_term = (
            item.get("source_term")
            or item.get("parent_term")
            or item.get("term")
            or item.get("topic")
            or ""
        )
        candidate_term = (
            item.get("expanded_term")
            or item.get("candidate_term")
            or item.get("title")
            or item.get("keyword")
            or item.get("variant")
            or item.get("term")
            or ""
        )

        source_type = item.get("type") or item.get("expansion_type") or "unknown"
        source_score = item.get("score") or item.get("expansion_score") or 0

        source_term = clean_spaces(str(source_term))
        candidate_term = clean_spaces(str(candidate_term))

        if not candidate_term:
            continue

        normalized = normalize_ascii(candidate_term)
        normalized_list.append(normalized)
        raw_candidates.append({
            "source_term": source_term,
            "candidate_term": candidate_term,
            "normalized_term": normalized,
            "source_type": str(source_type),
            "source_score": float(source_score) if str(source_score).strip() else 0.0,
            "source_payload": item,
        })

    dup_counter = Counter(normalized_list)

    for row in raw_candidates:
        candidate_term = row["candidate_term"]
        normalized = row["normalized_term"]

        flags, risk_score = build_flags(candidate_term)
        risk_level = decide_risk_level(flags, risk_score)
        safe_term = make_safe_term(candidate_term, flags)

        duplicate_group = normalized if dup_counter[normalized] > 1 else ""

        # 重复项提高一个复核级别
        if duplicate_group:
            flags = sorted(set(flags + ["duplicate_candidate"]))
            risk_score += 8
            if risk_level == "SAFE":
                risk_level = "REVIEW"

        processed.append({
            "source_term": row["source_term"],
            "candidate_term": candidate_term,
            "normalized_term": normalized,
            "safe_term": safe_term,
            "rewrite_suggestion": safe_term,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "flags": flags,
            "duplicate_group": duplicate_group,
            "source_type": row["source_type"],
            "source_score": row["source_score"],
            "source_payload": row["source_payload"],
        })

    conn = connect_db(DB_PATH)
    try:
        clear_old_rows(conn)
        insert_rows(conn, processed)
    finally:
        conn.close()

    level_counter = Counter([x["risk_level"] for x in processed])

    print(
        f"[OK] risk_ip_scan_engine_v58 "
        f"inserted={len(processed)} "
        f"safe={level_counter.get('SAFE', 0)} "
        f"review={level_counter.get('REVIEW', 0)} "
        f"block={level_counter.get('BLOCK', 0)} "
        f"db={DB_PATH}"
    )


if __name__ == "__main__":
    main()