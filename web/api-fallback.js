// api-fallback.js — 全局API降级组件
// 当后端不可用（GitHub Pages / 404 / 非JSON响应）时自动切换到 api-data/*.json
(function() {
  'use strict';

  var FallbackMap = {
    '/api/health': '/api-data/health.json',
    '/api/tasks': '/api-data/tasks.json',
    '/api/cases': '/api-data/cases.json',
    '/api/law_index': '/api-data/law_index.json',
    '/api/law_mapping': '/api-data/law_mapping.json',
    '/api/knowledge_graph': '/api-data/knowledge_graph.json',
    '/api/enterprises': '/api-data/enterprises.json',
    '/api/devices': '/api-data/devices.json',
    '/api/device_types': '/api-data/device_types.json',
    '/api/roles': '/api-data/roles.json',
    '/api/users': '/api-data/users.json',
    '/api/tenant': '/api-data/tenant.json',
    '/api/config': '/api-data/config.json',
    '/api/report': '/api-data/health.json',
    '/api/equipment': '/api-data/equipment.json',
    '/api/equipment/categories': '/api-data/equipment_categories.json',
    '/api/search': '/api-data/cases.json'
  };

  function getFallback(url) {
    var clean = url.split('?')[0].replace(/\/$/, '');
    return FallbackMap[clean] || FallbackMap[url];
  }

  var _origFetch = window.fetch;
  window.fetch = function(url, opts) {
    // 如果直接请求 api-data/，不走降级
    if (typeof url === 'string' && url.indexOf('/api-data/') !== -1) {
      return _origFetch(url, opts);
    }
    return _origFetch(url, opts).then(function(res) {
      // 网络层OK但HTTP 404/500 → 触发降级
      if (!res.ok && typeof url === 'string') {
        var fb = getFallback(url);
        if (fb) {
          console.log('[api-fallback] ' + url + ' HTTP' + res.status + ' -> ' + fb);
          return _origFetch(fb);
        }
      }
      // HTTP 200 但内容是HTML（GitHub Pages 404.html被200返回的情况）
      if (res.ok && typeof url === 'string' && url.indexOf('/api/') !== -1) {
        var ct = res.headers.get('content-type') || '';
        if (ct.indexOf('text/html') !== -1) {
          var fb2 = getFallback(url);
          if (fb2) {
            console.log('[api-fallback] ' + url + ' got HTML -> ' + fb2);
            return _origFetch(fb2);
          }
        }
      }
      return res;
    }).catch(function(err) {
      // 网络错误 → 触发降级
      if (typeof url === 'string') {
        var fb = getFallback(url);
        if (fb) {
          console.log('[api-fallback] ' + url + ' network error -> ' + fb);
          return _origFetch(fb);
        }
      }
      throw err;
    });
  };

  console.log('[api-fallback] 已加载，监控 ' + Object.keys(FallbackMap).length + ' 个API端点');
})();