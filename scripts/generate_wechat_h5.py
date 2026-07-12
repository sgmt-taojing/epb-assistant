#!/usr/bin/env python3
"""
环保智能体平台 — 微信公众号 H5 移动入口页面生成
生成 wechat-h5.html，适配微信内置浏览器和移动端浏览器
"""

import os, json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'db')
OUTPUT = os.path.join(BASE_DIR, 'web', 'wechat-h5.html')

def load_json(name):
    p = os.path.join(DB_DIR, name)
    if not os.path.exists(p):
        return {}
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

cases = load_json('cases.json')
law_data = load_json('law_index.json')
kg = load_json('knowledge_graph.json')

case_count = len(cases) if isinstance(cases, list) else 0
law_count = law_data.get('total_laws', 21) if isinstance(law_data, dict) else 21

REPORT_TYPES = [
    {"value": "水污染", "icon": "💧", "desc": "废水直排、暗管偷排、水体变色等"},
    {"value": "大气污染", "icon": "💨", "desc": "废气排放、烟尘异味、VOCs等"},
    {"value": "噪声污染", "icon": "🔊", "desc": "工业噪声、施工噪声、社会生活噪声"},
    {"value": "固废危废", "icon": "🗑️", "desc": "非法倾倒、危废违规处置等"},
    {"value": "土壤污染", "icon": "🟤", "desc": "土壤污染、农用地污染等"},
    {"value": "辐射污染", "icon": "☢️", "desc": "电磁辐射、电离辐射等"},
    {"value": "生态破坏", "icon": "🌿", "desc": "破坏生态、非法采伐等"},
    {"value": "其他", "icon": "📋", "desc": "其他环境违法行为"},
]

HOT_LAWS = [
    {"title": "水污染防治法", "icon": "💧", "path": "knowledge.html#水"},
    {"title": "大气污染防治法", "icon": "💨", "path": "knowledge.html#大气"},
    {"title": "固废防治法", "icon": "🗑️", "path": "knowledge.html#固废"},
    {"title": "噪声污染防治法", "icon": "🔊", "path": "knowledge.html#噪声"},
    {"title": "排污许可管理条例", "icon": "📄", "path": "knowledge.html#排污"},
    {"title": "环境影响评价法", "icon": "📋", "path": "knowledge.html#环评"},
]

QUICK_SERVICES = [
    {"title": "我的工作台", "desc": "角色定制工作台", "icon": "📋", "path": "/m-workspace.html", "color": "#1B4332"},
    {"title": "群众举报", "desc": "一键举报环境违法", "icon": "🚨", "path": "/m-report.html", "color": "#e74c3c"},
    {"title": "企业自查", "desc": "企业合规自检自纠", "icon": "🏢", "path": "/m-self-check.html", "color": "#27ae60"},
    {"title": "案例查询", "desc": "执法案例库检索", "icon": "📚", "path": "/m-cases.html", "color": "#2980b9"},
    {"title": "数据驾驶舱", "desc": "全局态势感知", "icon": "📊", "path": "/dashboard.html", "color": "#8e44ad"},
    {"title": "登录引导", "desc": "选择身份获取服务", "icon": "🔐", "path": "/login.html", "color": "#e67e22"},
]

# Build HTML sections
quick_items = ""
for s in QUICK_SERVICES:
    quick_items += (
        '    <a href="' + s['path'] + '" class="quick-item">\n'
        '      <div class="quick-icon" style="background:' + s['color'] + '">' + s['icon'] + '</div>\n'
        '      <div class="quick-label">' + s['title'] + '</div>\n'
        '      <div class="quick-desc">' + s['desc'] + '</div>\n'
        '    </a>\n'
    )

report_cards = ""
for r in REPORT_TYPES:
    report_cards += (
        '    <div class="report-card" onclick="location.href=\'/m-report.html?type=' + r['value'] + '\'">\n'
        '      <div class="report-card-icon">' + r['icon'] + '</div>\n'
        '      <div class="report-card-info">\n'
        '        <div class="report-card-title">' + r['value'] + '</div>\n'
        '        <div class="report-card-desc">' + r['desc'] + '</div>\n'
        '      </div>\n'
        '    </div>\n'
    )

