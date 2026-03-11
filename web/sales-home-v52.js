(async function(){
  async function load(){
    const urls = ["/docs/sales_home_v52.json","../docs/sales_home_v52.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {};
  }

  const data = await load();
  const hero = data.hero || {};
  document.getElementById("title").textContent = hero.title || "TrendForge";
  document.getElementById("subtitle").textContent = hero.subtitle || "-";
  document.getElementById("tagline").textContent = hero.tagline || "-";

  const pricing = data.pricing || [];
  document.getElementById("pricing").innerHTML = pricing.map(x => `
    <div class="card">
      <div class="badge">${x.plan || "-"}</div>
      <div class="price">${x.price_usd || "-"}</div>
      <div class="subprice">${x.price_cny || "-"}</div>
      <div style="margin-top:12px;">
        ${(x.features || []).map(f => `<div class="item">${f}</div>`).join("")}
      </div>
    </div>
  `).join("");

  const topItems = data.top_items || [];
  document.getElementById("top").innerHTML = topItems.map(x => `
    <div class="item">
      <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
        <b>${x.term || "-"}</b>
        <span class="badge">${x.decision_level || "-"}</span>
      </div>
      <div class="muted" style="margin-top:8px;">score: ${x.trend_power_score ?? "-"} | profit: ${x.profit_score ?? "-"}</div>
    </div>
  `).join("") || "<div class='muted'>暂无数据</div>";

  const s = data.summary || {};
  document.getElementById("runtime").innerHTML = `
    <div class="item"><b>Top Items</b><div class="muted">${s.top_items ?? 0}</div></div>
    <div class="item"><b>DO_NOW</b><div class="muted">${s.do_now ?? 0}</div></div>
    <div class="item"><b>Push Total</b><div class="muted">${s.push_total ?? 0}</div></div>
    <div class="item"><b>Push OK</b><div class="muted">${s.push_ok ?? 0}</div></div>
  `;
})();