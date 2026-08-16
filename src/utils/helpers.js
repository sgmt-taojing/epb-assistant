// 公共工具函数
export function epbToast(text, type = 'info') {
  var t = document.createElement('div');
  var colors = { info: '#3B9B6E', success: '#10b981', warn: '#E67E22', error: '#C0392B' };
  t.style.cssText = 'position:fixed;top:70px;right:20px;background:' + (colors[type] || colors.info) + ';color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;z-index:99999;box-shadow:0 4px 12px rgba(0,0,0,.2);animation:slideIn .3s ease';
  t.textContent = text;
  document.body.appendChild(t);
  setTimeout(function() { t.style.opacity = '0'; t.style.transition = 'opacity .3s'; }, 2500);
  setTimeout(function() { t.remove(); }, 2800);
}

export function formatDate(d) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false });
}

export function genId(prefix) {
  return prefix + '-' + Date.now().toString(36).toUpperCase();
}
