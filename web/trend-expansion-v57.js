(async function(){
  async function load(){
    const urls = ["/docs/trend_expansion_v57.json","../docs/trend_expansion_v57.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {items:[]};
  }

  const data = await load();
  const app = document.getElementById("app");
  const items = data.items || [];

  if(!items.length){
    app.innerHTML = "<div class='card'>暂无数据</div>";
    return;
  }

  app.innerHTML = items.slice(0,60).map(x => `
    <div class="card">
      <b>${x.base_term || "-"}</b>
      <div class="item"><div class="muted">${x.expanded_term || "-"}</div></div>
      <div class="item"><div class="muted">type: ${x.expansion_type || "-"} | score: ${x.score ?? "-"}</div></div>
    </div>
  `).join("");
})();