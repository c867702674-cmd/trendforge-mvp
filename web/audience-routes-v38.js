(async function(){
  async function load(){
    const urls = ["/docs/audience_routes_v38.json","../docs/audience_routes_v38.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {items:[]};
  }
  const data = await load();
  const grid = document.getElementById("grid");
  const items = data.items || [];
  if(!items.length){
    grid.innerHTML = "<div class='card'>暂无数据</div>";
    return;
  }
  grid.innerHTML = items.slice(0,24).map(x => `
    <div class="card">
      <div class="badge">${x.route_name || "-"}</div>
      <div style="font-size:22px;font-weight:700;">${x.title || "-"}</div>
      <div class="muted" style="margin-top:8px;">audience: ${x.audience || "-"}</div>
      <div style="margin-top:12px;">priority: ${x.priority_score ?? "-"}</div>
      <div class="muted" style="margin-top:10px;">listing: ${((x.body_json||{}).listing_title) || "-"}</div>
    </div>
  `).join("");
})();