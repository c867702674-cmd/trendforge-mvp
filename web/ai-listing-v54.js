(async function(){
  async function load(){
    const urls = ["/docs/ai_listing_v54.json","../docs/ai_listing_v54.json"];
    for (const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {items:[]};
  }
  const data = await load();
  const items = data.items || [];
  const grid = document.getElementById("grid");
  if(!items.length){
    grid.innerHTML = "<div class='card'>暂无数据</div>";
    return;
  }
  grid.innerHTML = items.slice(0,20).map(x => `
    <div class="card">
      <div style="font-size:22px;font-weight:700;">${x.title || "-"}</div>
      <div class="muted" style="margin-top:6px;">term: ${x.term || "-"} | platform: ${x.platform || "-"}</div>
      <div class="item"><b>Bullet 1</b><div class="muted">${x.bullet_1 || "-"}</div></div>
      <div class="item"><b>Bullet 2</b><div class="muted">${x.bullet_2 || "-"}</div></div>
      <div class="item"><b>Design Prompt</b><div class="muted">${x.design_prompt || "-"}</div></div>
      <div class="chips">${(x.tags_json || []).map(t => `<span class="chip">${t}</span>`).join("")}</div>
    </div>
  `).join("");
})();