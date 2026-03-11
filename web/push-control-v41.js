(async function(){
  async function load(){
    const urls = ["/docs/push_control_v41.json","../docs/push_control_v41.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {};
  }
  const data = await load();
  const summary = data.summary || {};
  const byAudience = data.by_audience || {};
  const recent = data.recent || [];

  document.getElementById("stats").innerHTML = [
    ["总数", summary.total ?? 0],
    ["成功", summary.ok ?? 0],
    ["Dry Run", summary.dry_run ?? 0],
    ["失败", summary.failed ?? 0]
  ].map(x => `<div class="card"><div class="muted">${x[0]}</div><div style="font-size:28px;font-weight:700;margin-top:8px;">${x[1]}</div></div>`).join("");

  document.getElementById("aud").innerHTML = Object.entries(byAudience).map(([k,v]) =>
    `<div class="item"><b>${k}</b><div class="muted">count: ${v}</div></div>`
  ).join("") || "<div class='muted'>暂无数据</div>";

  document.getElementById("recent").innerHTML = recent.slice(0,20).map(x =>
    `<div class="item"><b>${x.audience || "-"}</b><div class="muted">${x.response_text || "-"}</div><div class="muted">status: ${x.http_status ?? 0} | dry_run: ${x.dry_run ?? 0}</div></div>`
  ).join("") || "<div class='muted'>暂无数据</div>";
})();