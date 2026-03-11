(async function(){
  async function load(){
    const urls = ["/docs/push_ready_v37.json","../docs/push_ready_v37.json"];
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
      <div style="font-size:22px;font-weight:700;">${x.title || "-"}</div>
      <div class="muted" style="margin-top:6px;">audience: ${x.audience || "-"}</div>
      <div style="margin-top:12px;"><b>Listing标题：</b><div class="muted">${(x.body_json||{}).listing_title || "-"}</div></div>
      <div style="margin-top:12px;"><b>任务：</b>
        <div class="chips">${(((x.body_json||{}).task_list_json)||[]).map(t=>`<span class="chip">${t}</span>`).join("")}</div>
      </div>
    </div>
  `).join("");
})();