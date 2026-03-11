let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function actionCls(v){ if(v==="DO_NOW") return "do"; if(v==="WATCH") return "watch"; return "ignore"; }
function compCls(v){ if(v==="high") return "high"; if(v==="medium") return "medium"; return "low"; }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总趋势项</div><strong>${summary.total || 0}</strong></div>`];
  const bySource=summary.by_source || {};
  Object.keys(bySource).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${bySource[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function cardHtml(x){
  return `<div class="item">
    <strong style="font-size:20px">${esc(x.source_term)}</strong>
    <div class="meta">
      <span class="badge">${esc(x.source_name)}</span>
      <span class="badge ${actionCls(x.action_level)}">${esc(x.action_level)}</span>
      <span class="badge ${compCls(x.competition_level)}">${esc(x.competition_level)}</span>
      <span class="badge">${esc(x.product_type)}</span>
    </div>
    <div class="grid">
      <div class="panel"><div class="label">TREND SCORE</div>${esc(x.trend_score)}</div>
      <div class="panel"><div class="label">GROWTH RATE</div>${esc(x.growth_rate)}</div>
      <div class="panel"><div class="label">SOURCE URL</div><div class="mono">${esc(x.source_url)}</div></div>
      <div class="panel"><div class="label">PAYLOAD</div><div class="mono">${esc(JSON.stringify(x.payload_json || {}))}</div></div>
    </div>
  </div>`;
}
function renderList(items){
  const el=document.getElementById("list");
  el.innerHTML = items.length ? items.map(cardHtml).join("") : '<div class="item">暂无数据</div>';
}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const source=document.getElementById("source").value;
  const action=document.getElementById("action").value;
  const product=document.getElementById("product").value;
  const items=RAW.filter(x=>{
    const hay=[x.source_term,x.source_name].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(source && x.source_name!==source) return false;
    if(action && x.action_level!==action) return false;
    if(product && x.product_type!==product) return false;
    return true;
  });
  renderList(items);
}
fetch("/docs/trend_data_v89.json").then(r=>r.json()).then(data=>{
  RAW = data.items || [];
  renderSummary(data.summary || {});
  renderList(RAW);
  document.getElementById("q").addEventListener("input", applyFilters);
  document.getElementById("source").addEventListener("change", applyFilters);
  document.getElementById("action").addEventListener("change", applyFilters);
  document.getElementById("product").addEventListener("change", applyFilters);
}).catch(err=>{
  document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
