let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderSummary(summary){
  const el = document.getElementById("summary");
  const parts = [`<div class="card"><div>总发布编排中心</div><strong>${summary.total || 0}</strong></div>`];
  const byLane = summary.by_orchestrator_lane || {};
  Object.keys(byLane).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byLane[k]}</strong></div>`));
  el.innerHTML = parts.join("");
}

function buildProductOptions(items){
  const s = document.getElementById("product");
  [...new Set(items.map(x=>x.product_type).filter(Boolean))].sort().forEach(v=>{
    const op = document.createElement("option");
    op.value = v;
    op.textContent = v;
    s.appendChild(op);
  });
}

function cls(lane){
  if(lane === 'ORCHESTRATE_NOW') return 'now';
  if(lane === 'CREATIVE_ORCHESTRATION') return 'creative';
  if(lane === 'POSTER_ORCHESTRATION') return 'poster';
  if(lane === 'RESERVE_ORCHESTRATION') return 'reserve';
  return 'manual';
}

function cardHtml(x){
  return `
    <div class="item">
      <strong>${esc(x.title_en)}</strong>
      <div class="meta">
        <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
        <span class="badge ${cls(x.orchestrator_lane)}">${esc(x.orchestrator_lane)}</span>
        <span class="badge">${esc(x.product_type)}</span>
      </div>
      <div class="mono">${esc(x.sku_code)}</div>
      <div style="margin-top:8px">${esc(x.safe_term)}</div>
      <div class="note" style="margin-top:8px">${esc(x.orchestrator_action)}</div>
    </div>
  `;
}

function renderGrid(items){
  const mapping = {
    'ORCHESTRATE_NOW':'col-now',
    'CREATIVE_ORCHESTRATION':'col-creative',
    'POSTER_ORCHESTRATION':'col-poster',
    'RESERVE_ORCHESTRATION':'col-reserve',
    'MANUAL_ORCHESTRATION':'col-manual',
  };
  Object.values(mapping).forEach(id => document.getElementById(id).innerHTML = '<div class="item">暂无数据</div>');
  for (const [group, id] of Object.entries(mapping)) {
    const html = items.filter(x=>x.orchestrator_lane===group).map(cardHtml).join("");
    if (html) document.getElementById(id).innerHTML = html;
  }
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const priority = document.getElementById("priority").value;
  const product = document.getElementById("product").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.sku_code, x.safe_term, x.orchestrator_action].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier !== priority) return false;
    if(product && x.product_type !== product) return false;
    return true;
  });
  renderGrid(items);
}

fetch("/docs/launch_orchestrator_v76.json")
  .then(r=>r.json())
  .then(data=>{
    RAW = data.items || [];
    renderSummary(data.summary || {});
    buildProductOptions(RAW);
    renderGrid(RAW);
    document.getElementById("q").addEventListener("input", applyFilters);
    document.getElementById("priority").addEventListener("change", applyFilters);
    document.getElementById("product").addEventListener("change", applyFilters);
  })
  .catch(err=>{
    document.getElementById("col-now").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
  });
