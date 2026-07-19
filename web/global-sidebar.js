// === 环保智慧执法 · 侧边栏菜单（增强版）===
// 为所有页面提供统一的下拉菜单入口
(function(){
'use strict';

if (document.getElementById('epb-sidebar')) return;

// 注入CSS
var style = document.createElement('style');
style.textContent = `
#epb-sidebar-btn{position:fixed;top:50%;left:0;transform:translateY(-50%);width:36px;height:64px;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;border:none;border-radius:0 8px 8px 0;cursor:pointer;z-index:99997;box-shadow:0 2px 8px rgba(59,130,246,.4);transition:all .3s;font-size:14px;display:flex;align-items:center;justify-content:center}
#epb-sidebar-btn:hover{width:42px;background:linear-gradient(135deg,#2563eb,#1d4ed8)}
#epb-sidebar{position:fixed;top:0;left:-340px;width:320px;height:100vh;background:#0d1117;border-right:1px solid #1e293b;z-index:99998;transition:left .3s ease;overflow-y:auto;box-shadow:4px 0 24px rgba(0,0,0,.4);font-family:-apple-system,BlinkMacSystemFont,sans-serif}
#epb-sidebar.open{left:0}
#epb-sidebar-head{padding:18px 16px;background:linear-gradient(135deg,#1e293b,#0f172a);border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:1}
#epb-sidebar-head .title{color:#60a5fa;font-size:15px;font-weight:700}
#epb-sidebar-head .close{color:#64748b;font-size:20px;cursor:pointer;padding:4px 8px}
#epb-sidebar-head .close:hover{color:#fff}
#epb-sidebar-backdrop{position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,.5);z-index:99997;display:none}
#epb-sidebar-backdrop.open{display:block}
.epb-menu-group{padding:12px 0;border-bottom:1px solid #1e293b}
.epb-menu-group-title{padding:4px 16px;font-size:11px;color:#64748b;font-weight:600;letter-spacing:1px;text-transform:uppercase;display:flex;align-items:center;gap:6px}
.epb-menu-item{display:flex;align-items:center;padding:8px 16px;color:#cbd5e1;text-decoration:none;font-size:13px;transition:all .2s;border-left:2px solid transparent}
.epb-menu-item:hover{background:#1e293b;color:#fff;border-left-color:#3b82f6}
.epb-menu-item .icon{width:22px;text-align:center;margin-right:8px;font-size:14px;opacity:.85}
.epb-menu-item .name{flex:1}
.epb-menu-item .badge{font-size:9px;background:#3b82f6;color:#fff;padding:1px 5px;border-radius:8px;margin-left:4px}
`;
document.head.appendChild(style);

// 完整菜单（59页面全覆盖，0重复）
var MENU = [
  {title:'🏠 入口', items:[
    {name:'首页',icon:'🏠',url:'index.html'},
    {name:'总览驾驶舱',icon:'📊',url:'overview.html'},
    {name:'运营监控',icon:'📈',url:'ops-monitor.html',badge:'NEW'},
    {name:'数据驾驶舱',icon:'📈',url:'data-cockpit.html'},
    {name:'智能指挥中心',icon:'🚨',url:'emergency-center.html'},
    {name:'系统控制台',icon:'⚙️',url:'sys-console.html'},
  ]},
  {title:'🔍 监测感知', items:[
    {name:'环境一张图',icon:'🗺️',url:'env-map.html'},
    {name:'物联网监测',icon:'📡',url:'iot.html'},
    {name:'IoT接入与诊断',icon:'🔧',url:'iot-diagnostic.html',badge:'NEW'},
    {name:'传感器可视化',icon:'🌐',url:'sensor-dashboard.html'},
    {name:'设备管理',icon:'⚙️',url:'device-mgmt.html'},
    {name:'智能预警系统',icon:'🔔',url:'smart-alert.html',badge:'45'},
    {name:'非现场执法',icon:'👁️',url:'remote-enforcement.html'},
    {name:'无人机巡查',icon:'🚁',url:'drone-patrol.html'},
  ]},
  {title:'📋 执法办案', items:[
    {name:'执法流程引导',icon:'📋',url:'enforcement-guide.html'},
    {name:'现场执法终端',icon:'📱',url:'field-terminal.html'},
    {name:'案例智能分析',icon:'🧠',url:'case-analysis.html'},
    {name:'案件管理',icon:'📂',url:'m-cases.html'},
    {name:'取证工具箱',icon:'🧰',url:'evidence-toolkit.html'},
    {name:'执法文书AI生成',icon:'📄',url:'doc-generator.html'},
    {name:'自由裁量计算器',icon:'⚖️',url:'penalty-calculator.html'},
  ]},
  {title:'👥 公众企业', items:[
    {name:'公众互动中心',icon:'👥',url:'public-interact.html'},
    {name:'环境污染举报',icon:'🚨',url:'report.html'},
    {name:'环保科普',icon:'🌱',url:'eco-science.html'},
    {name:'企业环保台账',icon:'📚',url:'env-ledger.html'},
    {name:'环保管家',icon:'🔧',url:'eco-manager.html'},
    {name:'EHS安环管理',icon:'🏭',url:'ehs.html'},
    {name:'能力评估',icon:'📐',url:'capacity-assess.html'},
  ]},
  {title:'🛒 设备&能耗', items:[
    {name:'设备商城',icon:'🛒',url:'equipment-mall.html'},
    {name:'能耗管理',icon:'⚡',url:'energy.html',badge:'NEW'},
    {name:'碳排放管理',icon:'🌿',url:'carbon-mgmt.html'},
    {name:'绿色金融',icon:'💰',url:'green-finance.html'},
    {name:'数据中心',icon:'📊',url:'dashboard.html'},
  ]},
  {title:'📜 法规数据', items:[
    {name:'法规库',icon:'📜',url:'law-library.html'},
    {name:'知识图谱',icon:'🕸️',url:'knowledge-graph.html'},
    {name:'环保知识库',icon:'📚',url:'knowledge.html'},
    {name:'环保前沿·商机',icon:'🚀',url:'eco-frontier.html',badge:'NEW'},
    {name:'数据开放',icon:'📂',url:'open-data.html'},
    {name:'生态统计',icon:'📊',url:'eco-statistics.html'},
    {name:'信用评级',icon:'⭐',url:'credit-rating.html'},
    {name:'风险画像',icon:'🎯',url:'risk-profile.html'},
  ]},
  {title:'📅 审批督察', items:[
    {name:'环保审批服务',icon:'📝',url:'approval-service.html'},
    {name:'督察整改',icon:'🔍',url:'inspection.html'},
    {name:'环保政策日历',icon:'📅',url:'eco-calendar.html',badge:'NEW'},
    {name:'AI周报月报',icon:'📋',url:'ai-report.html'},
    {name:'协同办公',icon:'🤝',url:'collaboration.html'},
  ]},
  {title:'📱 移动端', items:[
    {name:'移动门户',icon:'📱',url:'m-portal.html'},
    {name:'移动举报',icon:'📢',url:'m-report.html'},
    {name:'移动工作台',icon:'💼',url:'m-workspace.html'},
    {name:'移动自查',icon:'✅',url:'m-self-check.html'},
    {name:'视频工作室',icon:'🎬',url:'video-studio.html'},
    {name:'微信H5',icon:'💬',url:'wechat-h5.html'},
  ]},
  {title:'🧰 其他', items:[
    {name:'培训学习',icon:'🎓',url:'training.html'},
    {name:'监管模块',icon:'👮',url:'supervision.html'},
    {name:'企业自查',icon:'✅',url:'self-check.html'},
    {name:'数据分析',icon:'📊',url:'analysis.html'},
    {name:'管理后台',icon:'🖥️',url:'admin.html'},
    {name:'工作空间',icon:'🗂️',url:'workspace.html'},
    {name:'登录',icon:'🔐',url:'login.html'},
    {name:'工程规划',icon:'🗺️',url:'engineering-plan.html'},
  ]},
];

// 按钮
var btn = document.createElement('div');
btn.id = 'epb-sidebar-btn';
btn.innerHTML = '☰';
btn.title = '打开菜单';
document.body.appendChild(btn);

// 遮罩
var backdrop = document.createElement('div');
backdrop.id = 'epb-sidebar-backdrop';
document.body.appendChild(backdrop);

// 侧栏
var sidebar = document.createElement('div');
sidebar.id = 'epb-sidebar';
var html = '<div id="epb-sidebar-head"><span class="title">🌿 功能菜单</span><span class="close">✕</span></div>';
MENU.forEach(function(group){
  html += '<div class="epb-menu-group"><div class="epb-menu-group-title">' + group.title + '</div>';
  group.items.forEach(function(item){
    html += '<a class="epb-menu-item" href="' + item.url + '"><span class="icon">' + item.icon + '</span><span class="name">' + item.name + '</span>' + (item.badge ? '<span class="badge">' + item.badge + '</span>' : '') + '</a>';
  });
  html += '</div>';
});
sidebar.innerHTML = html;
document.body.appendChild(sidebar);

var isOpen = false;
function toggle(){
  isOpen = !isOpen;
  sidebar.classList.toggle('open', isOpen);
  backdrop.classList.toggle('open', isOpen);
}
btn.addEventListener('click', toggle);
backdrop.addEventListener('click', function(){ if(isOpen) toggle(); });
sidebar.querySelector('.close').addEventListener('click', toggle);

})();