let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function cls(v){ if(v==="PUSHED") return "pushed"; if(v==="FAILED") return "failed"; return "skipped"; }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总卡片推送</div><strong>${summary.total || 0}</strong></div>`];
  const byStatus=summary.by_status || {};
  Object.keys(byStatus).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byStatus[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function cardHtml(x){
  return `<div class="item">
    <strong style="font-size:20px">${esc(x.card_title)}</strong>
    <div class="meta">
      <span class="badge ${cls(x.send_status)}">${esc(x.send_status)}</span>
      <span class="badge">${esc(x.target_channel)}</span>
    </div>
    <div class="panel"><div class="label">RESPONSE</div>${esc(x.response_text)}</div>
    <div class="panel"><div class="label">SENT AT</div>${esc(x.sent_at)}</div>
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
    const hay=[x.card_title,x.response_text,x.target_channel].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(channel && x.target_channel!==channel) return false;
    if(status && x.send_status!==status) return false;
    return true;
  });
  renderList(items);
}
fetch("/docs/feishu_card_v95.json").then(r=>r.json()).then(data=>{
  RAW = data.items || [];
  renderSummary(data.summary || {});
  renderList(RAW);
  document.getElementById("q").addEventListener("input", applyFilters);
  document.getElementById("channel").addEventListener("change", applyFilters);
  document.getElementById("status").addEventListener("change", applyFilters);
}).catch(err=>{
  document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
