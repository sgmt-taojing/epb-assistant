#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化知识库页面 - 添加便捷工作功能
"""

import os

# 读取原文件
_file_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_file_dir, 'knowledge.html'), 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 导航栏升级 - 在现有导航栏的 <a href="/">← 返回</a> 后面添加快捷按钮
nav_upgrade = """<div class="nav-actions">
  <button class="nav-btn" onclick="toggleSearch()" title="搜索 (Ctrl+K)">🔍 <span class="nav-btn-text">搜索</span></button>
  <button class="nav-btn" onclick="showTab('contribute',document.querySelector('.tab[onclick*=contribute]'))" title="新建条目">＋ <span class="nav-btn-text">新建条目</span></button>
</div>
</div>"""

# 替换导航栏结尾
content = content.replace(
    '<div class="nav"><span style="font-size:20px">📚</span><h1>开源环保知识库</h1><a href="/">← 返回</a></div>',
    '<div class="nav"><span style="font-size:20px">📚</span><h1>开源环保知识库</h1><a href="/" class="nav-back">← 返回首页</a><div class="nav-actions"><button class="nav-btn" onclick="toggleSearchModal()" title="搜索 (Ctrl+K)">🔍 <span class="nav-btn-text">搜索</span></button><button class="nav-btn" onclick="showTab(\'contribute\',document.querySelectorAll(\'.tab\')[4])" title="新建条目">＋ <span class="nav-btn-text">新建条目</span></button></div></div>'
)

# 2. 在 </style> 前添加新CSS
new_css = """
/* ===== 优化样式 ===== */

