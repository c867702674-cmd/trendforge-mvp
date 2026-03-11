let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总自动化任务</div><strong>${summary.total || 0}</strong></div>`];
  const byRule=summary.by_rule || {};
  Object.keys(byRule).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byRule[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function cardHtml(x){
  return `<div class="item">
    <strong style="font-size:20px">${esc(x.rule_code)}</strong>
    <div class="meta">
      <span class="badge pending">${esc(x.job_status)}</span>
      <span class="badge">${esc(x.target_channel)}</span>
    </div>
    <div class="panel"><div class="label">RESULT NOTE</div>${esc(x.result_note)}</div>
    <div class="panel"><div class="label">EXECUTE AT</div>${esc(x.execute_at)}</div>
  </div>`;
}
function renderList(items){
  const el=document.getElementById("list");
  el.innerHTML = items.length ? items.map(cardHtml).join("") : '<div class="item">暂无数据</div>';
}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const rule=document.getElementById("rule").value;
  const channel=document.getElementById("channel").value;
  const status=document.getElementById("status").value;
  const items=RAW.filter(x=>{
    const hay=[x.rule_code,x.target_channel,x.result_note].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(rule && x.rule_code!==rule) return false;
    if(channel && x.target_channel!==channel) return false;
    if(status && x.job_status!==status) return false;
    return true;
  });
  renderList(items);
}
fetch("/docs/automation_hub_v92.json").then(r=>r.json()).then(data=>{
  RAW = data.items || [];
  renderSummary(data.summary || {});
  renderList(RAW);
  document.getElementById("q").addEventListener("input", applyFilters);
  document.getElementById("rule").addEventListener("change", applyFilters);
  document.getElementById("channel").addEventListener("change", applyFilters);
  document.getElementById("status").addEventListener("change", applyFilters);
}).catch(err=>{
  document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
