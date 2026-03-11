let RAW = [];

function esc(s){
  return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function copyText(text){
  navigator.clipboard.writeText(text).then(()=>alert("已复制检查清单"));
}

function renderSummary(summary){
  const el = document.getElementById("summary");
  const parts = [`<div class="card"><div>总队列</div><strong>${summary.total || 0}</strong></div>`];
  const pri = summary.by_priority || {};
  Object.keys(pri).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${pri[k]}</strong></div>`));
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
        <button data-check='${esc(x.checklist_text)}'>复制清单</button>
      </div>
      <div class="meta">
        <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
        <span class="badge">${esc(x.schedule_bucket)}</span>
        <span class="badge ${String(x.risk_level).toLowerCase()==='safe'?'safe':'review'}">${esc(x.risk_level)}</span>
        <span class="badge">${esc(x.product_type)}</span>
        <span class="badge mono">${esc(x.sku_code)}</span>
      </div>
      <div class="grid">
        <div class="box"><div class="label">Safe Term</div><div>${esc(x.safe_term)}</div></div>
        <div class="box"><div class="label">Operator Note</div><div>${esc(x.operator_note)}</div></div>
        <div class="box" style="grid-column:1/-1">
          <div class="label">Checklist</div>
          <textarea readonly>${x.checklist_text}</textarea>
        </div>
      </div>
    </div>
  `).join("");

  el.querySelectorAll("button[data-check]").forEach(btn=>{
    btn.addEventListener("click", ()=>copyText(btn.getAttribute("data-check")));
  });
}

function applyFilters(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const priority = document.getElementById("priority").value;
  const bucket = document.getElementById("bucket").value;
  const product = document.getElementById("product").value;
  const items = RAW.filter(x=>{
    const hay = [x.title_en, x.sku_code, x.safe_term, x.operator_note].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier !== priority) return false;
    if(bucket && x.schedule_bucket !== bucket) return false;
    if(product && x.product_type !== product) return false;
    return true;
  });
  renderList(items);
}

fetch("/docs/launch_queue_v61.json")
  .then(r=>r.json())
  .then(data=>{
    RAW = data.items || [];
    renderSummary(data.summary || {});
    buildProductOptions(RAW);
    renderList(RAW);
    document.getElementById("q").addEventListener("input", applyFilters);
    document.getElementById("priority").addEventListener("change", applyFilters);
    document.getElementById("bucket").addEventListener("change", applyFilters);
    document.getElementById("product").addEventListener("change", applyFilters);
  })
  .catch(err=>{
    document.getElementById("list").innerHTML = `<div class="item">加载失败：${esc(err.message || err)}</div>`;
  });
