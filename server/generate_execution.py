#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendForge D8-A: Generate execution_pack_json (multi-SKU execution pack) for trends.

Usage examples:
  python3 server/generate_execution_pack.py --limit 20 --sku-count 8 --do-now-only 1
  python3 server/generate_execution_pack.py --id 123 --sku-count 8 --force 1
  python3 server/generate_execution_pack.py --dry-run 1

Notes:
- Default provider is MOCK (no external API required), to verify the pipeline end-to-end.
- If you already have an existing LLM call in your project, adapt `call_llm()` below to reuse it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Config
# -----------------------------
DEFAULT_DB_PATH = "/root/trendforge-mvp/server/trendforge.db"

SKU_ANGLES_DEFAULT = [
    "Humor",
    "Gift",
    "Identity",
    "Vintage",
    "Minimal Typography",
    "Bold Graphic",
    "Seasonal",
    "Sarcastic",
]


# -----------------------------
# Helpers
# -----------------------------
def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def extract_json(text: str) -> Dict[str, Any]:
    """
    Tolerant JSON extraction:
    - If the response contains extra text, grab the first {...} block.
    """
    text = (text or "").strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("LLM output does not contain a JSON object.")
    return json.loads(m.group(0))


def build_prompt(term: str, country: str, category: str, angles: List[str]) -> str:
    angles_str = ", ".join(angles)
    sku_n = len(angles)

    return f"""
You are a senior Amazon US POD listing expert.

Given the trend keyword:
- Term: {term}
- Country: {country}
- Category: {category}

Generate an EXECUTION PACK containing {sku_n} SKU variants.

Rules:
1. Each SKU must represent a DIFFERENT angle from this list:
   {angles_str}
2. Each SKU must include:
   - sku_id (snake_case, unique)
   - angle (must be one of the angles above)
   - target_audience (short string)
   - title (Amazon style, max 180 chars)
   - bullets (exactly 5 items)
   - backend_keywords (list of strings, 8-20 items)
   - design_prompt (for Midjourney or similar)
   - style (short string)
   - confidence (0.0-1.0 float)
3. Titles and bullets must be optimized for Amazon US.
4. Output MUST be valid JSON ONLY. No markdown. No extra text.
5. Do NOT repeat titles across SKUs.

Return JSON in this structure:
{{
  "summary": {{
    "total_skus": {sku_n},
    "recommended_platforms": ["Amazon","Etsy"],
    "best_angles": ["Humor","Gift","Identity"]
  }},
  "sku_variants": [
    {{
      "sku_id": "example_01",
      "angle": "Humor",
      "target_audience": "Cat Dad",
      "title": "Example title",
      "bullets": ["...","...","...","...","..."],
      "backend_keywords": ["..."],
      "design_prompt": "....",
      "style": "Bold Graphic",
      "confidence": 0.82
    }}
  ]
}}
""".strip()


