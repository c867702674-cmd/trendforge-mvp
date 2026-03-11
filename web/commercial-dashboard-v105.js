fetch('/docs/commercial_dashboard_v105.json')
.then(r => r.json())
.then(data => {
  let html = '';

  data.forEach(x => {
    html += `
      <div style="background:#16233d;padding:20px;margin-bottom:20px;border-radius:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
          <div style="font-size:28px;font-weight:bold;">${x.section_name}</div>
          <div style="display:flex;gap:10px;align-items:center;">
            <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.section_value}</span>
            <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
          </div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-top:14px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">SECTION NOTE</div>
          <div>${x.section_note}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
