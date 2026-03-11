let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总账号</div><strong>${summary.total || 0}</strong></div>`];
  const byPlan=summary.by_plan || {};
  Object.keys(byPlan).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byPlan[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function cardHtml(x){
  const planCls = x.plan_code || 'free';
  const statusCls = String(x.account_status || '').toLowerCase();
  return `<div class="item">
    <strong style="font-size:20px">${esc(x.username)}</strong>
    <div class="meta">
      <span class="badge ${planCls}">${esc(x.plan_code)}</span>
      <span class="badge ${statusCls}">${esc(x.account_status)}</span>
      <span class="badge">${esc(x.role_code)}</span>
    </div>
    <div class="grid">
      <div class="panel"><div class="label">EMAIL</div>${esc(x.email)}</div>
      <div class="panel"><div class="label">API TOKEN</div><div class="mono">${esc(x.api_token)}</div></div>
      <div class="panel"><div class="label">DAILY TREND LIMIT</div>${esc(x.daily_trend_limit)}</div>
      <div class="panel"><div class="label">PERMISSIONS</div>
        Listing AI: ${x.can_view_listing_ai ? 'YES' : 'NO'}<br>
        MJ Prompt: ${x.can_view_mj_prompt ? 'YES' : 'NO'}<br>
        Command Center: ${x.can_view_command_center ? 'YES' : 'NO'}
      </div>
    </div>
  </div>`;
}
function renderList(items){
  const el=document.getElementById("list");
  el.innerHTML = items.length ? items.map(cardHtml).join("") : '<div class="item">暂无数据</div>';
}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const plan=document.getElementById("plan").value;
  const status=document.getElementById("status").value;
  const items=RAW.filter(x=>{
    const hay=[x.email,x.username,x.api_token].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(plan && x.plan_code!==plan) return false;
    if(status && x.account_status!==status) return false;
    return true;
  });
  renderList(items);
}
fetch("/docs/user_system_v88.json").then(r=>r.json()).then(data=>{
  RAW = data.items || [];
  renderSummary(data.summary || {});
  renderList(RAW);
  document.getElementById("q").addEventListener("input", applyFilters);
  document.getElementById("plan").addEventListener("change", applyFilters);
  document.getElementById("status").addEventListener("change", applyFilters);
}).catch(err=>{
  document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
