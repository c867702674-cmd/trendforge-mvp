
fetch('/docs/risk_ip_scan_v58.json')
.then(r=>r.json())
.then(data=>{
  document.getElementById('app').innerText = JSON.stringify(data.summary, null, 2);
});