/* 导航栏升级 */
.nav{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.nav h1{font-size:17px;font-weight:600;margin:0}
.nav-back{color:rgba(255,255,255,.85);text-decoration:none;font-size:13px;margin-left:8px;transition:color .2s}
.nav-back:hover{color:#fff}
.nav-actions{display:flex;gap:6px;margin-left:auto}
.nav-btn{padding:6px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;font-size:12px;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:4px}
.nav-btn:hover{background:rgba(255,255,255,.25);border-color:rgba(255,255,255,.5)}
@media(max-width:640px){
  .nav-btn-text{display:none}
  .nav-btn{padding:6px 8px;font-size:14px}
}

/* Ctrl+K 全局搜索模态框 */
.search-modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:9999;justify-content:center;align-items:flex-start;padding-top:10vh}
.search-modal.show{display:flex}
.search-modal-content{background:#fff;border-radius:16px;width:90%;max-width:640px;box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden;animation:slideDown .2s ease}
@keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
.search-modal-input{padding:20px;font-size:18px;border:none;border-bottom:2px solid var(--green-light);outline:none;width:100%}
.search-modal-results{max-height:400px;overflow-y:auto;padding:8px}
.search-result-item{padding:12px 16px;border-radius:8px;cursor:pointer;transition:background .2s;border-bottom:1px solid var(--green-bg)}
.search-result-item:hover{background:var(--green-bg)}
.search-result-item .result-title{font-size:14px;font-weight:600;color:var(--green)}
.search-result-item .result-meta{font-size:11px;color:var(--muted);margin-top:2px}
.search-result-item .result-type{display:inline-block;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;margin-right:6px}
.result-type.law{background:#D5F5E3;color:#1B4332}
.result-type.case{background:#FEF5E7;color:#E67E22}
.result-type.standard{background:#EBF5FB;color:#2980B9}
.result-type.industry{background:#F5EEF8;color:#8E44AD}

/* 快捷模板区 */
.quick-templates{display:flex;gap:8px;padding:10px 14px;background:linear-gradient(135deg,var(--green-pale),#E8F5E9);border-radius:var(--r);margin-bottom:12px;overflow-x:auto;flex-wrap:wrap}
.template-tag{padding:6px 12px;border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;transition:all .2s;white-space:nowrap;text-decoration:none;display:inline-flex;align-items:center;gap:4px}
.template-tag.green{background:var(--green);color:#fff}
.template-tag.green:hover{background:var(--green-mid)}
.template-tag.light{background:#fff;color:var(--green);border:1.5px solid var(--green)}
.template-tag.light:hover{background:var(--green-bg)}
.template-tag.amber{background:var(--amber);color:#fff}
.template-tag.amber:hover{background:#D68910}

/* 浮动快捷面板 */
.fab-container{position:fixed;bottom:80px;right:20px;z-index:1000}
.fab-main{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,var(--green),var(--green-mid));color:#fff;border:none;font-size:24px;cursor:pointer;box-shadow:0 4px 20px rgba(27,67,50,.4);transition:all .3s;display:flex;align-items:center;justify-content:center}
.fab-main:hover{transform:scale(1.1);box-shadow:0 6px 24px rgba(27,67,50,.5)}
.fab-main.active{transform:rotate(45deg)}
.fab-menu{position:absolute;bottom:70px;right:0;display:none;flex-direction:column;gap:8px}
.fab-menu.show{display:flex}
.fab-item{display:flex;align-items:center;gap:8px;padding:10px 16px;background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.15);cursor:pointer;font-size:13px;transition:all .2s;white-space:nowrap;text-decoration:none;color:var(--text)}
.fab-item:hover{transform:translateX(-4px);box-shadow:0 4px 16px rgba(0,0,0,.2)}
.fab-item-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px}
.fab-item-icon.contribute{background:#E8F5E9;color:var(--green)}
.fab-item-icon.import{background:#E3F2FD;color:#1565C0}
.fab-item-icon.export{background:#FFF3E0;color:#E65100}
.fab-item-icon.stats{background:#F3E5F5;color:#6A1B9A}
.fab-item-icon.settings{background:#ECEFF1;color:#37474F}
.fab-item-icon.home{background:var(--green-pale);color:var(--green-mid)}

/* 返回顶部按钮 */
.back-to-top{position:fixed;bottom:140px;right:20px;width:40px;height:40px;border-radius:50%;background:var(--green-mid);color:#fff;border:none;font-size:18px;cursor:pointer;opacity:0;transition:all .3s;z-index:999;box-shadow:0 2px 8px rgba(0,0,0,.2);display:flex;align-items:center;justify-content:center}
.back-to-top.show{opacity:1}
.back-to-top:hover{background:var(--green);transform:translateY(-2px)}

/* 底部快捷栏 */
.bottom-bar{position:fixed;bottom:0;left:0;width:100%;background:#fff;border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0;padding-bottom:calc(8px + env(safe-area-inset-bottom));z-index:1000;box-shadow:0 -2px 12px rgba(0,0,0,.08)}
.bar-item{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10px;color:var(--muted);cursor:pointer;transition:color .2s;text-decoration:none;padding:4px 12px;border-radius:8px;transition:all .2s}
.bar-item:hover,.bar-item.active{color:var(--green);background:var(--green-bg)}
.bar-item-icon{font-size:20px}
.bar-item-label{font-size:10px;font-weight:600}
@media(max-width:600px){
  .bottom-bar{padding:6px 0}
  .bar-item{padding:4px 8px}
}
"""

content = content.replace('</style>', new_css + '\n</style>')

# 3. 在页面顶部（opensource-banner 之后）添加快捷模板区
quick_templates = """
<!-- 快捷模板区 -->
<div class="quick-templates">
  <a class="template-tag green" href="#" onclick="alert('快速立案功能开发中');return false">⚡ 快速立案</a>
  <a class="template-tag light" href="#" onclick="alert('企业查询功能开发中');return false">🏢 企业查询</a>
  <a class="template-tag amber" href="#" onclick="alert('现场执法终端功能开发中');return false">📱 现场执法终端</a>
  <a class="template-tag light" href="#" onclick="showTab('list',document.querySelectorAll('.tab')[3]);return false">📋 条目列表</a>
  <a class="template-tag light" href="#" onclick="showTab('contribute',document.querySelectorAll('.tab')[4]);return false">✏️ 贡献投稿</a>
  <a class="template-tag green" href="#" onclick="filterTag(document.querySelector('.tag'),'law');return false">⚖️ 法律法规</a>
</div>
"""

# 在 opensource-banner 的 div 结束后插入
content = content.replace(
    '<div class="card">\n<input class="search-input"',
    quick_templates + '\n<div class="card">\n<input class="search-input"'
)

# 4. 在 </body> 前添加 HTML (搜索模态框、浮动面板、返回顶部、底部快捷栏) 和 JS
new_html_js = """
<!-- Ctrl+K 全局搜索模态框 -->
<div class="search-modal" id="searchModal">
  <div class="search-modal-content">
    <input type="text" class="search-modal-input" id="globalSearchInput" placeholder="搜索知识库... (支持标题/类型/来源)" oninput="globalSearch(this.value)" autocomplete="off">
    <div class="search-modal-results" id="globalSearchResults">
      <div style="padding:20px;text-align:center;color:var(--muted);font-size:13px">输入关键词开始搜索...</div>
    </div>
  </div>
</div>

<!-- 浮动快捷面板 -->
<div class="fab-container">
  <div class="fab-menu" id="fabMenu">
    <div class="fab-item" onclick="showTab('contribute',document.querySelectorAll('.tab')[4]);toggleFab()">
      <div class="fab-item-icon contribute">📤</div>
      <span>贡献投稿</span>
    </div>
    <div class="fab-item" onclick="alert('批量导入功能开发中')">
      <div class="fab-item-icon import">📥</div>
      <span>批量导入</span>
    </div>
    <div class="fab-item" onclick="alert('导出列表功能开发中')">
      <div class="fab-item-icon export">📤</div>
      <span>导出列表</span>
    </div>
    <div class="fab-item" onclick="showTab('progress',document.querySelectorAll('.tab')[2])">
      <div class="fab-item-icon stats">📊</div>
      <span>数据统计</span>
    </div>
    <div class="fab-item" onclick="alert('管理设置功能开发中')">
      <div class="fab-item-icon settings">⚙️</div>
      <span>管理设置</span>
    </div>
    <div class="fab-item" href="/">
      <div class="fab-item-icon home">🏠</div>
      <span>返回首页</span>
    </div>
  </div>
  <button class="fab-main" id="fabMain" onclick="toggleFab()">＋</button>
</div>

<!-- 返回顶部按钮 -->
<button class="back-to-top" id="backToTop" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>

<!-- 底部快捷栏 -->
<div class="bottom-bar">
  <a class="bar-item" href="/">
    <span class="bar-item-icon">🏠</span>
    <span class="bar-item-label">首页</span>
  </a>
  <a class="bar-item active" href="/knowledge.html">
    <span class="bar-item-icon">📚</span>
    <span class="bar-item-label">知识库</span>
  </a>
  <a class="bar-item" href="/enforcement.html">
    <span class="bar-item-icon">⚖️</span>
    <span class="bar-item-label">执法</span>
  </a>
  <a class="bar-item" href="/analysis.html">
    <span class="bar-item-icon">📊</span>
    <span class="bar-item-label">分析</span>
  </a>
  <a class="bar-item" href="/workspace.html">
    <span class="bar-item-icon">🖥</span>
    <span class="bar-item-label">工作台</span>
  </a>
</div>

<script>
// Ctrl+K 全局搜索
function toggleSearchModal(){
  const modal=document.getElementById('searchModal');
  if(modal.classList.contains('show')){
    modal.classList.remove('show');
  }else{
    modal.classList.add('show');
    document.getElementById('globalSearchInput').focus();
  }
}

// 点击模态框背景关闭
document.getElementById('searchModal').addEventListener('click',function(e){
  if(e.target===this)this.classList.remove('show');
});

// ESC关闭模态框
document.addEventListener('keydown',function(e){
  if(e.key==='Escape')document.getElementById('searchModal').classList.remove('show');
  if((e.ctrlKey||e.metaKey)&&e.key==='k'){
    e.preventDefault();
    toggleSearchModal();
  }
});

// 全局搜索函数
function globalSearch(query){
  const resultsDiv=document.getElementById('globalSearchResults');
  query=query.toLowerCase().trim();
  if(!query){
    resultsDiv.innerHTML='<div style="padding:20px;text-align:center;color:var(--muted);font-size:13px">输入关键词开始搜索...</div>';
    return;
  }
  // 模拟搜索数据（实际应该从 knowledge_graph.json 或 API 获取）
  const mockData=[
    {title:'水污染防治法(2017修正)',type:'law',source:'生态环境部',cat:'法律法规'},
    {title:'大气污染防治法',type:'law',source:'生态环境部',cat:'法律法规'},
    {title:'GB 3838-2002 地表水环境质量标准',type:'standard',source:'国家标准系统',cat:'技术标准'},
    {title:'某化工厂私设暗管排放废水案',type:'case',source:'济南市环保局',cat:'执法案例'},
    {title:'化工行业产排污环节与检查要点',type:'industry',source:'环保行业文献',cat:'行业知识'},
    {title:'危废现场检查取证技巧',type:'experience',source:'社区贡献',cat:'行业知识'},
  ];
  const results=mockData.filter(item=>
    item.title.toLowerCase().includes(query)||
    item.type.toLowerCase().includes(query)||
    item.source.toLowerCase().includes(query)||
    item.cat.toLowerCase().includes(query)
  );
  if(results.length===0){
    resultsDiv.innerHTML='<div style="padding:20px;text-align:center;color:var(--muted);font-size:13px">未找到相关结果</div>';
    return;
  }
  let html='';
  results.forEach(r=>{
    const typeClass=r.type==='law'?'law':r.type==='case'?'case':r.type==='standard'?'standard':'industry';
    html+=`<div class="search-result-item" onclick="selectSearchResult('${r.title}')">
      <div class="result-title"><span class="result-type ${typeClass}">${r.cat}</span>${r.title}</div>
      <div class="result-meta">来源: ${r.source}</div>
    </div>`;
  });
  resultsDiv.innerHTML=html;
}

function selectSearchResult(title){
  document.getElementById('searchModal').classList.remove('show');
  // 切换到条目列表并搜索
  showTab('list',document.querySelectorAll('.tab')[3]);
  document.querySelector('#sec-list input[placeholder*=搜索]').value=title;
  filterListSearch(title);
}

// 浮动快捷面板
function toggleFab(){
  const fabMain=document.getElementById('fabMain');
  const fabMenu=document.getElementById('fabMenu');
  fabMain.classList.toggle('active');
  fabMenu.classList.toggle('show');
}

// 返回顶部按钮
window.addEventListener('scroll',function(){
  const btn=document.getElementById('backToTop');
  if(window.scrollY>100){
    btn.classList.add('show');
  }else{
    btn.classList.remove('show');
  }
});

// 点击搜索模态框外关闭
document.addEventListener('click',function(e){
  const modal=document.getElementById('searchModal');
  if(e.target.classList.contains('search-modal')){
    modal.classList.remove('show');
  }
});
</script>
"""

content = content.replace('</body>', new_html_js + '\n</body>')

# 写回文件
with open(os.path.join(_file_dir, 'knowledge.html'), 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 知识库页面优化完成！")
print("\n添加的功能：")
print("1. ✅ 导航栏升级 - 新增搜索和新建条目按钮")
print("2. ✅ Ctrl+K 全局搜索 - 模态框搜索")
print("3. ✅ 浮动快捷面板 - 右下角+按钮")
print("4. ✅ 返回顶部按钮 - 滚动100px后显示")
print("5. ✅ 快捷模板区 - 页面顶部常用操作标签")
print("6. ✅ 底部快捷栏 - 类似 field-terminal 的样式")
print("\n文件已保存到: /Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/web/knowledge.html")