law_items = ""
for l in HOT_LAWS:
    law_items += (
        '    <a href="/' + l['path'] + '" class="law-item">\n'
        '      <div class="law-icon">' + l['icon'] + '</div>\n'
        '      <div class="law-name">' + l['title'] + '</div>\n'
        '      <div class="law-arrow">›</div>\n'
        '    </a>\n'
    )

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="format-detection" content="telephone=no">
<title>🌿 环保智慧执法平台</title>
<style>
:root{
  --g:#1B4332;--gm:#2D6A4F;--gl:#52B788;--gp:#D8E8DC;--gbg:#F2F8F4;
  --red:#E74C3C;--amber:#E67E22;--blue:#2980B9;--purple:#8E44AD;--teal:#009688;
  --bg:#F0F2F0;--card:#FFF;--border:#D0E0D4;--text:#1A1A1A;--muted:#666;
  --shadow:0 2px 12px rgba(27,67,50,.08);--r:12px;--r-lg:16px;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%}

/* Header */
.header{
  background:linear-gradient(135deg,#1B4332 0%,#2D6A4F 50%,#1B4332 100%);
  color:#fff;padding:20px 16px 24px;position:relative;overflow:hidden;
}
.header::after{
  content:'';position:absolute;bottom:-30px;left:-10%;right:-10%;height:60px;
  background:var(--bg);border-radius:50% 50% 0 0;
}
.header-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;position:relative;z-index:1}
.header-logo{display:flex;align-items:center;gap:8px}
.header-logo-icon{width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;font-size:18px}
.header-logo-text{font-size:16px;font-weight:700;letter-spacing:1px}
.header-status{display:flex;align-items:center;gap:4px;background:rgba(76,175,80,.2);border:1px solid rgba(76,175,80,.4);border-radius:12px;padding:3px 8px;font-size:10px}
.header-status-dot{width:6px;height:6px;border-radius:50%;background:#4caf50;box-shadow:0 0 4px #4caf50;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}

/* Banner */
.banner{position:relative;z-index:2;margin:0 16px;background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.04));border:1px solid rgba(255,255,255,.15);border-radius:var(--r);padding:16px;display:flex;align-items:center;gap:14px}
.banner-icon{width:48px;height:48px;border-radius:12px;background:rgba(82,183,136,.3);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0}
.banner-text{flex:1}
.banner-title{font-size:14px;font-weight:700;margin-bottom:2px}
.banner-desc{font-size:11px;opacity:.8;line-height:1.4}
.banner-stats{display:flex;gap:12px;margin-top:8px}
.banner-stat{font-size:10px;opacity:.7}
.banner-stat strong{font-size:16px;font-weight:700;display:block;color:#fff;opacity:1}

/* Section */
.section{margin:16px;background:var(--card);border-radius:var(--r-lg);overflow:hidden;box-shadow:var(--shadow)}
.section-header{display:flex;align-items:center;justify-content:space-between;padding:14px 16px 10px}
.section-title{font-size:15px;font-weight:700;display:flex;align-items:center;gap:6px}
.section-title .dot{width:4px;height:16px;background:var(--gm);border-radius:2px}
.section-more{font-size:12px;color:var(--muted)}

/* Quick Services */
.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border)}
.quick-item{background:var(--card);padding:16px 8px 14px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:6px;transition:background .15s}
.quick-item:active{background:var(--gbg)}
.quick-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;color:#fff}
.quick-label{font-size:12px;font-weight:600;color:var(--text)}
.quick-desc{font-size:10px;color:var(--muted);line-height:1.3}

