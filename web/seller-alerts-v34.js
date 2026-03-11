(async function(){
  async function load(){
    const urls = ["/docs/seller_alerts_v34.json","../docs/seller_alerts_v34.json"];
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
  grid.innerHTML = items.slice(0,20).map(x => `
    <div class="card">
      <div class="badge">${x.alert_level || "-"}</div>
      <div style="font-size:22px;font-weight:700;">${x.alert_title || "-"}</div>
      <div class="muted" style="margin-top:10px;">${x.alert_text || "-"}</div>
      <div style="margin-top:14px;">Score: ${x.alert_score ?? "-"}</div>
    </div>
  `).join("");
})();