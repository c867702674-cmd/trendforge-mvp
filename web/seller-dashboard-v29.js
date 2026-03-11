
(async function(){
  async function load(){
    const urls = ["/docs/web_dashboard_v29_api.json","../docs/web_dashboard_v29_api.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {};
  }
  function put(id, html){ document.getElementById(id).innerHTML = html; }
  const data = await load();
  const opps = data.top_opportunities || [];
  const listings = data.top_listings || [];
  const profits = data.top_profits || [];
  put("meta", `<div>更新时间：${data.generated_at || "-"}</div>`);
  put("summary", `<div>Opportunities：${opps.length}</div><div>Listings：${listings.length}</div><div>Profits：${profits.length}</div>`);
  put("opps", opps.slice(0,10).map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">score: ${x.opportunity_score ?? "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("listings", listings.slice(0,10).map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">${x.listing_title||"-"}</div><div class="muted">score: ${x.draft_score ?? "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("profits", profits.slice(0,10).map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">profit: ${x.profit_score ?? "-"}</div><div class="muted">demand: ${x.demand_score ?? "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
})();
