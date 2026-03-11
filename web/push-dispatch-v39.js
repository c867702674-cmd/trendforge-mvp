async function load(){
 const r=await fetch('/docs/push_dispatch_v39.json');
 const d=await r.json();
 const el=document.getElementById('app');
 el.innerHTML=d.items.map(x=>`
 <div style="border:1px solid #ccc;margin:10px;padding:10px">
 <b>${x.title}</b><br>
 route:${x.route_name}<br>
 audience:${x.audience}
 </div>`).join('');
}
load();
