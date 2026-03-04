from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime, timezone
import sqlite3
import json
import os
import re

app = FastAPI(title="TrendForge API", version="0.6.2")
from routes_expansion import router as expansion_router
app.include_router(expansion_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Time / DB
# ----------------------------
def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_db_path() -> str:
    env_path = os.environ.get("TRENDFORGE_DB_PATH") or os.environ.get("DB_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    candidates = [
        "/root/trendforge-mvp/server/trendforge.db",
        "/root/trendforge-mvp/trendforge.db",
        "/root/trendforge-mvp/server/app.db",
        "/root/trendforge-mvp/app.db",
        "/var/www/trendforge/trendforge.db",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return "/root/trendforge-mvp/server/trendforge.db"


DB_PATH = detect_db_path()


def db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> set:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r["name"] for r in rows}


def try_ensure_flags_columns(conn: sqlite3.Connection) -> None:
    """
    尽量加列：done/saved/flags_updated_at/last_pushed_at/last_pushed_action/last_action_level（不强制成功）
    """
    cols = table_columns(conn, "trends")
    alters = []
    if "done" not in cols:
        alters.append("ALTER TABLE trends ADD COLUMN done INTEGER DEFAULT 0")
    if "saved" not in cols:
        alters.append("ALTER TABLE trends ADD COLUMN saved INTEGER DEFAULT 0")
    if "flags_updated_at" not in cols:
        alters.append("ALTER TABLE trends ADD COLUMN flags_updated_at TEXT")
    if "last_pushed_action" not in cols:
        alters.append("ALTER TABLE trends ADD COLUMN last_pushed_action TEXT")
    if "last_pushed_at" not in cols:
        alters.append("ALTER TABLE trends ADD COLUMN last_pushed_at TEXT")
    if "last_action_level" not in cols:
        alters.append("ALTER TABLE trends ADD COLUMN last_action_level TEXT")

    for sql in alters:
        try:
            conn.execute(sql)
        except Exception:
            pass
    if alters:
        conn.commit()


def safe_json_loads(s: Any) -> Dict[str, Any]:
    if s is None:
        return {}
    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except Exception:
        return {}


def json_dump(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def ensure_meta(payload: Dict[str, Any]) -> Dict[str, Any]:
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    payload["meta"] = meta
    return meta


def normalize_item(row: sqlite3.Row) -> Dict[str, Any]:
    payload = safe_json_loads(row["payload_json"])

    done_col = row["done"] if "done" in row.keys() else None
    saved_col = row["saved"] if "saved" in row.keys() else None
    flags = payload.get("flags") or {}
    done = bool(done_col) if done_col is not None else bool(flags.get("done", False))
    saved = bool(saved_col) if saved_col is not None else bool(flags.get("saved", False))

    return {
        "id": row["id"],
        "date": row["date"],
        "term": row["term"],
        "country": row["country"],
        "category": row["category"],
        "growth": row["growth"],
        "hit_score": row["hit_score"],
        "action_level": row["action_level"],
        "payload_json": payload,
        "done": done,
        "saved": saved,
    }


def get_trend_or_404(conn: sqlite3.Connection, trend_id: int) -> sqlite3.Row:
    r = conn.execute("SELECT * FROM trends WHERE id=?", (trend_id,)).fetchone()
    if not r:
        raise HTTPException(status_code=404, detail=f"trend id={trend_id} not found")
    return r


# ----------------------------
# D4-1 Listing generator (template, no LLM)
# ----------------------------
STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "with", "by", "is", "are",
    "shirt", "t", "tee", "tshirt", "hoodie", "sweatshirt", "tank", "top"
}


def _nonempty(v: Any) -> bool:
    return bool(str(v or "").strip())


def normalize_term(term: str) -> str:
    term = (term or "").strip()
    term = re.sub(r"\s+", " ", term)
    return term


def tokens(term: str) -> List[str]:
    term = normalize_term(term).lower()
    term = re.sub(r"[^a-z0-9\s]+", " ", term)
    tks = [t for t in term.split() if t and t not in STOPWORDS]
    seen = set()
    out = []
    for t in tks:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out


def slugify(term: str) -> str:
    term = normalize_term(term).lower()
    term = re.sub(r"[^a-z0-9\s-]+", "", term)
    term = re.sub(r"\s+", "-", term).strip("-")
    term = re.sub(r"-{2,}", "-", term)
    return term[:60] or "trend"


def detect_style(term: str) -> Dict[str, str]:
    t = normalize_term(term).lower()
    style = "graphic"
    if "retro" in t:
        style = "retro"
    elif "vintage" in t:
        style = "vintage"
    elif "minimal" in t or "minimalist" in t or "line art" in t or "one line" in t:
        style = "minimal"
    elif "funny" in t or "meme" in t:
        style = "funny"

    audience = "everyone"
    if "dad" in t:
        audience = "dads"
    elif "mom" in t:
        audience = "moms"
    elif "kids" in t or "kid" in t:
        audience = "kids"
    elif "cat" in t or "dog" in t:
        audience = "pet lovers"

    return {"style": style, "audience": audience}


def build_design_prompt(term: str, style: str) -> Dict[str, str]:
    base = normalize_term(term)
    if style == "minimal":
        mj = f"{base}, minimalist line art, clean vector, high contrast, centered composition, print-ready t-shirt design, no mockup, no background"
        sd = f"{base}, minimalist line art, clean vector, high contrast, centered, print-ready t-shirt design, transparent background"
    elif style in ("retro", "vintage"):
        mj = f"{base}, {style} typography, bold type, clean vector, high contrast, centered composition, print-ready t-shirt design, no mockup, no background"
        sd = f"{base}, {style} typography, clean vector, high contrast, print-ready t-shirt design, transparent background"
    elif style == "funny":
        mj = f"{base}, funny typography, playful but clean, vector style, high contrast, centered composition, print-ready t-shirt design, no mockup, no background"
        sd = f"{base}, funny typography, vector style, high contrast, print-ready t-shirt design, transparent background"
    else:
        mj = f"{base}, bold typography, clean vector, high contrast, centered composition, print-ready t-shirt design, no mockup, no background"
        sd = f"{base}, bold typography, clean vector, high contrast, print-ready t-shirt design, transparent background"
    return {"midjourney": mj, "stable_diffusion": sd}


def build_listing(term: str, style: str, audience: str) -> Dict[str, Any]:
    base = normalize_term(term)

    title_style = {
        "minimal": "Minimalist",
        "retro": "Retro",
        "vintage": "Vintage",
        "funny": "Funny",
        "graphic": "Graphic",
    }.get(style, "Graphic")

    audience_phrase = {
        "everyone": "Everyone",
        "dads": "Dads",
        "moms": "Moms",
        "kids": "Kids",
        "pet lovers": "Pet Lovers",
    }.get(audience, "Everyone")

    amazon_title = f"{title_style} {base} Shirt | {title_style} Graphic Tee for {audience_phrase}"
    amazon_title = re.sub(r"\s+", " ", amazon_title).strip()
    if len(amazon_title) > 180:
        amazon_title = amazon_title[:177] + "..."

    bullets = [
        f"Eye-catching {title_style.lower()} {base} design — perfect for daily wear and gifting.",
        "Lightweight, classic fit, and comfortable for all-day use.",
        "Print-ready artwork style — looks great on tees, hoodies, and sweatshirts.",
        f"Ideal gift idea for {audience_phrase.lower()} — birthdays, holidays, and special occasions.",
        "Easy to test fast and iterate — launch small batch, then scale winners.",
    ]

    tks = tokens(term)
    extras = []
    if style in ("retro", "vintage"):
        extras += ["retro", "vintage", "typography", "graphic tee"]
    if style == "minimal":
        extras += ["minimalist", "line art", "one line", "simple"]
    if style == "funny":
        extras += ["funny", "meme", "humor", "joke"]
    if "cat" in term.lower():
        extras += ["cat", "kitty", "cat lover"]
    if "dog" in term.lower():
        extras += ["dog", "puppy", "dog lover"]

    kw = []
    seen = set()
    for w in (tks + extras):
        w = str(w).strip().lower()
        if not w or w in STOPWORDS or w in seen:
            continue
        kw.append(w)
        seen.add(w)

    backend = " ".join(kw)
    backend = re.sub(r"\s+", " ", backend).strip()
    backend = backend[:240]

    sku_style = f"TF-{slugify(term)}-{style[:3].upper()}"

    return {
        "title": amazon_title,
        "bullets": bullets[:5],
        "backend_search_terms": backend,
        "sku_style": sku_style,
    }


def ensure_listing_strategy(ex: Dict[str, Any]) -> Dict[str, Any]:
    strat = ex.get("listing_strategy")
    if not isinstance(strat, dict):
        strat = {}
    strat.setdefault("suggested_quantity", 3)
    strat.setdefault("price_range", "$17.99–19.99")
    strat.setdefault("note", "窗口期短：先小批量测试，再根据数据加款")
    ex["listing_strategy"] = strat
    return strat


def merge_amazon(existing: Dict[str, Any], generated: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(existing) if isinstance(existing, dict) else {}
    # 不覆盖已有手工内容
    if not _nonempty(out.get("title")):
        out["title"] = generated.get("title")
    if not isinstance(out.get("bullets"), list) or not out.get("bullets"):
        out["bullets"] = generated.get("bullets", [])
    if not _nonempty(out.get("backend_search_terms")):
        out["backend_search_terms"] = generated.get("backend_search_terms")
    if not _nonempty(out.get("sku_style")):
        out["sku_style"] = generated.get("sku_style")
    return out


def apply_generate_execution(payload: Dict[str, Any], term: str) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
    """
    返回: (payload, execution, changed?)
    changed 用于 batch：如果没改动，就不更新 execution_updated_at
    """
    meta = ensure_meta(payload)

    ex = payload.get("execution")
    if isinstance(ex, str):
        ex = safe_json_loads(ex)
    if not isinstance(ex, dict):
        ex = {}

    before = json_dump(ex)

    d = detect_style(term)
    style = d["style"]
    audience = d["audience"]

    # design_prompt：若为空才补
    dp = ex.get("design_prompt")
    if not isinstance(dp, dict):
        dp = {}
    if not (_nonempty(dp.get("midjourney")) or _nonempty(dp.get("stable_diffusion"))):
        dp = build_design_prompt(term, style)
    ex["design_prompt"] = dp

    # amazon listing：merge，不覆盖已有手工内容
    amazon = ex.get("amazon")
    if not isinstance(amazon, dict):
        amazon = {}
    generated_listing = build_listing(term=term, style=style, audience=audience)
    amazon = merge_amazon(existing=amazon, generated=generated_listing)
    ex["amazon"] = amazon

    ensure_listing_strategy(ex)

    # execution meta
    ex["generated_at"] = utc_iso()
    ex["generator"] = "template_v2_listing"

    payload["execution"] = ex

    after = json_dump(ex)
    changed = (after != before)

    if changed:
        meta["execution_updated_at"] = utc_iso()

    return payload, ex, changed


# ----------------------------
# API
# ----------------------------
@app.get("/api/health")
def health():
    return {"ok": True, "ts": utc_iso(), "db": DB_PATH}


@app.get("/api/trends")
def get_trends(
    status: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 60,
    offset: int = 0,
    sort: str = "hit_score",
    order: str = "desc",
):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    allowed_sort = {"hit_score", "growth", "id", "date"}
    sort = sort if sort in allowed_sort else "hit_score"
    order = "asc" if str(order).lower() == "asc" else "desc"

    where = []
    params: List[Any] = []

    if status:
        where.append("action_level = ?")
        params.append(status)
    if country:
        where.append("country = ?")
        params.append(country)
    if category:
        where.append("category = ?")
        params.append(category)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    with db_conn() as conn:
        try_ensure_flags_columns(conn)

        count_sql = f"SELECT COUNT(1) AS c FROM trends {where_sql}"
        total = conn.execute(count_sql, params).fetchone()["c"]

        list_sql = f"""
        SELECT *
        FROM trends
        {where_sql}
        ORDER BY {sort} {order}
        LIMIT ? OFFSET ?
        """
        rows = conn.execute(list_sql, params + [limit, offset]).fetchall()
        items = [normalize_item(r) for r in rows]

    return {"items": items, "count": total, "limit": limit, "offset": offset}


@app.post("/api/trends/{trend_id}/flags")
def set_flags(trend_id: int, body: Dict[str, Any] = Body(...)):
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    has_done = "done" in body
    has_saved = "saved" in body
    if not has_done and not has_saved:
        raise HTTPException(status_code=400, detail="Body must include done and/or saved")

    done_val = bool(body.get("done")) if has_done else None
    saved_val = bool(body.get("saved")) if has_saved else None

    with db_conn() as conn:
        try_ensure_flags_columns(conn)
        r = get_trend_or_404(conn, trend_id)
        payload = safe_json_loads(r["payload_json"])
        flags = payload.get("flags") if isinstance(payload.get("flags"), dict) else {}
        if done_val is not None:
            flags["done"] = bool(done_val)
        if saved_val is not None:
            flags["saved"] = bool(saved_val)
        payload["flags"] = flags

        # update row columns if exist
        cols = table_columns(conn, "trends")
        sets = ["payload_json = ?", "flags_updated_at = ?"]
        params: List[Any] = [json_dump(payload), utc_iso()]

        if "done" in cols and done_val is not None:
            sets.append("done = ?")
            params.append(1 if done_val else 0)
        if "saved" in cols and saved_val is not None:
            sets.append("saved = ?")
            params.append(1 if saved_val else 0)

        params.append(trend_id)
        conn.execute(f"UPDATE trends SET {', '.join(sets)} WHERE id = ?", params)
        conn.commit()

        r2 = get_trend_or_404(conn, trend_id)
        return {"ok": True, "item": normalize_item(r2)}


@app.post("/api/trends/{trend_id}/set_action_level")
def set_action_level(trend_id: int, body: Dict[str, Any] = Body(...)):
    level = (body.get("action_level") or "").strip()
    if level not in {"DO_NOW", "DOING", "WATCH"}:
        raise HTTPException(status_code=400, detail="action_level must be DO_NOW/DOING/WATCH")

    with db_conn() as conn:
        try_ensure_flags_columns(conn)
        get_trend_or_404(conn, trend_id)
        conn.execute(
            "UPDATE trends SET action_level=?, flags_updated_at=? WHERE id=?",
            (level, utc_iso(), trend_id),
        )
        conn.commit()
        r2 = get_trend_or_404(conn, trend_id)
        return {"ok": True, "item": normalize_item(r2)}


@app.post("/api/trends/{trend_id}/generate_execution")
def generate_execution(trend_id: int):
    with db_conn() as conn:
        try_ensure_flags_columns(conn)
        r = get_trend_or_404(conn, trend_id)

        term = r["term"]
        payload = safe_json_loads(r["payload_json"])

        payload, ex, changed = apply_generate_execution(payload=payload, term=term)

        # 即使没变化，也刷新 generated_at（但不触发 execution_updated_at）
        if not changed:
            ex["generated_at"] = utc_iso()
            ex["generator"] = ex.get("generator") or "template_v2_listing"
            payload["execution"] = ex

        conn.execute("UPDATE trends SET payload_json=? WHERE id=?", (json_dump(payload), trend_id))
        conn.commit()

        r2 = get_trend_or_404(conn, trend_id)
        return {"ok": True, "id": trend_id, "execution": ex, "changed": changed, "item": normalize_item(r2)}


# ----------------------------
# D4-2 Batch API (方案A：只处理 DO_NOW)
# ----------------------------
@app.post("/api/trends/generate_execution_batch")
def generate_execution_batch(body: Dict[str, Any] = Body(default={})):
    """
    方案A：只对 DO_NOW 批量生成执行包（listing 补齐）
    body 可选：
      {
        "limit": 20,           # 本次最多处理多少条（默认20，上限100）
        "country": "US",       # 可选过滤
        "category": "POD"      # 可选过滤
      }
    """
    if body is None:
        body = {}
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    limit = int(body.get("limit", 20))
    limit = max(1, min(limit, 100))
    country = (body.get("country") or "").strip() or None
    category = (body.get("category") or "").strip() or None

    where = ["action_level = ?"]
    params: List[Any] = ["DO_NOW"]
    if country:
        where.append("country = ?")
        params.append(country)
    if category:
        where.append("category = ?")
        params.append(category)

    where_sql = " AND ".join(where)

    updated_ids: List[int] = []
    skipped_ids: List[int] = []

    with db_conn() as conn:
        try_ensure_flags_columns(conn)

        rows = conn.execute(
            f"""
            SELECT * FROM trends
            WHERE {where_sql}
            ORDER BY hit_score DESC, id DESC
            LIMIT ?
            """,
            params + [limit],
        ).fetchall()

        for r in rows:
            tid = int(r["id"])
            term = r["term"]
            payload = safe_json_loads(r["payload_json"])

            payload2, ex, changed = apply_generate_execution(payload=payload, term=term)

            if changed:
                conn.execute("UPDATE trends SET payload_json=? WHERE id=?", (json_dump(payload2), tid))
                updated_ids.append(tid)
            else:
                skipped_ids.append(tid)

        conn.commit()

    return {
        "ok": True,
        "mode": "DO_NOW_only",
        "limit": limit,
        "filters": {"country": country, "category": category},
        "updated": len(updated_ids),
        "skipped": len(skipped_ids),
        "updated_ids": updated_ids,
        "skipped_ids": skipped_ids,
    }