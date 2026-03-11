let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总推送项</div><strong>${summary.total || 0}</strong></div>`];
  const byChannel=summary.by_channel || {};
  Object.keys(byChannel).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byChannel[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function cardHtml(x){
  return `<div class="item">
    <strong style="font-size:20px">${esc(x.push_title)}</strong>
    <div class="meta">
      <span class="badge queued">${esc(x.push_status)}</span>
      <span class="badge">${esc(x.target_channel)}</span>
    </div>
    <div class="panel"><div class="label">PUSH BODY</div>${esc(x.push_body).replace(/\\n/g,'<br>')}</div>
    <div class="panel"><div class="label">SCHEDULED AT</div>${esc(x.scheduled_at)}</div>
  </div>`;
}
function renderList(items){
  const el=document.getElementById("list");
  el.innerHTML = items.length ? items.map(cardHtml).join("") : '<div class="item">暂无数据</div>';
}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const channel=document.getElementById("channel").value;
  const status=document.getElementById("status").value;
  const items=RAW.filter(x=>{
    const hay=[x.push_title,x.target_channel,x.push_body].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(channel && x.target_channel!==channel) return false;
    if(status && x.push_status!==status) return false;
    return true;
  });
  renderList(items);
}
fetch("/docs/push_center_v91.json").then(r=>r.json()).then(data=>{
  RAW = data.items || [];
  renderSummary(data.summary || {});
  renderList(RAW);
  document.getElementById("q").addEventListener("input", applyFilters);
  document.getElementById("channel").addEventListener("change", applyFilters);
  document.getElementById("status").addEventListener("change", applyFilters);
}).catch(err=>{
  document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
