let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderSummary(summary){
  const el = document.getElementById("summary");
  const parts = [`<div class="card"><div>总指挥中心</div><strong>${summary.total || 0}</strong></div>`];
  const byLane = summary.by_lane || {};
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

function laneClass(lane){
  if(lane === 'EXECUTE_FIRST') return 'exec';
  if(lane === 'ART_FACTORY') return 'art';
  if(lane === 'POSTER_LAB') return 'poster';
  return 'hold';
}

function cardHtml(x){
  return `
    <div class="item">
      <strong>${esc(x.title_en)}</strong>
      <div class="meta">
        <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
        <span class="badge ${laneClass(x.commander_lane)}">${esc(x.commander_lane)}</span>
        <span class="badge">${esc(x.product_type)}</span>
      </div>
      <div class="mono">${esc(x.sku_code)}</div>
      <div style="margin-top:8px">${esc(x.safe_term)}</div>
      <div class="note" style="margin-top:8px">${esc(x.commander_action)}</div>
    </div>
  `;
}

function renderGrid(items){
  const exec = items.filter(x=>x.commander_lane==='EXECUTE_FIRST').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const art = items.filter(x=>x.commander_lane==='ART_FACTORY').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const poster = items.filter(x=>x.commander_lane==='POSTER_LAB').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const hold = items.filter(x=>x.commander_lane==='REVIEW_HOLD').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  document.getElementById("col-exec").innerHTML = exec;
  document.getElementById("col-art").innerHTML = art;
  document.getElementById("col-poster").innerHTML = poster;
  document.getElementById("col-hold").innerHTML = hold;
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const priority = document.getElementById("priority").value;
  const product = document.getElementById("product").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.sku_code, x.safe_term, x.commander_action].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier !== priority) return false;
    if(product && x.product_type !== product) return false;
    return true;
  });
  renderGrid(items);
}

fetch("/docs/command_center_v64.json")
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
    document.getElementById("col-exec").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
  });
