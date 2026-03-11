let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderSummary(summary){
  const box = document.getElementById("summary");
  const byType = summary.by_product_type || {};
  const parts = [`<div class="card"><div>总 Listing</div><strong>${summary.total || 0}</strong></div>`];
  Object.keys(byType).sort().forEach(k=>{
    parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byType[k]}</strong></div>`);
  });
  box.innerHTML = parts.join("");
}

function buildProductOptions(items){
  const s = document.getElementById("product");
  const set = [...new Set(items.map(x=>x.product_type).filter(Boolean))].sort();
  set.forEach(v=>{
    const op = document.createElement("option");
    op.value = v;
    op.textContent = v;
    s.appendChild(op);
  });
}

function renderList(items){
  const el = document.getElementById("list");
  if(!items.length){
    el.innerHTML = `<div class="item">没有匹配结果</div>`;
    return;
  }
  el.innerHTML = items.map(x=>`
    <div class="item">
      <h3>${esc(x.title_en)}</h3>
      <div class="meta">
        <span class="badge ${String(x.risk_level).toLowerCase()==='safe'?'safe':'review'}">${esc(x.risk_level)}</span>
        <span class="badge">${esc(x.product_type)}</span>
        <span class="badge">score ${esc(x.listing_score)}</span>
      </div>
      <div class="grid">
        <div class="box"><div class="label">Source Term</div><div>${esc(x.source_term)}</div></div>
        <div class="box"><div class="label">Safe Term</div><div>${esc(x.safe_term)}</div></div>
        <div class="box"><div class="label">Tags</div><div>${esc(x.tags_en)}</div></div>
        <div class="box"><div class="label">SKU</div><div class="mono">${esc(x.sku_code)}</div></div>
        <div class="box"><div class="label">Bullets</div><div style="white-space:pre-line">${esc(x.bullets_en)}</div></div>
        <div class="box"><div class="label">Design Prompt</div><div>${esc(x.design_prompt_en)}</div></div>
        <div class="box" style="grid-column:1/-1"><div class="label">Description</div><div>${esc(x.description_en)}</div></div>
      </div>
    </div>
  `).join("");
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const product = document.getElementById("product").value;
  const risk = document.getElementById("risk").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.safe_term, x.source_term, x.tags_en, x.sku_code].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(product && x.product_type !== product) return false;
    if(risk && x.risk_level !== risk) return false;
    return true;
  });
  renderList(items);
}

fetch("/docs/listing_v59.json")
  .then(r=>r.json())
  .then(data=>{
    RAW = data.items || [];
    renderSummary(data.summary || {});
    buildProductOptions(RAW);
    renderList(RAW);
    document.getElementById("q").addEventListener("input", applyFilters);
    document.getElementById("product").addEventListener("change", applyFilters);
    document.getElementById("risk").addEventListener("change", applyFilters);
  })
  .catch(err=>{
    document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
  });
