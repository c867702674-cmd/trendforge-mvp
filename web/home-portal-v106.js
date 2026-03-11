fetch('/docs/home_portal_v106.json')
.then(r => r.json())
.then(data => {
  const summary = document.getElementById('summary');
  const sections = document.getElementById('sections');

  const summaryBlocks = data.slice(0, 4);
  let summaryHtml = '';
  summaryBlocks.forEach(x => {
    summaryHtml += `
      <div style="background:#16233d;padding:18px;border-radius:14px;">
        <div style="font-size:15px;color:#9fb3d9;margin-bottom:8px;">${x.block_title}</div>
        <div style="font-size:34px;font-weight:bold;">${x.block_value}</div>
        <div style="margin-top:10px;display:inline-block;background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</div>
      </div>
    `;
  });
  summary.innerHTML = summaryHtml;

  const groupNames = {
    listing: "Listing & Publish",
    ops: "Operations",
    saas: "SaaS System",
    automation: "Automation"
  };

  ["listing", "ops", "saas", "automation"].forEach(group => {
    const rows = data.filter(x => x.block_name === group);
    let groupHtml = `
      <div style="margin-bottom:26px;">
        <div style="font-size:28px;font-weight:bold;margin-bottom:14px;">${groupNames[group]}</div>
    `;

    rows.forEach(x => {
      groupHtml += `
        <div style="background:#16233d;padding:18px;border-radius:14px;margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;">
            <div style="font-size:24px;font-weight:bold;">${x.block_title}</div>
            <div style="display:flex;gap:10px;align-items:center;">
              <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.block_value}</span>
              <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
            </div>
          </div>
          <div style="background:#0d1730;padding:14px;border-radius:10px;margin-top:14px;">
            <div style="color:#9fb3d9;margin-bottom:6px;">BLOCK NOTE</div>
            <div>${x.block_note}</div>
          </div>
        </div>
      `;
    });

    groupHtml += `</div>`;
    sections.innerHTML += groupHtml;
  });
});
