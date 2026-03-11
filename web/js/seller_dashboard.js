const TrendForgeSellerDashboard = (() => {
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
  function fmt(v) {
    const n = Number(v || 0);
    return Number.isNaN(n) ? "-" : n.toFixed(2);
  }
  async function load() {
    return safeFetch("../docs/seller_dashboard_api.json").catch(() => safeFetch("/docs/seller_dashboard_api.json"));
  }
  async function render() {
    const rootTrends = document.getElementById("savedTrends");
    const rootPacks = document.getElementById("executionPacks");
    const rootListings = document.getElementById("amazonListings");
    const kpiSellerName = document.getElementById("kpiSellerName");
    const kpiSaved = document.getElementById("kpiSaved");
    const kpiPacks = document.getElementById("kpiPacks");
    const kpiListings = document.getElementById("kpiListings");
    try {
      const data = await load();
      const seller = data.seller || {};
      const saved = data.saved_trends || [];
      const packs = data.execution_packs || [];
      const listings = data.amazon_listings || [];
      kpiSellerName.textContent = seller.name || "Owner";
      kpiSaved.textContent = saved.length;
      kpiPacks.textContent = packs.length;
      kpiListings.textContent = listings.length;
      rootTrends.innerHTML = "";
      saved.forEach((item, idx) => {
        rootTrends.appendChild(el(`<div class="item"><div><b>#${idx+1}</b> ${item.term}</div><div class="meta">Level: ${item.action_level || "-"} · Hit: ${fmt(item.hit_score)} · POD Relevance: ${fmt(item.pod_relevance_score)}</div></div>`));
      });
      rootPacks.innerHTML = "";
      packs.forEach((item, idx) => {
        const tags = Array.isArray(item.tags) ? item.tags.slice(0,6) : [];
        rootPacks.appendChild(el(`<div class="item"><div><b>#${idx+1}</b> ${item.title || item.trend_term || "-"}</div><div class="meta">Trend: ${item.trend_term || "-"} · Score: ${fmt(item.score)} · Rank: ${fmt(item.rank_score)}</div><div>${tags.map(t => `<span class="tag">${t}</span>`).join("")}</div></div>`));
      });
      rootListings.innerHTML = "";
      listings.forEach((item, idx) => {
        rootListings.appendChild(el(`<div class="item"><div><b>#${idx+1}</b> ${item.amazon_title || "-"}</div><div class="meta">Trend ID: ${item.trend_id} · Rank: ${fmt(item.rank_score)}</div><div class="meta">Search Terms: ${item.amazon_search_terms || "-"}</div><div style="margin-top:8px;">${item.amazon_description || ""}</div></div>`));
      });
    } catch (e) {
      rootTrends.innerHTML = `<div class="item">seller_dashboard_api.json 读取失败，请确认 V17 pipeline 已运行。</div>`;
      rootPacks.innerHTML = `<div class="item">Execution Packs 未读取成功。</div>`;
      rootListings.innerHTML = `<div class="item">Amazon Listings 未读取成功。</div>`;
    }
  }
  return { render };
})();