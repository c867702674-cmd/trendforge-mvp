# /root/trendforge-mvp/server/routes_expansion.py
from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from expansion_engine import expand_trend_to_db, DEFAULT_DB_PATH

router = APIRouter()

def _db_path() -> str:
    return os.environ.get("TRENDFORGE_DB_PATH", DEFAULT_DB_PATH)

@router.post("/api/expand/{trend_id}")
def api_expand_trend(
    trend_id: int,
    n: int = Query(12, ge=1, le=50),
    force: int = Query(0, ge=0, le=1),
) -> Dict[str, Any]:
    """
    A3: 扩散一个趋势并写入 design_ideas / design_prompts
    - force=0: 已存在则跳过
    - force=1: 删除旧扩散结果后重建
    """
    out = expand_trend_to_db(db_path=_db_path(), trend_id=trend_id, n=n, force=bool(force))
    if not out.get("ok"):
        raise HTTPException(status_code=404, detail=out.get("error", "expand failed"))
    return out

@router.get("/api/ideas/{trend_id}")
def api_get_ideas(trend_id: int) -> Dict[str, Any]:
    """
    读取某 trend_id 的 design ideas + prompts（给 Web/Push 用）
    """
    db = _db_path()
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        ideas = conn.execute(
            "SELECT id, idea FROM design_ideas WHERE trend_id = ? ORDER BY id DESC",
            (trend_id,),
        ).fetchall()

        result = []
        for r in ideas:
            idea_id = int(r["id"])
            prompt_row = conn.execute(
                "SELECT prompt FROM design_prompts WHERE idea_id = ? ORDER BY id DESC LIMIT 1",
                (idea_id,),
            ).fetchone()
            result.append(
                {
                    "idea_id": idea_id,
                    "idea": r["idea"],
                    "prompt": prompt_row["prompt"] if prompt_row else "",
                }
            )
        return {"ok": True, "trend_id": trend_id, "items": result, "count": len(result)}
    finally:
        conn.close()