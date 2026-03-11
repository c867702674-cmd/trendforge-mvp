#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""TrendForge - POD Trend Filter V2
--------------------------------
Purpose:
  Decide whether a term is likely POD-designable (safe/printable) vs. noise (sports/news/live scores/etc).

Notes:
  - Lightweight heuristic filter (no external APIs).
  - Goal: reduce obvious non-POD terms before expansion/push.

Env (optional):
  POD_FILTER_MODE = 'strict' (default) or 'loose'
"""

import os
import re
from typing import Tuple, List

MODE = os.getenv("POD_FILTER_MODE", "strict").strip().lower()

# Hard blocks: news/sports/live events/queries
BLOCK_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bvs\b", re.I),
    re.compile(r"\bwhere to watch\b", re.I),
    re.compile(r"\bwatch\b", re.I),
    re.compile(r"\blive\b", re.I),
    re.compile(r"\bscore\b", re.I),
    re.compile(r"\bhighlights?\b", re.I),
    re.compile(r"\bmatch\b", re.I),
    re.compile(r"\bgame\b", re.I),
    re.compile(r"\bnba\b|\bnfl\b|\bmlb\b|\bnhl\b|\buefa\b|\bfifa\b", re.I),
    re.compile(r"\bforecast\b|\bweather\b|\bstorm\b|\bhurricane\b|\bsnow\b", re.I),
    re.compile(r"\belection\b|\bpolitic(s|al)?\b|\bwar\b|\bconflict\b", re.I),
    re.compile(r"\btickets?\b|\bconcert\b|\btour\b", re.I),
    re.compile(r"\binterview\b|\bbreaking\b|\bnews\b", re.I),
]

# Allow signals: print/design-friendly terms
ALLOW_KEYWORDS = [
    "shirt","tshirt","hoodie","sweatshirt","crewneck",
    "mug","sticker","poster","svg","graphic","gift",
    "retro","vintage","line art","minimalist","aesthetic",
    "cute","funny","cat","dog","mom","dad","teacher","nurse",
    "valentine","christmas","halloween","easter","birthday",
    "cowboy","boho","sunset","flower","skull","dragon","bee",
]

MIN_LEN = 3

def normalize(s: str) -> str:
    return " ".join((s or "").strip().split())

def is_pod_term(term: str) -> Tuple[bool, str]:
    t = normalize(term)
    if len(t) < MIN_LEN:
        return False, "too_short"

    for p in BLOCK_PATTERNS:
        if p.search(t):
            return False, f"blocked:{p.pattern}"

    if MODE == "loose":
        return True, "loose_pass"

    tl = t.lower()
    allow_hit = any(k in tl for k in ALLOW_KEYWORDS)
    if allow_hit:
        return True, "allow_keyword"

    # heuristic: printable phrases 2-6 words, letters/spaces mostly
    if re.fullmatch(r"[a-z0-9\s'&-]+", tl) and 2 <= len(t.split()) <= 6:
        return True, "heuristic_phrase"

    return False, "no_pod_signal"

if __name__ == "__main__":
    samples = [
        "st louis blues",
        "where to watch club america vs fc juarez",
        "minimalist line art cat",
        "retro golf typography",
        "weather forecast snow storm",
    ]
    for s in samples:
        ok, reason = is_pod_term(s)
        print(f"{ok}\t{reason}\t{s}")
