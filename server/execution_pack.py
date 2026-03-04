# server/execution_pack.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_execution_pack_prompt(term: str, country: str, category: str, angles: List[str]) -> str:
    # 单次生成 8 个 SKU，强制 angles，要求 JSON-only
    angles_str = ", ".join(angles)
    return f"""
You are a senior Amazon US POD listing expert.

Given the trend keyword:
- Term: {term}
- Country: {country}
- Category: {category}

Generate an EXECUTION PACK containing {len(angles)} SKU variants.

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
    "total_skus": {len(angles)},
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


def _extract_json(text: str) -> Dict[str, Any]:
    """
    尽量容错：如果模型输出夹杂了多余字符，尝试截取第一个 {...} 的 JSON。
    """
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # 截取第一个大括号块
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("LLM output does not contain JSON object.")
    return json.loads(m.group(0))


def validate_execution_pack(pack: Dict[str, Any], angles: List[str]) -> Dict[str, Any]:
    if "sku_variants" not in pack or not isinstance(pack["sku_variants"], list):
        raise ValueError("execution_pack_json missing sku_variants list.")

    variants = pack["sku_variants"]
    if len(variants) < len(angles):
        # 允许少量不足，但建议你生产环境要求必须齐
        raise ValueError(f"sku_variants count {len(variants)} < required {len(angles)}.")

    seen_titles = set()
    seen_sku = set()
    for v in variants:
        if v.get("angle") not in angles:
            raise ValueError(f"Invalid angle: {v.get('angle')}")

        title = (v.get("title") or "").strip()
        if not title:
            raise ValueError("SKU missing title")
        if title in seen_titles:
            raise ValueError(f"Duplicate title: {title}")
        seen_titles.add(title)

        sku_id = (v.get("sku_id") or "").strip()
        if not sku_id:
            raise ValueError("SKU missing sku_id")
        if sku_id in seen_sku:
            raise ValueError(f"Duplicate sku_id: {sku_id}")
        seen_sku.add(sku_id)

        bullets = v.get("bullets")
        if not isinstance(bullets, list) or len(bullets) != 5:
            raise ValueError("bullets must be a list of exactly 5 items")

        bk = v.get("backend_keywords")
        if not isinstance(bk, list) or len(bk) < 5:
            raise ValueError("backend_keywords must be a list")

        conf = v.get("confidence")
        if conf is None or not isinstance(conf, (int, float)):
            raise ValueError("confidence must be a number")
        if conf < 0 or conf > 1:
            raise ValueError("confidence must be between 0 and 1")

    # 补齐元信息（保证你 DB 里结构稳定）
    pack.setdefault("summary", {})
    return pack


@dataclass
class LLMResult:
    text: str
    raw: Optional[Any] = None


class LLMProvider:
    """
    你项目里如果已有“生成 execution_json”的 LLM 调用函数，
    直接在这里替换 call() 即可。
    """
    def call(self, prompt: str) -> LLMResult:
        raise NotImplementedError


class DummyProvider(LLMProvider):
    """
    兜底：没有接 LLM 时，先返回一个可用的 mock pack，方便你先把链路打通。
    上线前把它换掉即可。
    """
    def call(self, prompt: str) -> LLMResult:
        mock = {
            "summary": {
                "total_skus": 8,
                "recommended_platforms": ["Amazon", "Etsy"],
                "best_angles": ["Humor", "Gift", "Identity"],
            },
            "sku_variants": [
                {
                    "sku_id": "mock_humor_01",
                    "angle": "Humor",
                    "target_audience": "General",
                    "title": "Mock Title - Humor",
                    "bullets": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4", "Bullet 5"],
                    "backend_keywords": ["mock", "keyword", "pod", "shirt", "tee"],
                    "design_prompt": "Simple typography design",
                    "style": "Minimal Typography",
                    "confidence": 0.7,
                }
            ] + [
                {
                    "sku_id": f"mock_{i:02d}",
                    "angle": a,
                    "target_audience": "General",
                    "title": f"Mock Title - {a}",
                    "bullets": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4", "Bullet 5"],
                    "backend_keywords": ["mock", "keyword", "pod", "shirt", "tee"],
                    "design_prompt": "Simple design prompt",
                    "style": "Bold Graphic",
                    "confidence": 0.6,
                }
                for i, a in enumerate(SKU_ANGLES_DEFAULT[1:], start=2)
            ],
        }
        return LLMResult(text=json.dumps(mock))


def generate_execution_pack(
    *,
    trend_id: int,
    term: str,
    country: str,
    category: str,
    sku_count: int = 8,
    provider: Optional[LLMProvider] = None,
) -> Dict[str, Any]:
    angles = SKU_ANGLES_DEFAULT[: max(1, min(sku_count, len(SKU_ANGLES_DEFAULT)))]
    provider = provider or DummyProvider()

    prompt = build_execution_pack_prompt(term=term, country=country, category=category, angles=angles)
    llm_res = provider.call(prompt)

    pack = _extract_json(llm_res.text)
    pack = validate_execution_pack(pack, angles)

    # 统一补齐一些字段，方便你前端、推送直接用
    pack_out: Dict[str, Any] = {
        "trend_id": trend_id,
        "term": term,
        "country": country,
        "category": category,
        "generated_at": _utc_iso(),
        "summary": pack.get("summary", {}),
        "sku_variants": pack["sku_variants"][: len(angles)],
    }
    # summary.total_skus 保底
    pack_out["summary"].setdefault("total_skus", len(pack_out["sku_variants"]))
    return pack_out