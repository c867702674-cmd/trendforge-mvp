#!/bin/bash

echo "Installing TrendForge V117..."

mkdir -p /root/trendforge-mvp/web

cat > /root/trendforge-mvp/web/subscription-v116.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TrendForge Subscription V117</title>
  <style>
    * { box-sizing: border-box; }
    body{
      margin:0;
      font-family:Arial,Helvetica,sans-serif;
      background:linear-gradient(180deg,#06101f 0%, #081224 100%);
      color:#fff;
    }
    .wrap{
      max-width:1280px;
      margin:0 auto;
      padding:36px 24px 72px;
    }
    .top{
      display:flex;
      align-items:flex-start;
      justify-content:space-between;
      gap:20px;
      flex-wrap:wrap;
      margin-bottom:26px;
    }
    .brand{
      font-size:56px;
      font-weight:900;
      line-height:1;
      letter-spacing:.4px;
      margin-bottom:14px;
    }
    .subtitle{
      color:#9db3d9;
      font-size:20px;
      line-height:1.7;
      max-width:860px;
    }
    .top-badge{
      background:#173154;
      color:#dbeaff;
      border:1px solid rgba(120,180,255,.25);
      padding:12px 18px;
      border-radius:999px;
      font-size:15px;
      font-weight:700;
      white-space:nowrap;
    }
    .panel{
      background:#16233d;
      border-radius:24px;
      padding:26px;
      margin-bottom:22px;
      box-shadow:0 10px 30px rgba(0,0,0,.18);
    }
    .section-title{
      font-size:34px;
      font-weight:900;
      margin-bottom:18px;
    }
    .stats{
      display:grid;
      grid-template-columns:repeat(4,minmax(0,1fr));
      gap:16px;
    }
    .stat{
      background:#0c1730;
      border-radius:18px;
      padding:18px 18px 20px;
      min-height:112px;
    }
    .stat-label{
      font-size:14px;
      color:#9db3d9;
      margin-bottom:12px;
    }
    .stat-value{
      font-size:24px;
      font-weight:900;
      line-height:1.25;
      word-break:break-word;
    }
    .status-line{
      margin-top:16px;
      color:#c7d7f5;
      font-size:16px;
    }
    .plans{
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:22px;
      margin-bottom:22px;
    }
    .card{
      background:#16233d;
      border-radius:26px;
      padding:26px;
      border:2px solid transparent;
      box-shadow:0 8px 24px rgba(0,0,0,.16);
      display:flex;
      flex-direction:column;
      position:relative;
      overflow:hidden;
    }
    .card.active{
      border-color:#5da9ff;
      box-shadow:0 0 0 1px rgba(93,169,255,.16) inset, 0 12px 30px rgba(20,60,120,.22);
    }
    .card.recommended{
      border-color:#4f8dff;
      transform:translateY(-4px);
    }
    .recommend{
      position:absolute;
      top:18px;
      right:18px;
      background:#2f8f4e;
      color:#fff;
      padding:8px 14px;
      border-radius:999px;
      font-size:13px;
      font-weight:800;
    }
    .plan-title{
      font-size:34px;
      font-weight:900;
      text-transform:uppercase;
      margin-bottom:12px;
    }
    .current-tag{
      display:inline-block;
      padding:8px 14px;
      border-radius:999px;
      background:#4a9a52;
      font-size:14px;
      font-weight:800;
      margin-bottom:16px;
    }
    .price{
      font-size:52px;
      font-weight:900;
      line-height:1;
      margin-bottom:8px;
    }
    .price small{
      font-size:20px;
      font-weight:600;
      color:#dfe9ff;
    }
    .desc{
      color:#9db3d9;
      font-size:17px;
      line-height:1.7;
      min-height:74px;
      margin-bottom:16px;
    }
    .features{
      list-style:none;
      padding:0;
      margin:0 0 18px 0;
      flex:1;
    }
    .features li{
      padding:10px 0;
      border-bottom:1px solid rgba(255,255,255,.06);
      color:#f0f5ff;
      font-size:17px;
      line-height:1.6;
    }
    .features li:last-child{
      border-bottom:none;
    }
    .btn-row{
      display:flex;
      flex-direction:column;
      gap:12px;
      margin-top:12px;
    }
    .btn{
      border:none;
      border-radius:16px;
      padding:15px 18px;
      font-size:18px;
      font-weight:800;
      cursor:pointer;
      transition:.2s ease;
    }
    .btn:hover{
      transform:translateY(-1px);
    }
    .btn-main{
      background:#fff;
      color:#091325;
    }
    .btn-alt{
      background:#324564;
      color:#fff;
    }
    .btn-pay{
      background:#4f8dff;
      color:#fff;
    }
    .btn[disabled]{
      opacity:.55;
      cursor:not-allowed;
      transform:none;
    }
    .result-panel{
      background:#16233d;
      border-radius:24px;
      padding:26px;
    }
    .result-box{
      background:#0c1730;
      border-radius:18px;
      padding:18px;
      min-height:80px;
      line-height:1.8;
      color:#eef4ff;
      margin-top:14px;
      word-break:break-word;
    }
    .link-box{
      margin-top:16px;
      background:#0c1730;
      border-radius:18px;
      padding:18px;
      word-break:break-all;
      color:#9ecbff;
    }
    .bottom-links{
      margin-top:18px;
      line-height:2;
    }
    .bottom-links a{
      color:#9ecbff;
    }
    @media (max-width: 1100px){
      .plans{ grid-template-columns:1fr; }
      .stats{ grid-template-columns:1fr 1fr; }
      .card.recommended{ transform:none; }
    }
    @media (max-width: 680px){
      .wrap{ padding:22px 14px 50px; }
      .brand{ font-size:40px; }
      .subtitle{ font-size:17px; }
      .section-title{ font-size:28px; }
      .stats{ grid-template-columns:1fr; }
      .price{ font-size:42px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <div class="brand">TrendForge</div>
        <div class="subtitle">
          V117 订阅页美化 + 支付按钮联动版：把套餐展示、升级操作、支付入口预留统一成更接近正式商业版的 SaaS 订阅页面。
        </div>
      </div>
      <div class="top-badge" id="topBadge">Subscription Center</div>
    </div>

    <div class="panel">
      <div class="section-title">当前订阅概览</div>
      <div class="stats">
        <div class="stat">
          <div class="stat-label">当前邮箱</div>
          <div class="stat-value" id="meEmail">加载中...</div>
        </div>
        <div class="stat">
          <div class="stat-label">当前套餐</div>
          <div class="stat-value" id="mePlan">加载中...</div>
        </div>
        <div class="stat">
          <div class="stat-label">当前价格</div>
          <div class="stat-value" id="mePrice">加载中...</div>
        </div>
        <div class="stat">
          <div class="stat-label">每日趋势额度</div>
          <div class="stat-value" id="meLimit">加载中...</div>
        </div>
      </div>
      <div class="status-line" id="statusLine">正在加载当前订阅状态...</div>
    </div>

    <div class="plans">
      <div class="card" id="card-free">
        <div class="plan-title">FREE</div>
        <div class="current-tag" id="tag-free" style="display:none;">当前套餐</div>
        <div class="price">$0 <small>/ month</small></div>
        <div class="desc">适合先体验 TrendForge 的新用户，先注册、先试跑、先理解整套商业闭环。</div>
        <ul class="features">
          <li>每日趋势额度：3</li>
          <li>Listing AI：NO</li>
          <li>MJ Prompt：NO</li>
          <li>Command Center：NO</li>
          <li>适合初次体验账号</li>
        </ul>
        <div class="btn-row">
          <button class="btn btn-alt" id="btn-free" disabled>当前默认套餐</button>
        </div>
      </div>

      <div class="card recommended" id="card-pro">
        <div class="recommend">推荐套餐</div>
        <div class="plan-title">PRO</div>
        <div class="current-tag" id="tag-pro" style="display:none;">当前套餐</div>
        <div class="price">$39 <small>/ month</small></div>
        <div class="desc">适合需要持续上新的 POD 卖家，能直接获得 Listing AI 与 MJ Prompt 能力。</div>
        <ul class="features">
          <li>每日趋势额度：20</li>
          <li>Listing AI：YES</li>
          <li>MJ Prompt：YES</li>
          <li>Command Center：NO</li>
          <li>适合个人高频上新卖家</li>
        </ul>
        <div class="btn-row">
          <button class="btn btn-main" id="btn-upgrade-pro" onclick="changePlan('pro')">升级到 PRO</button>
          <button class="btn btn-pay" onclick="getCheckout('pro')">PRO 支付入口</button>
        </div>
      </div>

      <div class="card" id="card-vip">
        <div class="plan-title">VIP</div>
        <div class="current-tag" id="tag-vip" style="display:none;">当前套餐</div>
        <div class="price">$99 <small>/ month</small></div>
        <div class="desc">适合团队化、批量化、商业版使用场景，具备完整 Command Center 权限。</div>
        <ul class="features">
          <li>每日趋势额度：999</li>
          <li>Listing AI：YES</li>
          <li>MJ Prompt：YES</li>
          <li>Command Center：YES</li>
          <li>适合真正商业化运转用户</li>
        </ul>
        <div class="btn-row">
          <button class="btn btn-main" id="btn-upgrade-vip" onclick="changePlan('vip')">升级到 VIP</button>
          <button class="btn btn-pay" onclick="getCheckout('vip')">VIP 支付入口</button>
        </div>
      </div>
    </div>

    <div class="result-panel">
      <div class="section-title" style="font-size:30px;">操作结果</div>
      <div class="result-box" id="resultBox">等待操作...</div>
      <div class="link-box" id="checkoutBox" style="display:none;"></div>
      <div class="bottom-links">
        <a href="/dashboard-v108.html">返回 Dashboard</a><br/>
        <a href="/index-v107.html">返回首页</a>
      </div>
    </div>
  </div>

  <script>
    function token(){
      return localStorage.getItem("tf_token");
    }

    function clearActiveState(){
      ["free","pro","vip"].forEach(p => {
        document.getElementById("card-" + p).classList.remove("active");
        document.getElementById("tag-" + p).style.display = "none";
      });
      document.getElementById("btn-upgrade-pro").disabled = false;
      document.getElementById("btn-upgrade-vip").disabled = false;
    }

    async function getPlan(){
      const t = token();
      if(!t){
        location.href = "/login-v108.html";
        return null;
      }
      const res = await fetch("/api/plan_v112?token=" + encodeURIComponent(t));
      const data = await res.json();
      if(data.status !== "ok"){
        localStorage.removeItem("tf_token");
        localStorage.removeItem("tf_email");
        localStorage.removeItem("tf_plan");
        location.href = "/login-v108.html";
        return null;
      }
      return data;
    }

    async function renderPage(){
      const data = await getPlan();
      if(!data) return;

      document.getElementById("meEmail").innerText = data.email;
      document.getElementById("mePlan").innerText = data.plan.toUpperCase();
      document.getElementById("mePrice").innerText = data.price;
      document.getElementById("meLimit").innerText = data.daily_limit;
      document.getElementById("topBadge").innerText = "Current Plan: " + data.plan.toUpperCase();
      document.getElementById("statusLine").innerText =
        "当前账号已接入套餐能力、权限判断、升级模拟与支付入口预留。";

      clearActiveState();
      document.getElementById("card-" + data.plan).classList.add("active");
      document.getElementById("tag-" + data.plan).style.display = "inline-block";

      if(data.plan === "pro"){
        document.getElementById("btn-upgrade-pro").disabled = true;
      }
      if(data.plan === "vip"){
        document.getElementById("btn-upgrade-vip").disabled = true;
      }

      document.getElementById("resultBox").innerHTML =
        "当前订阅页已加载完成。<br>你现在可以直接做套餐切换模拟，或点击支付入口按钮查看预留支付链接。";
    }

    async function changePlan(targetPlan){
      const t = token();
      const res = await fetch("/api/change_plan_v114?token=" + encodeURIComponent(t) + "&target_plan=" + encodeURIComponent(targetPlan));
      const data = await res.json();

      if(data.status === "ok"){
        await renderPage();
        document.getElementById("resultBox").innerHTML =
          "套餐切换成功：<b>" + data.plan.toUpperCase() + "</b><br>" +
          "每日趋势额度：" + data.daily_limit + "<br>" +
          "Listing AI：" + (data.listing_ai ? "YES" : "NO") + "<br>" +
          "MJ Prompt：" + (data.mj_prompt ? "YES" : "NO") + "<br>" +
          "Command Center：" + (data.command_center ? "YES" : "NO");
      } else {
        document.getElementById("resultBox").innerText = "套餐切换失败";
      }
    }

    async function getCheckout(targetPlan){
      const t = token();
      const res = await fetch("/api/checkout_link_v115?token=" + encodeURIComponent(t) + "&target_plan=" + encodeURIComponent(targetPlan));
      const data = await res.json();

      if(data.status === "ok"){
        document.getElementById("checkoutBox").style.display = "block";
        document.getElementById("checkoutBox").innerHTML =
          "<b>目标套餐：</b>" + data.target_plan.toUpperCase() + "<br><br>" +
          "<b>预留支付链接：</b><br>" +
          data.checkout_link + "<br><br>" +
          data.note;
        document.getElementById("resultBox").innerHTML =
          "支付入口预留链接已生成。<br>当前还是预留版，下一步可以直接接 Stripe / 微信 / 支付宝。";
      } else {
        document.getElementById("checkoutBox").style.display = "none";
        document.getElementById("resultBox").innerText = "支付入口生成失败";
      }
    }

    renderPage();
  </script>
</body>
</html>
EOF

echo "TrendForge V117 files installed successfully."
