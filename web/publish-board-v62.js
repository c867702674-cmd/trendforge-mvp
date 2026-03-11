let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderSummary(summary){
  const el = document.getElementById("summary");
  const parts = [`<div class="card"><div>总看板</div><strong>${summary.total || 0}</strong></div>`];
  const byCol = summary.by_board_column || {};
  Object.keys(byCol).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byCol[k]}</strong></div>`));
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
  const statusCls = x.publish_status === 'READY' ? 'ready' : (x.publish_status === 'WAIT_ART' ? 'waitart' : 'review');
  return `
    <div class="item">
      <strong>${esc(x.title_en)}</strong>
      <div class="meta">
        <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
        <span class="badge ${statusCls}">${esc(x.publish_status)}</span>
        <span class="badge">${esc(x.product_type)}</span>
      </div>
      <div class="mono">${esc(x.sku_code)}</div>
      <div style="margin-top:8px">${esc(x.safe_term)}</div>
      <div class="note" style="margin-top:8px">${esc(x.publish_note)}</div>
    </div>
  `;
}

function renderBoard(items){
  const ready = items.filter(x=>x.board_column==='READY_TO_PUBLISH').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const art = items.filter(x=>x.board_column==='ARTWORK_PENDING').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  const review = items.filter(x=>x.board_column==='REVIEW_QUEUE').map(cardHtml).join("") || '<div class="item">暂无数据</div>';
  document.getElementById("col-ready").innerHTML = ready;
  document.getElementById("col-art").innerHTML = art;
  document.getElementById("col-review").innerHTML = review;
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const priority = document.getElementById("priority").value;
  const product = document.getElementById("product").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.sku_code, x.safe_term, x.publish_note].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier !== priority) return false;
    if(product && x.product_type !== product) return false;
    return true;
  });
  renderBoard(items);
}

fetch("/docs/publish_board_v62.json")
  .then(r=>r.json())
  .then(data=>{
    RAW = data.items || [];
    renderSummary(data.summary || {});
    buildProductOptions(RAW);
    renderBoard(RAW);
    document.getElementById("q").addEventListener("input", applyFilters);
    document.getElementById("priority").addEventListener("change", applyFilters);
    document.getElementById("product").addEventListener("change", applyFilters);
  })
  .catch(err=>{
    document.getElementById("col-ready").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
  });
