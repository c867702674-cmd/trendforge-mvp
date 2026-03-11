let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function riskCls(v){ if(v==="SAFE") return "safe"; if(v==="REVIEW") return "review"; return "block"; }
function statusCls(v){ return v==="ACTIVE" ? "active" : "waiting"; }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总指挥中心项</div><strong>${summary.total || 0}</strong></div>`];
  const byLane=summary.by_center_lane || {};
  Object.keys(byLane).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byLane[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function cardHtml(x){
  return `<div class="item">
    <strong>${esc(x.title_en)}</strong>
    <div class="meta">
      <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
      <span class="badge ${riskCls(x.risk_level)}">${esc(x.risk_level)}</span>
      <span class="badge ${statusCls(x.center_status)}">${esc(x.center_status)}</span>
      <span class="badge">${esc(x.owner_role)}</span>
    </div>
    <div class="mono">${esc(x.sku_code)}</div>
    <div style="margin-top:8px">${esc(x.center_module)}</div>
    <div class="note" style="margin-top:8px">${esc(x.summary_text)}</div>
    <div class="note" style="margin-top:8px"><strong>Blocker:</strong> ${esc(x.blocker_text)}</div>
    <div class="note" style="margin-top:8px"><strong>Next:</strong> ${esc(x.next_action)}</div>
  </div>`;
}
function renderGrid(items){
  const mapping={LAUNCH_CENTER:"col-launch",ASSET_CENTER:"col-asset",COMPLIANCE_CENTER:"col-compliance",POSTER_CENTER:"col-poster",MANUAL_CENTER:"col-manual"};
  Object.values(mapping).forEach(id=>document.getElementById(id).innerHTML='<div class="item">暂无数据</div>');
  for(const [group,id] of Object.entries(mapping)){
    const html=items.filter(x=>x.center_lane===group).map(cardHtml).join("");
    if(html) document.getElementById(id).innerHTML=html;
  }
}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const priority=document.getElementById("priority").value;
  const status=document.getElementById("status").value;
  const owner=document.getElementById("owner").value;
  const items=RAW.filter(x=>{
    const hay=[x.title_en,x.sku_code,x.safe_term,x.summary_text,x.blocker_text,x.next_action,x.center_module].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier!==priority) return false;
    if(status && x.center_status!==status) return false;
    if(owner && x.owner_role!==owner) return false;
    return true;
  });
  renderGrid(items);
}
fetch("/docs/command_center_v87.json").then(r=>r.json()).then(data=>{
  RAW=data.items || [];
  renderSummary(data.summary || {});
  renderGrid(RAW);
  document.getElementById("q").addEventListener("input",applyFilters);
  document.getElementById("priority").addEventListener("change",applyFilters);
  document.getElementById("status").addEventListener("change",applyFilters);
  document.getElementById("owner").addEventListener("change",applyFilters);
}).catch(err=>{
  document.getElementById("col-launch").innerHTML=`<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
