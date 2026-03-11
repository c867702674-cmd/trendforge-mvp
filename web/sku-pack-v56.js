
(async function(){

const res = await fetch('/docs/pod_sku_packs_v56.json',{cache:'no-store'});
const data = await res.json();

const app = document.getElementById("app");

app.innerHTML = data.items.map(x=>`
<div class="card">
<b>${x.term}</b><br>
SKU: ${x.sku_type}<br>
Title: ${x.listing_title}<br>
Prompt: ${x.mj_prompt}
</div>
`).join("");

})();
