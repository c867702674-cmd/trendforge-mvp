(async function(){
  async function load(){
    const urls = ["/docs/opportunity_cards_v33.json","../docs/opportunity_cards_v33.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {items:[]};
  }
  const data = await load();
  const grid = document.getElementById('grid');
  const items = data.items || [];
  if(!items.length){
    grid.innerHTML = "<div class='card'>暂无数据</div>";
    return;
  }
  grid.innerHTML = items.slice(0,12).map(x => `
    <div class="card">
      <div style="font-size:22px;font-weight:700;">${x.card_title || "-"}</div>
      <div class="muted" style="margin-top:6px;">${x.card_subtitle || "-"}</div>
      <div class="section"><b>推荐设计：</b><div class="muted">${x.design_direction || "-"}</div></div>
      <div class="section"><b>推荐标题：</b><div class="muted">${x.recommended_title || "-"}</div></div>
      <div class="section"><b>推荐产品：</b>
        <div class="chips">${(x.recommended_products_json || []).map(p=>`<span class="chip">${p}</span>`).join("")}</div>
      </div>
    </div>
  `).join("");
})();