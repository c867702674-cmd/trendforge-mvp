fetch('/docs/homepage_v107.json')
  .then(r => r.json())
  .then(data => {
    const hero = data.find(x => x.section_key === 'hero');
    const metrics = data.filter(x => x.section_key === 'metric');
    const features = data.filter(x => x.section_key === 'feature');
    const plans = data.filter(x => x.section_key === 'plan');
    const cta = data.find(x => x.section_key === 'cta');

    const metricHtml = metrics.map(x => `
      <div style="background:#16233d;border-radius:18px;padding:24px;">
        <div style="font-size:16px;color:#9fb3d9;margin-bottom:12px;">${x.section_title}</div>
        <div style="font-size:42px;font-weight:bold;margin-bottom:12px;">${x.section_value}</div>
        <div style="display:inline-block;background:#215732;padding:6px 12px;border-radius:999px;margin-bottom:14px;">${x.status}</div>
        <div style="color:#d7def0;line-height:1.7;">${x.section_desc}</div>
      </div>
    `).join('');

    const featureHtml = features.map(x => `
      <div style="background:#16233d;border-radius:18px;padding:24px;">
        <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px;">
          <div style="font-size:26px;font-weight:bold;">${x.section_title}</div>
          <div style="background:#2a3b5f;padding:6px 12px;border-radius:999px;">${x.section_value}</div>
        </div>
        <div style="color:#d7def0;line-height:1.8;">${x.section_desc}</div>
      </div>
    `).join('');

    const planHtml = plans.map(x => `
      <div style="background:#16233d;border-radius:18px;padding:24px;flex:1;min-width:240px;">
        <div style="font-size:28px;font-weight:bold;margin-bottom:8px;">${x.section_title}</div>
        <div style="font-size:36px;font-weight:bold;margin-bottom:12px;color:#fff;">${x.section_value}</div>
        <div style="color:#d7def0;line-height:1.8;">${x.section_desc}</div>
      </div>
    `).join('');

    document.getElementById('app').innerHTML = `
      <div style="max-width:1320px;margin:0 auto;padding:34px 24px 60px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;margin-bottom:28px;">
          <div style="font-size:34px;font-weight:bold;">TrendForge</div>
          <div style="color:#9fb3d9;font-size:16px;">北美 POD 趋势商业版</div>
        </div>

        <div style="background:linear-gradient(135deg,#142441,#1b3158);border-radius:24px;padding:34px;margin-bottom:28px;">
          <div style="font-size:18px;color:#9fb3d9;margin-bottom:10px;">正式首页整合版</div>
          <div style="font-size:56px;font-weight:bold;line-height:1.15;margin-bottom:18px;">${hero.section_title}</div>
          <div style="font-size:22px;color:#fff;margin-bottom:12px;">当前趋势引擎数据量：${hero.section_value}</div>
          <div style="max-width:920px;color:#d7def0;line-height:1.9;font-size:18px;margin-bottom:24px;">${hero.section_desc}</div>
          <div style="display:flex;gap:14px;flex-wrap:wrap;">
            <div style="background:#215732;padding:12px 18px;border-radius:999px;font-weight:bold;">${hero.status}</div>
            <div style="background:#2a3b5f;padding:12px 18px;border-radius:999px;">趋势 → Prompt → Mockup → Listing → 发布</div>
          </div>
        </div>

        <div style="font-size:36px;font-weight:bold;margin:20px 0 18px;">核心指标</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-bottom:34px;">
          ${metricHtml}
        </div>

        <div style="font-size:36px;font-weight:bold;margin:20px 0 18px;">核心能力</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-bottom:34px;">
          ${featureHtml}
        </div>

        <div style="font-size:36px;font-weight:bold;margin:20px 0 18px;">套餐建议</div>
        <div style="display:flex;gap:18px;flex-wrap:wrap;margin-bottom:34px;">
          ${planHtml}
        </div>

        <div style="background:#16233d;border-radius:24px;padding:30px;">
          <div style="font-size:34px;font-weight:bold;margin-bottom:14px;">${cta.section_title}</div>
          <div style="font-size:22px;margin-bottom:12px;">${cta.section_value}</div>
          <div style="color:#d7def0;line-height:1.8;margin-bottom:20px;">${cta.section_desc}</div>
          <div style="display:flex;gap:14px;flex-wrap:wrap;">
            <a href="/home-portal-v106.html" style="text-decoration:none;background:#215732;color:#fff;padding:12px 18px;border-radius:999px;font-weight:bold;">进入统一门户</a>
            <a href="/commercial-dashboard-v105.html" style="text-decoration:none;background:#2a3b5f;color:#fff;padding:12px 18px;border-radius:999px;font-weight:bold;">查看商业总览</a>
          </div>
        </div>
      </div>
    `;
  });
