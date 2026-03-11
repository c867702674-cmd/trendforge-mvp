fetch('/docs/publish_pack_v102.json')
.then(r => r.json())
.then(data => {
  let html = '';

  data.forEach(x => {
    html += `
      <div style="background:#16233d;padding:20px;margin-bottom:20px;border-radius:14px;">
        <div style="font-size:28px;font-weight:bold;margin-bottom:16px;">
          ${x.source_term}
        </div>

        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
          <span style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.product_type}</span>
          <span style="background:#215732;padding:6px 12px;border-radius:999px;">${x.status}</span>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PUBLISH TITLE</div>
          <div>${x.publish_title}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PUBLISH SUBTITLE</div>
          <div>${x.publish_subtitle}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">PUBLISH CHECKLIST</div>
          <div>${x.publish_checklist}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">MARKETPLACE NOTE</div>
          <div>${x.marketplace_note}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;margin-bottom:12px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">FINAL PUBLISH PACK</div>
          <div>${x.final_publish_pack}</div>
        </div>

        <div style="background:#0d1730;padding:14px;border-radius:10px;">
          <div style="color:#9fb3d9;margin-bottom:6px;">OPERATOR ACTION</div>
          <div>${x.operator_action}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('app').innerHTML = html;
});
