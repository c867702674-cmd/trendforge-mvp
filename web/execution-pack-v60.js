let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderSummary(summary){
  const box = document.getElementById("summary");
  const parts = [`<div class="card"><div>总执行包</div><strong>${summary.total || 0}</strong></div>`];
  const byType = summary.by_product_type || {};
  Object.keys(byType).sort().forEach(k=>{
    parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byType[k]}</strong></div>`);
  });
  box.innerHTML = parts.join("");
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

function copyText(text){
  navigator.clipboard.writeText(text).then(()=>alert("已复制执行包"));
}

function renderList(items){
  const el = document.getElementById("list");
  if(!items.length){
    el.innerHTML = `<div class="item">没有匹配结果</div>`;
    return;
  }
  el.innerHTML = items.map(x=>`
    <div class="item">
      <div class="row">
        <h3 style="margin:0">${esc(x.title_en)}</h3>
        <button onclick='copyText(${JSON.stringify("").slice(0,2)}${""})' style="display:none"></button>
      </div>
      <div class="meta">
        <span class="badge ${String(x.risk_level).toLowerCase()==='safe'?'safe':'review'}">${esc(x.risk_level)}</span>
        <span class="badge">${esc(x.product_type)}</span>
        <span class="badge">score ${esc(x.pack_score)}</span>
        <span class="badge mono">${esc(x.sku_code)}</span>
      </div>
      <div class="grid">
        <div class="box"><div class="label">Safe Term</div><div>${esc(x.safe_term)}</div></div>
        <div class="box"><div class="label">Tags</div><div>${esc(x.tags_en)}</div></div>
        <div class="box" style="grid-column:1/-1">
          <div class="row">
            <div class="label">Execution Pack</div>
            <button data-pack='${esc(x.execution_pack_text)}'>复制执行包</button>
          </div>
          <textarea readonly>${x.execution_pack_text}</textarea>
        </div>
      </div>
    </div>
  `).join("");

  el.querySelectorAll("button[data-pack]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      copyText(btn.getAttribute("data-pack"));
    });
  });
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const product = document.getElementById("product").value;
  const risk = document.getElementById("risk").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.safe_term, x.tags_en, x.sku_code, x.execution_pack_text].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(product && x.product_type !== product) return false;
    if(risk && x.risk_level !== risk) return false;
    return true;
  });
  renderList(items);
}

fetch("/docs/execution_pack_v60.json")
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
