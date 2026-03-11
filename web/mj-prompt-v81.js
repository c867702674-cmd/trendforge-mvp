let RAW = [];
function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function riskCls(v){ if(v==="SAFE") return "safe"; if(v==="REVIEW") return "review"; return "block"; }
function renderSummary(summary){
  const el=document.getElementById("summary");
  const parts=[`<div class="card"><div>总 Prompt</div><strong>${summary.total || 0}</strong></div>`];
  const byProduct=summary.by_product_type || {};
  Object.keys(byProduct).sort().forEach(k=>parts.push(`<div class="card"><div>${esc(k)}</div><strong>${byProduct[k]}</strong></div>`));
  el.innerHTML=parts.join("");
}
function buildProductOptions(items){
  const s=document.getElementById("product");
  [...new Set(items.map(x=>x.product_type).filter(Boolean))].sort().forEach(v=>{
    const op=document.createElement("option"); op.value=v; op.textContent=v; s.appendChild(op);
  });
}
function cardHtml(x){
  return `<div class="item">
    <strong style="font-size:20px">${esc(x.title_en)}</strong>
    <div class="meta">
      <span class="badge ${String(x.priority_tier).toLowerCase()}">${esc(x.priority_tier)}</span>
      <span class="badge ${riskCls(x.risk_level)}">${esc(x.risk_level)}</span>
      <span class="badge">${esc(x.product_type)}</span>
      <span class="badge mono">${esc(x.sku_code)}</span>
    </div>
    <div class="grid">
      <div class="panel"><div class="label">SAFE TERM</div>${esc(x.safe_term)}</div>
      <div class="panel"><div class="label">DESIGN STYLE</div>${esc(x.design_style)}</div>
      <div class="panel"><div class="label">MJ PROMPT</div><div class="desc">${esc(x.mj_prompt)}</div></div>
      <div class="panel"><div class="label">NEGATIVE PROMPT</div><div class="desc">${esc(x.negative_prompt)}</div></div>
      <div class="panel"><div class="label">MOCKUP PROMPT</div><div class="desc">${esc(x.mockup_prompt)}</div></div>
    </div>
  </div>`;
}
function renderList(items){
  const el=document.getElementById("list");
  el.innerHTML=items.length?items.map(cardHtml).join(""):'<div class="item">暂无数据</div>';
}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const priority=document.getElementById("priority").value;
  const product=document.getElementById("product").value;
  const risk=document.getElementById("risk").value;
  const items=RAW.filter(x=>{
    const hay=[x.title_en,x.sku_code,x.safe_term,x.mj_prompt,x.mockup_prompt].join(" ").toLowerCase();
    if(q && !hay.includes(q)) return false;
    if(priority && x.priority_tier!==priority) return false;
    if(product && x.product_type!==product) return false;
    if(risk && x.risk_level!==risk) return false;
    return true;
  });
  renderList(items);
}
fetch("/docs/mj_prompt_v81.json").then(r=>r.json()).then(data=>{
  RAW=data.items || [];
  renderSummary(data.summary || {});
  buildProductOptions(RAW);
  renderList(RAW);
  document.getElementById("q").addEventListener("input",applyFilters);
  document.getElementById("priority").addEventListener("change",applyFilters);
  document.getElementById("product").addEventListener("change",applyFilters);
  document.getElementById("risk").addEventListener("change",applyFilters);
}).catch(err=>{
  document.getElementById("list").innerHTML=`<div class="item">加载失败：${esc(err.message || err)}</div>`;
});
