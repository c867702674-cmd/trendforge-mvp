# server/api/flags.py
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["flags"])

def _db_path() -> str:
    # 兼容：优先环境变量；否则用你项目默认路径
    return os.environ.get("DB_PATH", "/root/trendforge-mvp/server/trendforge.db")

def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

class FlagsIn(BaseModel):
    done: Optional[bool] = None
    favorite: Optional[bool] = None

@router.get("/trends/{trend_id}/flags")
def get_flags(trend_id: int):
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT payload_json FROM trends WHERE id = ?",
            (trend_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trend not found")

        payload_raw = row["payload_json"] or "{}"
        try:
            payload = json.loads(payload_raw)
        except Exception:
            payload = {}

        flags = (payload.get("flags") or {})
        return {
            "id": trend_id,
            "flags": {
                "done": bool(flags.get("done")) if "done" in flags else False,
                "favorite": bool(flags.get("favorite")) if "favorite" in flags else False,
                "updated_at": flags.get("updated_at"),
            },
        }
    finally:
        conn.close()

@router.post("/trends/{trend_id}/flags")
def set_flags(trend_id: int, data: FlagsIn):
    if data.done is None and data.favorite is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT payload_json FROM trends WHERE id = ?",
            (trend_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trend not found")

        payload_raw = row["payload_json"] or "{}"
        try:
            payload = json.loads(payload_raw)
        except Exception:
            payload = {}

        flags = payload.get("flags") or {}
        if data.done is not None:
            flags["done"] = bool(data.done)
        if data.favorite is not None:
            flags["favorite"] = bool(data.favorite)
        flags["updated_at"] = _utc_now()
        payload["flags"] = flags

        conn.execute(
            "UPDATE trends SET payload_json = ? WHERE id = ?",
            (json.dumps(payload, ensure_ascii=False), trend_id),
        )
        conn.commit()

        return {"id": trend_id, "flags": flags}
    finally:
        conn.close()