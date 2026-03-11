fetch('/docs/listing_draft_v96.json')
.then(r=>r.json())
.then(data=>{

let html=""

data.forEach(x=>{

html+=`
<div style="background:#1b2a44;padding:20px;margin-bottom:20px;border-radius:10px">
<b>${x.title}</b><br>
Product: ${x.product_type}<br>
SKU: ${x.sku}<br>
Tags: ${x.tags}<br>
<p>${x.description}</p>
</div>
`

})

document.getElementById("app").innerHTML=html

})
