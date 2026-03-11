(async function(){
  async function load(){
    const urls = ["/docs/saas_core_v30_api.json","../docs/saas_core_v30_api.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {};
  }
  function put(id, html){ const el=document.getElementById(id); if(el) el.innerHTML=html; }
  const data = await load();
  const counts = data.counts || {};
  put("meta", `更新时间：${data.generated_at || "-"}`);
  put("c1", counts.opportunities ?? 0);
  put("c2", counts.listings ?? 0);
  put("c3", counts.profits ?? 0);
  put("c4", counts.rankings ?? 0);

  const opps = data.top_opportunities || [];
  const listings = data.top_listings || [];
  const profits = data.top_profits || [];
  const rankings = data.top_rankings || [];

  put("opps", opps.map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">score: ${x.opportunity_score ?? "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("listings", listings.map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">${x.listing_title||"-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("profits", profits.map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">profit: ${x.profit_score ?? "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("rankings", rankings.map(x=>`<div class="item"><b>${x.term||"-"}</b><div class="muted">rank: ${x.rank_score ?? "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
})();