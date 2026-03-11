let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderSummary(summary){
  const el = document.getElementById("summary");
  const parts = [`<div class="card"><div>总运营面板</div><strong>${summary.total || 0}</strong></div>`];
  const byStage = summary.by_ops_stage || {};
  Object.keys(byStage).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byStage[k]}</strong></div>`));
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

function cardHtml(x){
  let cls = 'review';
  if (x.ops_stage === 'QUEUE_NOW') cls = 'queue';
  else if (x.ops_stage === 'MAKE_ART') cls = 'art';
  return `
    <div class="item">
      <strong>${esc(x.title_en)}</strong>
      <div class="meta">
        <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
        <span class="badge ${cls}">${esc(x.ops_stage)}</span>
        <span class="badge">${esc(x.product_type)}</span>
      </div>
      <div class="mono">${esc(x.sku_code)}</div>
      <div style="margin-top:8px">${esc(x.safe_term)}</div>
      <div class="note" style="margin-top:8px">${esc(x.action_hint)}</div>
    </div>
  `;
}

function renderGrid(items){
  const q = items.filter(x=>x.ops_stage==='QUEUE_NOW').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const a = items.filter(x=>x.ops_stage==='MAKE_ART').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const r = items.filter(x=>x.ops_stage!=='QUEUE_NOW' && x.ops_stage!=='MAKE_ART').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  document.getElementById("col-queue").innerHTML = q;
  document.getElementById("col-art").innerHTML = a;
  document.getElementById("col-review").innerHTML = r;
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const priority = document.getElementById("priority").value;
  const product = document.getElementById("product").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.sku_code, x.safe_term, x.action_hint].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier !== priority) return false;
    if(product && x.product_type !== product) return false;
    return true;
  });
  renderGrid(items);
}

fetch("/docs/ops_dashboard_v63.json")
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
    document.getElementById("col-queue").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
  });
