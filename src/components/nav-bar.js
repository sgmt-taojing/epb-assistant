// 公共导航栏组件 — 各页面可通过 import 使用
export function createNavBar(title = '环保智慧执法平台', backUrl = 'index.html') {
  return `
  <nav style="background:linear-gradient(135deg,#2E7D5B,#3B9B6E);padding:0 20px;height:56px;display:flex;align-items:center;position:sticky;top:0;z-index:100;box-shadow:0 2px 12px rgba(46,125,91,.15)">
    <a href="${backUrl}" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:#fff">
      <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--gl),var(--gm));display:flex;align-items:center;justify-content:center;font-size:18px">🌿</div>
      <span style="font-size:15px;font-weight:700;color:#e8f5e9">${title}</span>
    </a>
    <a href="${backUrl}" style="margin-left:auto;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:8px;padding:6px 14px;font-size:13px;text-decoration:none">← 返回首页</a>
  </nav>`;
}
