(async function(){
  async function load(){
    const urls = ["/docs/seller_flow_v35.json","../docs/seller_flow_v35.json"];
    for(const u of urls){
      try{
        const r = await fetch(u,{cache:"no-store"});
        if(r.ok) return await r.json();
      }catch(e){}
    }
    return {};
  }
  function put(id, html){ const el=document.getElementById(id); if(el) el.innerHTML = html; }
  const data = await load();
  put("meta", `更新时间：${data.generated_at || "-"}`);
  const cards = data.cards || [];
  const alerts = data.alerts || [];
  const subs = data.subscription || [];
  put("cards", cards.slice(0,8).map(x=>`<div class="item"><b>${x.card_title || x.term || "-"}</b><div class="muted">${x.card_subtitle || "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("alerts", alerts.slice(0,8).map(x=>`<div class="item"><b>${x.alert_title || "-"}</b><div class="muted">${x.alert_text || "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
  put("subs", subs.slice(0,5).map(x=>`<div class="item"><b>${x.user_email || "-"}</b><div class="muted">plan: ${x.plan || "-"} | status: ${x.status || "-"}</div></div>`).join("") || "<div class='muted'>暂无数据</div>");
})();