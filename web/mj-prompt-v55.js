(async function(){
  async function load(){
    const urls = ["/docs/mj_prompt_v55.json","../docs/mj_prompt_v55.json"];
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
      <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
        <b>${x.subject_line || "-"}</b>
        <span class="badge">${x.sku_hint || "-"}</span>
      </div>
      <div class="muted" style="margin-top:8px;">style: ${x.style_name || "-"} | ar: ${x.aspect_ratio || "-"}</div>
      <div class="item"><b>MJ Prompt</b><div class="muted">${x.mj_prompt || "-"}</div></div>
      <div class="item"><b>SDXL Prompt</b><div class="muted">${x.sdxl_prompt || "-"}</div></div>
      <div class="item"><b>Negative</b><div class="muted">${x.negative_prompt || "-"}</div></div>
    </div>
  `).join("");
})();