(async function(){
  async function load(){
    const urls = ["/docs/feishu_push_v40.json","../docs/feishu_push_v40.json"];
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
      <div class="badge">${x.audience || "-"}</div>
      <div style="font-size:22px;font-weight:700;">${x.title || "-"}</div>
      <div class="muted" style="margin-top:8px;">ok: ${x.ok} | dry_run: ${x.dry_run} | status: ${x.http_status}</div>
      <div class="muted" style="margin-top:10px;">${x.response_text || "-"}</div>
    </div>
  `).join("");
})();