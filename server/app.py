from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import date
import json

from db import init_db, list_trends, insert_trend

app = FastAPI(title="TrendForge MVP")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def home():
    rows = list_trends(200)

    css = """
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
             padding: 24px; background: #f7f7fb; color:#111; }
      h2 { margin: 0 0 8px; }
      .sub { color:#555; margin: 0 0 16px; }
      .card { background:#fff; border-radius:12px; padding:16px; box-shadow: 0 6px 18px rgba(0,0,0,.06); }
      table { width:100%; border-collapse: collapse; overflow:hidden; border-radius:10px; }
      th, td { padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; font-size: 14px; }
      th { background: #fafafa; color:#333; font-weight: 600; }
      tr:hover td { background:#fcfcff; }
      .pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#f0f2ff; color:#3b5bdb; font-size:12px; }
      .muted { color:#888; }
      .topbar { display:flex; align-items:baseline; justify-content:space-between; gap:12px; margin-bottom:12px;}
      a { color:#3b5bdb; text-decoration:none; }
      a:hover { text-decoration:underline; }
      code { background:#f2f2f2; padding:2px 6px; border-radius:6px; }
      .tag { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; }
      .do { background:#e6fcf5; color:#087f5b; }
      .ft { background:#fff3bf; color:#8a5a00; }
      .ig { background:#f1f3f5; color:#495057; }
      .risk-low { background:#e7f5ff; color:#1c7ed6; }
      .risk-med { background:#fff4e6; color:#d9480f; }
      .risk-high { background:#fff5f5; color:#c92a2a; }
    </style>
    """

    html = [
        "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'/>",
        "<title>TrendForge</title>",
        css,
        "</head><body>",
        "<div class='topbar'>",
        "<div>",
        "<h2>TrendForge – Daily Opportunity Dashboard</h2>",
        "<p class='sub'>Latest 200 records (Tip: visit <code>/seed</code> to insert demo rows)</p>",
        "</div>",
        "<div class='muted'>API: <a href='/docs'>/docs</a></div>",
        "</div>",
        "<div class='card'>",
        "<table>",
        "<tr>"
        "<th>ID</th><th>Date</th><th>Keyword</th><th>Growth</th>"
        "<th>Score</th><th>Action</th><th>Risk</th>"
        "<th>Country</th><th>Category</th>"
        "</tr>",
    ]

    def fmt_float(x):
        if x is None:
            return ""
        try:
            return f"{float(x):.2f}"
        except Exception:
            return str(x)

    def action_badge(a: str) -> str:
        a = (a or "").upper()
        if a == "DO_NOW":
            return "<span class='tag do'>DO NOW</span>"
        if a == "FAST_TEST":
            return "<span class='tag ft'>FAST TEST</span>"
        if a in ["IGNORE", "WATCH", "SKIP"]:
            return "<span class='tag ig'>IGNORE</span>"
        return "<span class='tag ig'></span>"

    def risk_badge(r: str) -> str:
        r = (r or "").upper()
        if r == "LOW":
            return "<span class='tag risk-low'>LOW</span>"
        if r == "MEDIUM":
            return "<span class='tag risk-med'>MEDIUM</span>"
        if r == "HIGH":
            return "<span class='tag risk-high'>HIGH</span>"
        return "<span class='tag ig'></span>"

    for r in rows:
        rid = r.get("id", "")
        rdate = r.get("date", "")
        term = r.get("term", "")
        growth = fmt_float(r.get("growth", None))

        score = r.get("hit_score", "")
        action = action_badge(r.get("action_level", ""))
        risk = risk_badge(r.get("risk_level", ""))

        country = r.get("country", "") or ""
        category = r.get("category", "") or ""

        html.append(
            "<tr>"
            f"<td>{rid}</td>"
            f"<td><span class='pill'>{rdate}</span></td>"
            f"<td>{term}</td>"
            f"<td>{growth}</td>"
            f"<td>{score if score is not None else ''}</td>"
            f"<td>{action}</td>"
            f"<td>{risk}</td>"
            f"<td>{country}</td>"
            f"<td>{category}</td>"
            "</tr>"
        )

    html.extend(["</table>", "</div>", "</body></html>"])
    return "\n".join(html)


@app.get("/seed")
def seed():
    """Insert a few demo rows so you can see the dashboard immediately."""
    today = date.today().isoformat()
    demo = [
        {"date": today, "term": "vintage mountain line art", "country": "US", "category": "POD", "growth": 2400.0,
         "hit_score": 82, "action_level": "DO_NOW", "risk_level": "LOW", "reason": "Clear visual motif; low IP risk."},
        {"date": today, "term": "heart patchwork pattern", "country": "US", "category": "POD", "growth": 1800.0,
         "hit_score": 71, "action_level": "FAST_TEST", "risk_level": "LOW", "reason": "Good for patterns across home goods."},
        {"date": today, "term": "sports team logo", "country": "US", "category": "POD", "growth": 3500.0,
         "hit_score": 25, "action_level": "IGNORE", "risk_level": "HIGH", "reason": "Trademark/logo risk."},
    ]
    for item in demo:
        insert_trend(
            date=item["date"],
            term=item["term"],
            country=item.get("country"),
            category=item.get("category"),
            growth=item.get("growth"),
            hit_score=item.get("hit_score"),
            action_level=item.get("action_level"),
            risk_level=item.get("risk_level"),
            reason=item.get("reason"),
            payload_json=json.dumps(item, ensure_ascii=False),
        )
    return JSONResponse({"ok": True, "inserted": len(demo), "tip": "Back to / to view the dashboard"})