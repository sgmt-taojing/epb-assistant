// mobile-nav.js - 移动端底部导航栏（5页面共享）
(function() {
  const isMobile = /Mobile|iPhone|iPad|iPod|Android/i.test(navigator.userAgent) || window.innerWidth < 768;
  if (!isMobile) return;
  const cur = (location.pathname.split('/').pop() || '').toLowerCase();
  const items = [
    {name:'首页', icon:'home', url:'m-portal.html'},
    {name:'现场', icon:'field', url:'field-terminal.html'},
    {name:'案件', icon:'case', url:'m-cases.html'},
    {name:'报告', icon:'report', url:'m-report.html'},
    {name:'我的', icon:'mine', url:'m-self-check.html'},
  ];
  const svg = {
    home:'<path d="M3 12L12 4l9 8M5 10v10h14V10"/>',
    field:'<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M7 9h10M7 13h6"/>',
    case:'<path d="M6 3h9l4 4v14H6z M15 3v4h4"/>',
    report:'<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    mine:'<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-7 8-7s8 3 8 7"/>',
  };
  const bar = document.createElement('div');
  bar.className = 'm-bottom-bar';
  bar.innerHTML = items.map(it => {
    const active = cur === it.url ? ' active' : '';
    return `<a class="m-bar-item${active}" href="${it.url}">
      <svg class="m-bar-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${svg[it.icon]}</svg>
      <span class="m-bar-nm">${it.name}</span>
    </a>`;
  }).join('');
  const style = document.createElement('style');
  style.textContent = `
    .m-bottom-bar{position:fixed;left:0;right:0;bottom:0;height:60px;background:rgba(13,17,23,.96);backdrop-filter:blur(14px);border-top:1px solid rgba(59,130,246,.15);display:flex;justify-content:space-around;align-items:stretch;padding:6px 4px 8px;z-index:99950;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    .m-bar-item{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#64748b;text-decoration:none;font-size:10px;flex:1;min-width:0;transition:color .2s}
    .m-bar-ic{width:22px;height:22px}
    .m-bar-item.active{color:#3b82f6}
    .m-bar-item.active .m-bar-ic{filter:drop-shadow(0 0 4px rgba(59,130,246,.4))}
    body{padding-bottom:env(safe-area-inset-bottom,0)}
    @media(min-width:768px){.m-bottom-bar{display:none}}
  `;
  document.head.appendChild(style);
  document.body.appendChild(bar);
})();