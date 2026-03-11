#!/bin/bash

echo "Installing TrendForge V116..."

mkdir -p /root/trendforge-mvp/web

cat > /root/trendforge-mvp/web/subscription-v116.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>TrendForge Subscription V116</title>
  <style>
    * { box-sizing: border-box; }
    body{
      margin:0;
      font-family:Arial,Helvetica,sans-serif;
      background:#071224;
      color:#fff;
    }
    .wrap{
      max-width:1200px;
      margin:0 auto;
      padding:40px 24px 80px;
    }
    .topbar{
      display:flex;
      justify-content:space-between;
      align-items:center;
      margin-bottom:28px;
      gap:16px;
      flex-wrap:wrap;
    }
    .brand{
      font-size:44px;
      font-weight:800;
      letter-spacing:.5px;
    }
    .sub{
      color:#9db3d9;
      font-size:20px;
      margin-top:8px;
      line-height:1.6;
    }
    .panel{
      background:#16233d;
      border-radius:22px;
      padding:24px;
      margin-bottom:24px;
    }
    .current{
      display:grid;
      grid-template-columns:repeat(4,minmax(0,1fr));
      gap:16px;
      margin-top:18px;
    }
    .stat{
      background:#0d1730;
      border-radius:18px;
      padding:18px;
    }
    .stat .label{
      color:#9db3d9;
      font-size:15px;
      margin-bottom:10px;
    }
    .stat .value{
      font-size:28px;
      font-weight:800;
    }
    .plans{
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:20px;
      margin-top:14px;
    }
    .plan-card{
      background:#16233d;
      border-radius:24px;
      padding:24px;
      border:2px solid transparent;
      min-height:540px;
      display:flex;
      flex-direction:column;
    }
    .plan-card.active{
      border-color:#4ea1ff;
      box-shadow:0 0 0 1px rgba(78,161,255,.15) inset;
    }
    .plan-name{
      font-size:34px;
      font-weight:800;
      margin-bottom:10px;
      text-transform:uppercase;
    }
    .badge{
      display:inline-block;
      padding:8px 14px;
      border-radius:999px;
      background:#2f8f4e;
      font-size:14px;
      font-weight:700;
      margin-bottom:18px;
    }
    .price{
      font-size:38px;
      font-weight:900;
      margin-bottom:12px;
    }
    .price-sub{
      color:#9db3d9;
      margin-bottom:20px;
      min-height:24px;
    }
    .feature-list{
      margin:0;
      padding-left:20px;
      line-height:1.9;
      color:#f4f7ff;
      flex:1;
    }
    .feature-list li{
      margin-bottom:4px;
    }
    .btn{
      border:none;
      border-radius:14px;
      padding:14px 18px;
      font-size:17px;
      font-weight:700;
      cursor:pointer;
      margin-top:18px;
    }
    .btn-primary{
      background:#ffffff;
      color:#091325;
    }
    .btn-secondary{
      background:#324564;
      color:#fff;
    }
    .btn[disabled]{
      opacity:.55;
      cursor:not-allowed;
    }
    .result{
      margin-top:22px;
      background:#0d1730;
      border-radius:18px;
      padding:18px;
      line-height:1.8;
      color:#eef4ff;
      min-height:68px;
    }
    .links{
      margin-top:18px;
      line-height:2;
    }
    .links a{
      color:#9ecbff;
    }
    @media (max-width: 980px){
      .plans{ grid-template-columns:1fr; }
      .current{ grid-template-columns:1fr 1fr; }
    }
    @media (max-width: 640px){
      .brand{ font-size:34px; }
      .current{ grid-template-columns:1fr; }
      .wrap{ padding:24px 16px 50px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <div class="brand">TrendForge</div>
        <div class="sub">V116 订阅页 UI 升级版：把商业套餐做成真正可展示的 SaaS 订阅页面。</div>
      </div>
    </div>

    <div class="panel">
      <div style="font-size:30px;font-weight:800;">当前订阅概览</div>
      <div class="current">
        <div class="stat">
          <div class="label">当前邮箱</div>
          <div class="value" id="meEmail">加载中</div>
        </div>
        <div class="stat">
          <div class="label">当前套餐</div>
          <div class="value" id="mePlan">加载中</div>
        </div>
        <div class="stat">
          <div class="label">当前价格</div>
          <div class="value" id="mePrice">加载中</div>
        </div>
        <div class="stat">
          <div class="label">每日趋势额度</div>
          <div class="value" id="meLimit">加载中</div>
        </div>
      </div>
    </div>

    <div class="plans" id="plansWrap">
      <div class="plan-card" id="card-free">
        <div class="plan-name">Free</div>
        <div class="badge" id="badge-free" style="display:none;">当前套餐</div>
        <div class="price">$0<span style="font-size:18px;font-weight:500;"> / month</span></div>
        <div class="price-sub">适合先体验 TrendForge 的新用户</div>
        <ul class="feature-list">
          <li>每日趋势额度：3</li>
          <li>Listing AI：NO</li>
          <li>MJ Prompt：NO</li>
          <li>Command Center：NO</li>
          <li>适合先注册、先体验、先试跑</li>
        </ul>
        <button class="btn btn-secondary" id="btn-free" disabled>当前默认套餐</button>
      </div>

      <div class="plan-card" id="card-pro">
        <div class="plan-name">Pro</div>
        <div class="badge" id="badge-pro" style="display:none;">当前套餐</div>
        <div class="price">$39<span style="font-size:18px;font-weight:500;"> / month</span></div>
        <div class="price-sub">适合需要稳定上新的 POD 卖家</div>
        <ul class="feature-list">
          <li>每日趋势额度：20</li>
          <li>Listing AI：YES</li>
          <li>MJ Prompt：YES</li>
          <li>Command Center：NO</li>
          <li>适合开始形成稳定上新工作流</li>
        </ul>
        <button class="btn btn-primary" id="btn-pro" onclick="changePlan('pro')">升级到 PRO</button>
      </div>

      <div class="plan-card" id="card-vip">
        <div class="plan-name">VIP</div>
        <div class="badge" id="badge-vip" style="display:none;">当前套餐</div>
        <div class="price">$99<span style="font-size:18px;font-weight:500;"> / month</span></div>
        <div class="price-sub">适合团队化、批量化、商业版使用场景</div>
        <ul class="feature-list">
          <li>每日趋势额度：999</li>
          <li>Listing AI：YES</li>
          <li>MJ Prompt：YES</li>
          <li>Command Center：YES</li>
          <li>适合真正商业化运转的高频用户</li>
        </ul>
        <button class="btn btn-primary" id="btn-vip" onclick="changePlan('vip')">升级到 VIP</button>
      </div>
    </div>

    <div class="panel">
      <div style="font-size:28px;font-weight:800;margin-bottom:12px;">操作结果</div>
      <div class="result" id="resultBox">等待操作...</div>
      <div class="links">
        <a href="/dashboard-v108.html">返回 Dashboard</a><br/>
        <a href="/index-v107.html">返回首页</a>
      </div>
    </div>
  </div>

  <script>
    function getToken(){
      return localStorage.getItem("tf_token");
    }

    async function fetchMeAndPlan(){
      const token = getToken();
      if(!token){
        location.href = "/login-v108.html";
        return null;
      }

      const res = await fetch("/api/plan_v112?token=" + encodeURIComponent(token));
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

    function resetCards(){
      ["free","pro","vip"].forEach(p => {
        document.getElementById("card-" + p).classList.remove("active");
        document.getElementById("badge-" + p).style.display = "none";
      });
    }

    function renderCurrent(data){
      document.getElementById("meEmail").innerText = data.email;
      document.getElementById("mePlan").innerText = data.plan;
      document.getElementById("mePrice").innerText = data.price;
      document.getElementById("meLimit").innerText = data.daily_limit;

      resetCards();
      document.getElementById("card-" + data.plan).classList.add("active");
      document.getElementById("badge-" + data.plan).style.display = "inline-block";

      document.getElementById("btn-free").disabled = true;
      document.getElementById("btn-pro").disabled = false;
      document.getElementById("btn-vip").disabled = false;

      if(data.plan === "pro"){
        document.getElementById("btn-pro").disabled = true;
      }
      if(data.plan === "vip"){
        document.getElementById("btn-vip").disabled = true;
      }
    }

    async function loadPage(){
      const data = await fetchMeAndPlan();
      if(!data) return;
      renderCurrent(data);
      document.getElementById("resultBox").innerText = "当前订阅页已加载完成。";
    }

    async function changePlan(targetPlan){
      const token = getToken();
      const res = await fetch("/api/change_plan_v114?token=" + encodeURIComponent(token) + "&target_plan=" + encodeURIComponent(targetPlan));
      const data = await res.json();

      if(data.status === "ok"){
        renderCurrent(data);
        document.getElementById("resultBox").innerHTML = `
          套餐切换成功：${data.plan}<br/>
          每日趋势额度：${data.daily_limit}<br/>
          Listing AI：${data.listing_ai ? 'YES' : 'NO'}<br/>
          MJ Prompt：${data.mj_prompt ? 'YES' : 'NO'}<br/>
          Command Center：${data.command_center ? 'YES' : 'NO'}
        `;
      } else {
        document.getElementById("resultBox").innerText = "套餐切换失败";
      }
    }

    loadPage();
  </script>
</body>
</html>
EOF

echo "TrendForge V116 files installed successfully."
