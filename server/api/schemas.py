from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class TrendOut(BaseModel):
    id: int
    date: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    term: str
    growth: Optional[float] = None
    hit_score: Optional[float] = None
    action_level: Optional[str] = None
    payload_json: Dict[str, Any] = Field(default_factory=dict)


class TrendsListOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TrendOut]


class SummaryOut(BaseModel):
    total: int
    by_status: Dict[str, int]