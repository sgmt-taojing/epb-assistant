/**
 * EPB 权限守卫 — 各页面引入此脚本可自动检查登录状态
 * 用法：<script src="/auth-guard.js"></script>
 * 可配置：window.AUTH_REQUIRED = true/false（默认true）
 *        window.AUTH_ROLE = 'gov_enforcement'（限制角色）
 */
(function(){
  var REQUIRED = window.AUTH_REQUIRED !== false;
  var ROLE_REQUIRED = window.AUTH_ROLE || null;

  function getUser(){
    try{
      return JSON.parse(localStorage.getItem('epb_user')||'{}');
    }catch(e){
      return {};
    }
  }

  function redirectToLogin(){
    var current = location.pathname;
    if(current !== '/login.html' && current !== '/'){
      sessionStorage.setItem('epb_redirect', current);
    }
    location.href = '/login.html';
  }

  function updateWelcomeBar(){
    var u = getUser();
    if(!u.role) return;
    // 更新欢迎条（如果存在）
    var bar = document.getElementById('welcome-bar');
    if(bar){
      bar.style.display = 'flex';
      var icon = document.getElementById('welcome-icon');
      var name = document.getElementById('welcome-name');
      var role = document.getElementById('welcome-role');
      var org = document.getElementById('welcome-org');
      if(icon) icon.textContent = u.roleIcon || '🌿';
      if(name) name.textContent = u.name || '用户';
      if(role) role.textContent = u.roleName || '';
      if(org) org.textContent = u.org || '';
    }
    // 更新角色标签（如果存在）
    var badge = document.getElementById('role-badge');
    if(badge){
      badge.textContent = (u.roleIcon||'') + ' ' + (u.roleName||'');
    }
    // 更新用户名显示
    var un = document.getElementById('user-name');
    if(un) un.textContent = u.name || '游客';
    var uo = document.getElementById('user-org');
    if(uo) uo.textContent = u.org || '请登录获取个性化服务';
    var ua = document.getElementById('user-avatar');
    if(ua) ua.textContent = u.roleIcon || '🌿';
  }

  function checkAuth(){
    var u = getUser();
    if(REQUIRED && !u.role){
      redirectToLogin();
      return false;
    }
    if(ROLE_REQUIRED && u.role !== ROLE_REQUIRED){
      // 角色不匹配，仅提示不拦截
      console.warn('[AuthGuard] 当前角色: '+u.role+', 建议角色: '+ROLE_REQUIRED);
    }
    updateWelcomeBar();
    return true;
  }

  // DOM Ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', checkAuth);
  }else{
    checkAuth();
  }

  // 暴露全局方法
  window.EPB_AUTH = {
    getUser: getUser,
    isLoggedIn: function(){ return !!getUser().role; },
    logout: function(){
      localStorage.removeItem('epb_user');
      location.href = '/login.html';
    },
    hasPermission: function(perm){
      var u = getUser();
      return (u.permissions||[]).indexOf(perm) >= 0;
    }
  };
})();
