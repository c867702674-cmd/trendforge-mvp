
(async function(){

async function load(){
 const urls=["/docs/push_scheduler_v42.json","../docs/push_scheduler_v42.json"]
 for(const u of urls){
  try{
   const r=await fetch(u,{cache:"no-store"})
   if(r.ok) return await r.json()
  }catch(e){}
 }
 return {items:[]}
}

const data=await load()
const list=document.getElementById("list")

list.innerHTML=(data.items||[]).map(x=>`
<div class="card">
<b>${x.schedule_name}</b>
<div>triggered: ${x.triggered}</div>
<div>${x.created_at}</div>
</div>
`).join("")

})()
