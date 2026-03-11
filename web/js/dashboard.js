const TrendForgeDashboard = (() => {
  async function safeFetch(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error(`Fetch failed: ${url}`);
    return res.json();
  }
  function el(html) {
    const t = document.createElement("template");
    t.innerHTML = html.trim();
    return t.content.firstChild;
  }
  function fmtScore(v) {
    const n = Number(v || 0);
    if (Number.isNaN(n)) return "-";
    return n.toFixed(2);
  }
  async function loadDashboard() {
    return safeFetch("../docs/dashboard_api.json").catch(() => safeFetch("/docs/dashboard_api.json"));
  }
  async function loadTrendBoard() {
    return safeFetch("../docs/top_trend_board.json").catch(() => safeFetch("/docs/top_trend_board.json"));
  }
  async function renderHome() {
    const rootTrends = document.getElementById("topTrends");
    const rootPacks = document.getElementById("topPacks");
    const kpiTrends = document.getElementById("kpiTrends");
    const kpiPacks = document.getElementById("kpiPacks");
    const kpiUpdated = document.getElementById("kpiUpdated");
    try {
      const data = await loadDashboard();
      const trends = data.top_trends || [];
      const packs = data.top_execution_packs || [];
      kpiTrends.textContent = trends.length;
      kpiPacks.textContent = packs.length;
      kpiUpdated.textContent = (data.generated_at || "-").slice(11, 16);
      rootTrends.innerHTML = "";
      trends.slice(0, 8).forEach((item, idx) => {
        rootTrends.appendChild(el(`<div class="item"><div><b>#${idx+1}</b> ${item.term}</div><div class="meta">Level: ${item.action_level || "-"} · Hit Score: ${fmtScore(item.hit_score)} · Growth: ${fmtScore(item.growth)}</div></div>`));
      });
      rootPacks.innerHTML = "";
      packs.slice(0, 8).forEach((item, idx) => {
        rootPacks.appendChild(el(`<div class="item"><div><b>#${idx+1}</b> ${item.title || item.trend_term || "-"}</div><div class="meta">Trend: ${item.trend_term || "-"} · Pack Score: ${fmtScore(item.score)} · Rank: ${fmtScore(item.rank_score)}</div></div>`));
      });
    } catch (e) {
      rootTrends.innerHTML = `<div class="item">Dashboard API 未读取成功，请确认 /docs/dashboard_api.json 可访问。</div>`;
      rootPacks.innerHTML = `<div class="item">Execution Packs 未读取成功，请确认 V13 已运行。</div>`;
    }
  }
  async function renderTrendBoard() {
    const root = document.getElementById("trendBoard");
    try {
      const data = await loadTrendBoard();
      const items = data.items || [];
      root.innerHTML = "";
      items.forEach((item, idx) => {
        root.appendChild(el(`<div class="card"><div class="row"><div><div class="term">#${idx+1} ${item.term}</div><div class="meta">Action: ${item.action_level || "-"} · Hit Score: ${fmtScore(item.hit_score)} · Growth: ${fmtScore(item.growth)}</div></div><div>${item.id}</div></div></div>`));
      });
    } catch (e) {
      root.innerHTML = `<div class="card">趋势榜读取失败，请确认 /docs/top_trend_board.json 已生成。</div>`;
    }
  }
  async function renderExecutionPacks() {
    const root = document.getElementById("executionPacks");
    try {
      const data = await loadDashboard();
      const items = data.top_execution_packs || [];
      root.innerHTML = "";
      items.forEach((item, idx) => {
        root.appendChild(el(`<div class="card"><div class="title">#${idx+1} ${item.title || "-"}</div><div class="meta">Trend: ${item.trend_term || "-"} · Pack Score: ${fmtScore(item.score)} · Rank Score: ${fmtScore(item.rank_score)}</div><div class="tags">Trend ID: ${item.trend_id}</div></div>`));
      });
    } catch (e) {
      root.innerHTML = `<div class="card">Execution Packs 读取失败，请确认 /docs/dashboard_api.json 已生成。</div>`;
    }
  }
  async function renderListingIdeas() {
    const root = document.getElementById("listingIdeas");
    try {
      const data = await loadDashboard();
      const items = data.top_execution_packs || [];
      root.innerHTML = "";
      items.forEach((item, idx) => {
        root.appendChild(el(`<div class="card"><div class="title">#${idx+1} ${item.title || "-"}</div><div class="meta">Trend: ${item.trend_term || "-"} · Rank Score: ${fmtScore(item.rank_score)}</div><div>Pack Score: ${fmtScore(item.score)}</div></div>`));
      });
    } catch (e) {
      root.innerHTML = `<div class="card">Listing Ideas 读取失败，请确认 dashboard_api.json 已生成。</div>`;
    }
  }
  return { renderHome, renderTrendBoard, renderExecutionPacks, renderListingIdeas };
})();