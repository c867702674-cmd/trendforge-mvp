#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

POD_KEYWORDS = [
    "tshirt", "t-shirt", "shirt", "hoodie", "sweatshirt",
    "mug", "sticker", "poster", "canvas", "print",
    "embroidery", "patch", "hat", "cap", "tote",
    "typography", "line art", "minimalist", "retro",
    "gift", "svg", "png", "design", "graphic",
    "pod",
]

# 明显不适合 POD 的噪声（运动队/比分/直播等）
BLOCK_PATTERNS = [
    r"\bvs\b",
    r"\bscore\b",
    r"\blive\b",
    r"\bhighlights\b",
    r"\bmatch\b",
    r"\bseason\b",
    r"\bwhere to watch\b",
]


def _contains_any(text: str, keywords) -> bool:
    t = (text or "").lower()
    return any(k in t for k in keywords)


def _blocked(text: str) -> bool:
    t = (text or "").lower()
    for p in BLOCK_PATTERNS:
        if re.search(p, t):
            return True
    return False


def filter_pod_trends(rows, sources_by_term=None):
    """
    rows: list[tuple|list] where first element is term
    sources_by_term: optional dict(term_lower -> sources_string). If term contains etsy source, we keep it.
    Return rows with original shape preserved.
    """
    out = []
    for r in rows:
        if not r:
            continue
        term = (r[0] or "").strip()
        if not term:
            continue

        t = term.lower()

        # 有 etsy 来源优先保留（如果 build 提供了 sources_by_term）
        if sources_by_term:
            s = (sources_by_term.get(t) or "")
            if "etsy:" in s:
                out.append(r)
                continue

        # 强噪声直接过滤
        if _blocked(term):
            # 但如果 term 里有明确 POD 产品词，则放行
            if _contains_any(term, POD_KEYWORDS):
                out.append(r)
            continue

        # 正向关键词命中放行
        if _contains_any(term, POD_KEYWORDS):
            out.append(r)
            continue

        # 默认：不过滤（你也可以改成默认过滤更严格）
        out.append(r)

    return out