def validate_pack(pack: Dict[str, Any], angles: List[str]) -> Dict[str, Any]:
    if not isinstance(pack, dict):
        raise ValueError("Pack must be a JSON object")

    variants = pack.get("sku_variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("Pack missing sku_variants list")

    # Require at least the number of angles (strict)
    if len(variants) < len(angles):
        raise ValueError(f"sku_variants count {len(variants)} < required {len(angles)}")

    seen_titles = set()
    seen_sku = set()

    for v in variants[: len(angles)]:
        if not isinstance(v, dict):
            raise ValueError("Each sku_variant must be an object")

        angle = v.get("angle")
        if angle not in angles:
            raise ValueError(f"Invalid angle: {angle}")

        sku_id = (v.get("sku_id") or "").strip()
        if not sku_id:
            raise ValueError("Missing sku_id")
        if sku_id in seen_sku:
            raise ValueError(f"Duplicate sku_id: {sku_id}")
        seen_sku.add(sku_id)

        title = (v.get("title") or "").strip()
        if not title:
            raise ValueError("Missing title")
        if title in seen_titles:
            raise ValueError(f"Duplicate title: {title}")
        seen_titles.add(title)

        bullets = v.get("bullets")
        if not isinstance(bullets, list) or len(bullets) != 5:
            raise ValueError("bullets must be a list of exactly 5 items")

        bk = v.get("backend_keywords")
        if not isinstance(bk, list) or len(bk) < 5:
            raise ValueError("backend_keywords must be a list with >= 5 items")

        conf = v.get("confidence")
        if conf is None or not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            raise ValueError("confidence must be a number between 0 and 1")

    pack.setdefault("summary", {})
    return pack


# -----------------------------
# Provider (MOCK default)
# -----------------------------
@dataclass
class LLMResult:
    text: str


def call_llm(prompt: str, provider: str = "mock") -> LLMResult:
    """
    Provider options:
    - mock: no external dependency. Good for pipeline validation.
    - custom: try to reuse your existing project LLM function if present.
              You can modify this block to call your existing generator.
    """
    provider = (provider or "mock").lower()

    if provider == "mock":
        # Produce deterministic mock pack (8 SKUs) for end-to-end verification
        skus = []
        for i, angle in enumerate(SKU_ANGLES_DEFAULT, start=1):
            skus.append(
                {
                    "sku_id": f"mock_{angle.lower().replace(' ', '_')}_{i:02d}",
                    "angle": angle,
                    "target_audience": "General",
                    "title": f"Mock Title - {angle}",
                    "bullets": [
                        "Bullet 1",
                        "Bullet 2",
                        "Bullet 3",
                        "Bullet 4",
                        "Bullet 5",
                    ],
                    "backend_keywords": ["mock", "keyword", "pod", "shirt", "tee", angle.lower()],
                    "design_prompt": f"Simple {angle} design prompt, clean POD style",
                    "style": angle,
                    "confidence": round(0.55 + (i * 0.03), 2),
                }
            )

        mock = {
            "summary": {
                "total_skus": len(skus),
                "recommended_platforms": ["Amazon", "Etsy"],
                "best_angles": ["Humor", "Gift", "Identity"],
            },
            "sku_variants": skus,
        }
        return LLMResult(text=json_dumps(mock))

    if provider == "custom":
        # Try to import an existing LLM helper from your codebase.
        # If you have something like `server/ai.py` or `server/llm.py`,
        # change the import here to match.
        try:
            # Example:
            # from server.ai import call_text_model
            # text = call_text_model(prompt)
            # return LLMResult(text=text)

            raise ImportError("No custom LLM wiring configured.")
        except Exception as e:
            raise RuntimeError(
                "Provider=custom failed. Please wire your project's LLM call in call_llm(). "
                f"Underlying error: {e}"
            )

    raise ValueError(f"Unknown provider: {provider}")


# -----------------------------
# Core generation
# -----------------------------
def generate_pack_for_trend(
    trend_id: int,
    term: str,
    country: str,
    category: str,
    sku_count: int,
    provider: str,
) -> Dict[str, Any]:
    angles = SKU_ANGLES_DEFAULT[: max(1, min(sku_count, len(SKU_ANGLES_DEFAULT)))]
    prompt = build_prompt(term=term, country=country, category=category, angles=angles)

    llm_res = call_llm(prompt, provider=provider)
    pack_raw = extract_json(llm_res.text)
    pack_raw = validate_pack(pack_raw, angles)

    # Normalize output for DB stability
    variants = pack_raw["sku_variants"][: len(angles)]
    out = {
        "trend_id": trend_id,
        "term": term,
        "country": country,
        "category": category,
        "generated_at": utc_iso(),
        "summary": pack_raw.get("summary", {}),
        "sku_variants": variants,
    }
    out["summary"].setdefault("total_skus", len(variants))
    return out


# -----------------------------
# DB functions
# -----------------------------
def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_columns_exist(conn: sqlite3.Connection) -> None:
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(trends)").fetchall()]
    required = ["execution_pack_json", "execution_pack_generated_at"]
    missing = [c for c in required if c not in cols]
    if missing:
        raise RuntimeError(
            "Missing required columns in trends table: "
            + ", ".join(missing)
            + "\nPlease run SQLite ALTER TABLE to add them."
        )


def select_candidates(
    conn: sqlite3.Connection,
    *,
    limit: int,
    do_now_only: bool,
    force: bool,
    trend_id: Optional[int],
) -> List[sqlite3.Row]:
    where = []
    params: List[Any] = []

    if trend_id is not None:
        where.append("id = ?")
        params.append(trend_id)
    else:
        if do_now_only:
            where.append("action_level = ?")
            params.append("DO_NOW")

        if not force:
            where.append("(execution_pack_json IS NULL OR execution_pack_json = '')")

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT id, term, country, category, action_level, execution_pack_json
        FROM trends
        {where_sql}
        ORDER BY id DESC
        LIMIT ?
    """.strip()
    params.append(limit)
    return conn.execute(sql, tuple(params)).fetchall()


def update_pack(
    conn: sqlite3.Connection,
    *,
    trend_id: int,
    pack: Dict[str, Any],
    generated_at: str,
    dry_run: bool,
) -> None:
    if dry_run:
        return
    conn.execute(
        "UPDATE trends SET execution_pack_json = ?, execution_pack_generated_at = ? WHERE id = ?",
        (json_dumps(pack), generated_at, trend_id),
    )


# -----------------------------
# CLI
# -----------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", default=os.getenv("TRENDFORGE_DB_PATH", DEFAULT_DB_PATH))
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--sku-count", type=int, default=8)
    p.add_argument("--do-now-only", type=int, default=1, help="1=true, 0=false")
    p.add_argument("--force", type=int, default=0, help="1=overwrite existing pack")
    p.add_argument("--dry-run", type=int, default=0, help="1=do not write DB")
    p.add_argument("--id", type=int, default=None, help="Generate for a single trend id")
    p.add_argument("--provider", default="mock", help="mock | custom")
    p.add_argument("--sleep-ms", type=int, default=0, help="sleep between generations")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    db_path: str = args.db_path
    limit: int = max(1, args.limit)
    sku_count: int = max(1, min(args.sku_count, 12))
    do_now_only: bool = bool(args.do_now_only)
    force: bool = bool(args.force)
    dry_run: bool = bool(args.dry_run)
    trend_id: Optional[int] = args.id
    provider: str = args.provider
    sleep_ms: int = max(0, args.sleep_ms)

    if not os.path.exists(db_path):
        print(f"[ERROR] DB not found: {db_path}")
        return 2

    conn = get_conn(db_path)
    try:
        ensure_columns_exist(conn)
        rows = select_candidates(
            conn,
            limit=limit,
            do_now_only=do_now_only,
            force=force,
            trend_id=trend_id,
        )

        print(
            f"[INFO] candidates={len(rows)} limit={limit} sku_count={sku_count} "
            f"do_now_only={do_now_only} force={force} dry_run={dry_run} provider={provider}"
        )

        generated = 0
        skipped = 0
        errors = 0

        for r in rows:
            tid = int(r["id"])
            term = r["term"]
            country = r["country"]
            category = r["category"]
            action_level = r["action_level"]

            existing = r["execution_pack_json"]
            if existing and not force:
                skipped += 1
                print(f"[SKIP] id={tid} action_level={action_level} reason=pack_exists")
                continue

            try:
                pack = generate_pack_for_trend(
                    trend_id=tid,
                    term=term,
                    country=country,
                    category=category,
                    sku_count=sku_count,
                    provider=provider,
                )
                gen_at = pack.get("generated_at") or utc_iso()
                update_pack(conn, trend_id=tid, pack=pack, generated_at=gen_at, dry_run=dry_run)
                generated += 1
                print(f"[OK]   id={tid} action_level={action_level} skus={pack['summary'].get('total_skus')}")
            except Exception as e:
                errors += 1
                print(f"[ERR]  id={tid} action_level={action_level} error={e}")

            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

        if not dry_run:
            conn.commit()

        print(f"[DONE] generated={generated} skipped={skipped} errors={errors}")
        return 0 if errors == 0 else 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())