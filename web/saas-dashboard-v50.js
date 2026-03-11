(async function(){
  async function load(){
    const urls = ["/docs/saas_dashboard_v50.json","../docs/saas_dashboard_v50.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {summary:{}, top_items:[]};
  }
  const data = await load();
  const s = data.summary || {};
  document.getElementById("stats").innerHTML = [
    ["总趋势", s.total ?? 0],
    ["DO_NOW", s.do_now ?? 0],
    ["FAST_FOLLOW", s.fast_follow ?? 0],
    ["WATCH", s.watch ?? 0],
    ["AVOID", s.avoid ?? 0],
  ].map(x => `<div class="card"><div class="muted">${x[0]}</div><div style="font-size:28px;font-weight:700;margin-top:8px;">${x[1]}</div></div>`).join("");

  const items = data.top_items || [];
  document.getElementById("list").innerHTML = items.map(x => `
    <div class="item">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;">
        <b>${x.term || "-"}</b>
        <span class="badge">${x.decision_level || "-"}</span>
      </div>
      <div class="muted" style="margin-top:8px;">trend_power_score: ${x.trend_power_score ?? "-"} | profit: ${x.profit_score ?? "-"} | competition: ${x.competition_score ?? "-"}</div>
      <div class="muted" style="margin-top:8px;">${x.design_direction || "-"}</div>
    </div>
  `).join("") || "<div class='muted'>暂无数据</div>";
})();