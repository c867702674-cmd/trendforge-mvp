(async function(){

async function load(){
  const urls = [
    "/docs/main_index_v53.json",
    "../docs/main_index_v53.json"
  ];

  for(const u of urls){
    try{
      const r = await fetch(u,{cache:"no-store"});
      if(r.ok) return await r.json();
    }catch(e){}
  }
  return {};
}

const data = await load();

const hero = data.hero || {};
document.getElementById("title").textContent = hero.title || "TrendForge";
document.getElementById("subtitle").textContent = hero.subtitle || "-";
document.getElementById("tagline").textContent = hero.tagline || "-";

const pricing = data.pricing || [];
document.getElementById("pricing").innerHTML =
pricing.map(x=>`
<div class="card">
<div class="badge">${x.plan}</div>
<div class="price">${x.price_usd}</div>
<div class="subprice">${x.price_cny}</div>
${(x.features||[]).map(f=>`<div class="item">${f}</div>`).join("")}
</div>
`).join("");

const topItems = data.top_items || [];
document.getElementById("top").innerHTML =
topItems.map(x=>`
<div class="item">
<b>${x.term}</b>
<div class="muted">
score:${x.trend_power_score} profit:${x.profit_score}
</div>
</div>
`).join("");

const runtime = data.runtime || {};
document.getElementById("runtime").innerHTML = `
<div class="item">Push Total ${runtime.total||0}</div>
<div class="item">Push OK ${runtime.ok||0}</div>
<div class="item">Dry Run ${runtime.dry_run||0}</div>
`;

})();
