fetch('/docs/execution_engine_v93.json')
.then(r=>r.json())
.then(data=>{
 let html='';
 data.items.forEach(x=>{
  html+=`<div class="item">
  <strong>${x.rule_code}</strong><br>
  Channel: ${x.target_channel}<br>
  Status: <span class="badge">${x.execution_status}</span><br>
  Executed: ${x.executed_at}<br>
  Log: ${x.execution_log}
  </div>`
 });
 document.getElementById('list').innerHTML=html;
});