/* Report Types */
.report-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;padding:0 16px 16px}
.report-card{display:flex;align-items:center;gap:10px;padding:12px;background:var(--gbg);border-radius:var(--r);border:1px solid var(--border);transition:all .15s}
.report-card:active{background:var(--gp);border-color:var(--gl)}
.report-card-icon{font-size:24px;flex-shrink:0}
.report-card-info{flex:1;min-width:0}
.report-card-title{font-size:13px;font-weight:600;margin-bottom:1px}
.report-card-desc{font-size:10px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* Laws */
.law-list{padding:0 16px 14px}
.law-item{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border)}
.law-item:last-child{border-bottom:none}
.law-icon{width:32px;height:32px;border-radius:8px;background:var(--gbg);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.law-name{flex:1;font-size:13px;font-weight:500}
.law-arrow{color:var(--muted);font-size:12px}

/* Cases */
.case-list{padding:0 16px 14px}
.case-item{padding:10px 0;border-bottom:1px solid var(--border)}
.case-item:last-child{border-bottom:none}
.case-tag{display:inline-block;font-size:10px;padding:2px 6px;border-radius:4px;margin-bottom:4px;margin-right:4px}
.case-tag-water{background:#e3f2fd;color:#1565c0}
.case-tag-air{background:#fff3e0;color:#e65100}
.case-tag-solid{background:#f3e5f5;color:#6a1b9a}
.case-tag-noise{background:#fce4ec;color:#c62828}
.case-tag-soil{background:#efebe9;color:#5d4037}
.case-tag-other{background:#e8f5e9;color:#2e7d32}
.case-title{font-size:13px;font-weight:500;line-height:1.4;margin-bottom:2px}
.case-meta{font-size:10px;color:var(--muted);display:flex;gap:8px}
.case-risk{font-size:10px;padding:1px 5px;border-radius:3px}
.case-risk-high{background:#ffebee;color:#c62828}
.case-risk-mid{background:#fff8e1;color:#f57f17}
.case-risk-low{background:#e8f5e9;color:#2e7d32}

/* News Card */
.news-card{margin:16px;background:linear-gradient(135deg,#1B4332,#2D6A4F);border-radius:var(--r-lg);padding:20px;color:#fff;position:relative;overflow:hidden}
.news-card::before{content:'📢';position:absolute;top:10px;right:16px;font-size:40px;opacity:.1}
.news-title{font-size:15px;font-weight:700;margin-bottom:8px;position:relative}
.news-text{font-size:12px;opacity:.85;line-height:1.6;position:relative}
.news-btn{display:inline-block;margin-top:12px;background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:6px 16px;font-size:12px;color:#fff}

/* Footer */
.footer{text-align:center;padding:20px 16px 32px;color:var(--muted);font-size:11px}
.footer-logo{font-size:20px;margin-bottom:6px}
.footer-text{margin-bottom:4px}
.footer-link{color:var(--gm);margin:0 4px}

/* Toast */
#toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.8);color:#fff;padding:12px 20px;border-radius:10px;font-size:13px;z-index:2000;display:none;max-width:80%;text-align:center}
#toast.show{display:block;animation:fadeIn .3s}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}

.loading{text-align:center;padding:20px;color:var(--muted);font-size:12px}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="header-top">
    <div class="header-logo">
      <div class="header-logo-icon">🌿</div>
      <div class="header-logo-text">环保智慧执法平台</div>
    </div>
    <div class="header-status">
      <div class="header-status-dot"></div>
      <span>系统运行中</span>
    </div>
  </div>

  <div class="banner">
    <div class="banner-icon">🤖</div>
    <div class="banner-text">
      <div class="banner-title">AI 环保智能体</div>
      <div class="banner-desc">服务政府 · 企业 · 第三方 · 群众，全行业协同闭环</div>
      <div class="banner-stats">
        <div class="banner-stat"><strong>''' + str(case_count) + '''</strong>执法案例</div>
        <div class="banner-stat"><strong>''' + str(law_count) + '''</strong>部法规</div>
        <div class="banner-stat"><strong>8</strong>大领域</div>
      </div>
    </div>
  </div>
</div>

<!-- Quick Services -->
<div class="section">
  <div class="section-header">
    <div class="section-title"><span class="dot"></span>快捷服务</div>
  </div>
  <div class="quick-grid">
''' + quick_items + '''  </div>
</div>

<!-- News Card -->
<div class="news-card">
  <div class="news-title">📋 环保知识库持续更新中</div>
  <div class="news-text">平台已收录 ''' + str(case_count) + ''' 条执法案例、''' + str(law_count) + ''' 部环保法规，覆盖水、大气、固废、噪声、土壤、辐射、生态、环评 8 大领域。AI 智能检索支持关键词语义匹配，助力环保执法精准高效。</div>
  <a href="/knowledge.html" class="news-btn">进入知识库 →</a>
</div>

<!-- Report Entry -->
<div class="section">
  <div class="section-header">
    <div class="section-title"><span class="dot" style="background:var(--red)"></span>群众举报</div>
    <a href="/report.html" class="section-more">全部 →</a>
  </div>
  <div class="report-grid">
''' + report_cards + '''  </div>
</div>

<!-- Hot Laws -->
<div class="section">
  <div class="section-header">
    <div class="section-title"><span class="dot" style="background:var(--blue)"></span>常用法规</div>
    <a href="/knowledge.html" class="section-more">全部 →</a>
  </div>
  <div class="law-list">
''' + law_items + '''  </div>
</div>

<!-- Hot Cases -->
<div class="section">
  <div class="section-header">
    <div class="section-title"><span class="dot" style="background:var(--purple)"></span>典型案例</div>
    <a href="/knowledge.html" class="section-more">全部 →</a>
  </div>
  <div class="case-list" id="hot-cases">
    <div class="loading">加载中...</div>
  </div>
</div>

<!-- Footer -->
<div class="footer">
  <div class="footer-logo">🌿</div>
  <div class="footer-text">环保智慧执法平台 · EPB-Agent</div>
  <div class="footer-text" style="margin-top:4px;opacity:.6">
    <a class="footer-link" href="/">PC端</a>|
    <a class="footer-link" href="/m-report.html">举报</a>|
    <a class="footer-link" href="/m-cases.html">案例</a>|
    <a class="footer-link" href="/m-self-check.html">自查</a>|
    <a class="footer-link" href="/knowledge.html">知识库</a>
  </div>
  <div class="footer-text" style="margin-top:8px;opacity:.5">© 2026 环保智能体平台 · 服务全社会环保职能体系</div>
</div>

<!-- Toast -->
<div id="toast"></div>

<script>
function showToast(msg, duration) {
  duration = duration || 2000;
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() { t.classList.remove('show'); }, duration);
}

var tagMap = {
  '水污染类': 'case-tag-water',
  '大气污染类': 'case-tag-air',
  '固体废物污染类': 'case-tag-solid',
  '噪声污染类': 'case-tag-noise',
  '土壤污染类': 'case-tag-soil',
  '危险废物类': 'case-tag-solid',
  '自动监控类': 'case-tag-other',
  '排污许可类': 'case-tag-other',
  '环评类': 'case-tag-other',
  '移动源监管类': 'case-tag-other',
  '其他': 'case-tag-other'
};

var riskMap = {
  '高风险': 'case-risk-high',
  '中风险': 'case-risk-mid',
  '低风险': 'case-risk-low'
};

// Load hot cases
fetch('/api/search?type=all&limit=5')
  .then(function(r) { return r.json(); })
  .then(function(data) {
    var cases = data.cases || data.results || data.data || [];
    if (!Array.isArray(cases) || cases.length === 0) {
      return fetch('/api/cases?limit=5').then(function(r) { return r.json(); });
    }
    return cases;
  })
  .then(function(cases) {
    if (!Array.isArray(cases) || cases.length === 0) {
      document.getElementById('hot-cases').innerHTML = '<div style="text-align:center;padding:16px;color:var(--muted);font-size:12px">暂无案例数据</div>';
      return;
    }
    var html = cases.slice(0, 5).map(function(c) {
      var tagCls = tagMap[c.type] || 'case-tag-other';
      var riskCls = riskMap[c.risk_level] || 'case-risk-low';
      var riskText = c.risk_level || '低风险';
      return '<div class="case-item">' +
        '<span class="case-tag ' + tagCls + '">' + (c.type || '其他') + '</span>' +
        '<span class="case-risk ' + riskCls + '">' + riskText + '</span>' +
        '<div class="case-title">' + (c.title || '') + '</div>' +
        '<div class="case-meta">' +
          '<span>' + (c.source || '未知来源') + '</span>' +
          '<span>' + (c.date || '') + '</span>' +
        '</div>' +
      '</div>';
    }).join('');
    document.getElementById('hot-cases').innerHTML = html;
  })
  .catch(function(err) {
    document.getElementById('hot-cases').innerHTML = '<div style="text-align:center;padding:16px;color:var(--muted);font-size:12px">案例加载失败</div>';
  });

// Prevent double tap zoom
var lastTouch = 0;
document.addEventListener('touchend', function(e) {
  var now = Date.now();
  if (now - lastTouch < 300) { e.preventDefault(); }
  lastTouch = now;
}, { passive: false });

// WeChat welcome
document.addEventListener('DOMContentLoaded', function() {
  var ua = navigator.userAgent.toLowerCase();
  if (ua.indexOf('micromessenger') !== -1) {
    showToast('欢迎使用环保智慧执法平台');
  }
});
</script>

</body>
</html>'''

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

print('Generated: ' + OUTPUT)
print('Case count: ' + str(case_count))
print('Law count: ' + str(law_count))
print('File size: ' + str(os.path.getsize(OUTPUT)) + ' bytes')
