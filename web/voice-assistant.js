// === 环保智慧执法 · 全局语音助手 ===
// 使用 Web Speech API（ASR + TTS），无需后端依赖
// 注入方式：在 </body> 前引入 <script src="voice-assistant.js"></script>

(function(){
'use strict';

// 检测浏览器支持
var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
var TTS = window.speechSynthesis;

// 创建浮窗UI
var fab = document.createElement('div');
fab.id = 'va-fab';
fab.innerHTML = '🎤';
fab.style.cssText = [
  'position:fixed','bottom:70px','right:16px','width:52px','height:52px',
  'border-radius:50%','background:linear-gradient(135deg,#3b82f6,#60a5fa)',
  'color:#fff','font-size:22px','display:flex','align-items:center','justify-content:center',
  'cursor:pointer','z-index:99996','box-shadow:0 4px 12px rgba(59,130,246,.4)',
  'transition:all .3s','user-select:none','-webkit-tap-highlight-color:transparent'
].join(';');

// 面板
var panel = document.createElement('div');
panel.id = 'va-panel';
panel.style.cssText = [
  'position:fixed','bottom:130px','right:16px','width:300px','max-width:calc(100vw - 32px)',
  'background:#111827','border:1px solid #1e293b','border-radius:12px',
  'padding:16px','z-index:99996','display:none','box-shadow:0 8px 24px rgba(0,0,0,.3)',
  'font-family:-apple-system,BlinkMacSystemFont,sans-serif','color:#e2e8f0'
].join(';');

panel.innerHTML = `
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
    <span style="font-size:14px;font-weight:600;color:#60a5fa">语音助手</span>
    <span id="va-close" style="cursor:pointer;font-size:18px;color:#64748b">✕</span>
  </div>
  <div id="va-status" style="font-size:12px;color:#64748b;margin-bottom:12px;min-height:18px">点击下方按钮开始语音交互</div>
  <div id="va-transcript" style="font-size:13px;color:#e2e8f0;margin-bottom:12px;min-height:40px;background:#1a2332;border-radius:8px;padding:10px;display:none"></div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <button id="va-btn-listen" style="flex:1;padding:10px 8px;border:none;border-radius:8px;background:#3b82f6;color:#fff;font-size:12px;font-weight:600;cursor:pointer;min-width:80px">🎙 语音指令</button>
    <button id="va-btn-read" style="flex:1;padding:10px 8px;border:none;border-radius:8px;background:#10b981;color:#fff;font-size:12px;font-weight:600;cursor:pointer;min-width:80px">🔊 朗读页面</button>
    <button id="va-btn-stop" style="flex:1;padding:10px 8px;border:none;border-radius:8px;background:#64748b;color:#fff;font-size:12px;font-weight:600;cursor:pointer;min-width:60px">⏹ 停止</button>
  </div>
  <div style="margin-top:12px;font-size:11px;color:#64748b">
    <div style="font-weight:600;margin-bottom:4px">语音指令示例：</div>
    <div>• "打开设备商城" / "打开法规库"</div>
    <div>• "搜索水污染" / "搜索COD超标"</div>
    <div>• "举报" / "执法流程"</div>
    <div>• "朗读" / "停止朗读"</div>
  </div>
`;

document.body.appendChild(fab);
document.body.appendChild(panel);

// 页面导航映射
var NAV_MAP = {
  '首页':'index.html','主页':'index.html','平台':'index.html',
  '门户':'m-portal.html','移动端':'m-portal.html',
  '总览':'overview.html','看板':'overview.html',
  '仪表盘':'dashboard.html','驾驶舱':'data-cockpit.html',
  '统计':'eco-statistics.html',
  '一张图':'env-map.html','地图':'env-map.html',
  '执法':'field-terminal.html','现场执法':'field-terminal.html','执法终端':'field-terminal.html',
  '流程':'enforcement-guide.html','执法流程':'enforcement-guide.html',
  '取证':'evidence-toolkit.html','工具箱':'evidence-toolkit.html',
  '裁量':'penalty-calculator.html','处罚计算':'penalty-calculator.html',
  '文书':'doc-generator.html','执法文书':'doc-generator.html',
  '案例分析':'case-analysis.html','案例':'m-cases.html',
  '风险':'risk-profile.html','风险画像':'risk-profile.html',
  '信用':'credit-rating.html','信用评级':'credit-rating.html',
  '督察':'inspection.html','督察整改':'inspection.html',
  '非现场':'remote-enforcement.html','在线监测':'remote-enforcement.html',
  '预警':'smart-alert.html','智能预警':'smart-alert.html',
  '感知':'sensor-dashboard.html','传感器':'sensor-dashboard.html',
  '无人机':'drone-patrol.html',
  '物联':'iot.html','设备管理':'device-mgmt.html',
  '应急':'emergency-center.html','应急指挥':'emergency-center.html',
  '知识图谱':'knowledge-graph.html','图谱':'knowledge-graph.html',
  '知识库':'knowledge.html',
  '法规':'law-library.html','法规库':'law-library.html',
  '科普':'eco-science.html','环保科普':'eco-science.html',
  '周报':'ai-report.html','月报':'ai-report.html','报告':'ai-report.html',
  '能力评估':'capacity-assess.html',
  'ehs':'ehs.html','企业ehs':'ehs.html',
  '台账':'env-ledger.html','环保台账':'env-ledger.html',
  '自查':'self-check.html','合规':'self-check.html',
  '审批':'approval-service.html',
  '碳':'carbon-mgmt.html','碳排放':'carbon-mgmt.html',
  '金融':'green-finance.html','绿色金融':'green-finance.html',
  '管家':'eco-manager.html','环保管家':'eco-manager.html',
  '商城':'equipment-mall.html','设备':'equipment-mall.html',
  '互动':'public-interact.html','公众':'public-interact.html',
  '举报':'m-report.html',
  '协同':'collaboration.html',
  '工作台':'m-workspace.html','工作空间':'workspace.html',
  '培训':'training.html',
  '视频':'video-studio.html',
  '管理':'admin.html','后台':'admin.html',
  '控制台':'sys-console.html','系统':'sys-console.html',
  '数据开放':'open-data.html','api':'open-data.html',
  '登录':'login.html',
  '微信':'wechat-h5.html','h5':'wechat-h5.html',
  '分析':'analysis.html'
};

// 面板显示/隐藏
var isOpen = false;
fab.addEventListener('click', function(){
  isOpen = !isOpen;
  panel.style.display = isOpen ? 'block' : 'none';
  fab.style.transform = isOpen ? 'scale(1.1)' : 'scale(1)';
});

document.getElementById('va-close').addEventListener('click', function(){
  isOpen = false;
  panel.style.display = 'none';
  fab.style.transform = 'scale(1)';
  stopAll();
});

// ASR 语音识别
var recognition = null;
var isListening = false;

function initRecognition(){
  if(!SR){
    setStatus('⚠️ 当前浏览器不支持语音识别，请使用Chrome/Edge', '#fca5a5');
    return null;
  }
  var r = new SR();
  r.lang = 'zh-CN';
  r.continuous = false;
  r.interimResults = true;
  r.onstart = function(){
    isListening = true;
    var btn = document.getElementById('va-btn-listen');
    btn.style.background = '#ef4444';
    btn.textContent = '🔴 正在听...';
    setStatus('正在聆听...请说话', '#60a5fa');
    fab.style.animation = 'pulse 1s infinite';
  };
  r.onresult = function(event){
    var transcript = '';
    for(var i=0; i<event.results.length; i++){
      transcript += event.results[i][0].transcript;
    }
    var tEl = document.getElementById('va-transcript');
    tEl.style.display = 'block';
    tEl.textContent = transcript;
    if(event.results[event.results.length-1].isFinal){
      handleCommand(transcript.trim());
    }
  };
  r.onerror = function(event){
    setStatus('语音识别错误: ' + event.error, '#fca5a5');
    resetListenBtn();
  };
  r.onend = function(){
    resetListenBtn();
  };
  return r;
}

function resetListenBtn(){
  isListening = false;
  var btn = document.getElementById('va-btn-listen');
  btn.style.background = '#3b82f6';
  btn.textContent = '🎙 语音指令';
  fab.style.animation = '';
}

function startListening(){
  if(isListening) return;
  if(!recognition) recognition = initRecognition();
  if(!recognition) return;
  try {
    recognition.start();
  } catch(e) {
    // already started
  }
}

function stopListening(){
  if(recognition && isListening){
    recognition.stop();
  }
}

document.getElementById('va-btn-listen').addEventListener('click', function(){
  if(isListening){
    stopListening();
  } else {
    startListening();
  }
});

// 命令处理
function handleCommand(text){
  setStatus('识别结果: ' + text, '#e2e8f0');
  var lower = text.toLowerCase();

  // 停止朗读
  if(text.indexOf('停止') >= 0 || text.indexOf('停下') >= 0){
    stopSpeaking();
    return;
  }

  // 朗读页面
  if(text.indexOf('朗读') >= 0 || text.indexOf('念') >= 0 || text.indexOf('读一下') >= 0){
    speakPage();
    return;
  }

  // 搜索
  if(text.indexOf('搜索') >= 0 || text.indexOf('查找') >= 0 || text.indexOf('查') >= 0){
    var keyword = text.replace(/搜索|查找|查一下|查/g, '').trim();
    if(keyword){
      window.location.href = 'knowledge.html?q=' + encodeURIComponent(keyword);
      return;
    }
  }

  // 举报
  if(text.indexOf('举报') >= 0){
    window.location.href = 'm-report.html';
    return;
  }

  // 页面导航
  for(var key in NAV_MAP){
    if(text.indexOf(key) >= 0){
      setStatus('正在跳转: ' + key, '#10b981');
      window.location.href = NAV_MAP[key];
      return;
    }
  }

  // 未匹配
  setStatus('未识别指令: "' + text + '"，请尝试"打开设备商城"等', '#fcd34d');
}

// TTS 语音合成
var isSpeaking = false;

function speakPage(){
  if(!TTS){
    setStatus('⚠️ 当前浏览器不支持语音合成', '#fca5a5');
    return;
  }
  stopSpeaking();

  // 提取页面主要内容文本
  var title = document.title || '';
  var h1 = '';
  var h1El = document.querySelector('h1');
  if(h1El) h1 = h1El.textContent;
  var pText = '';
  var paragraphs = document.querySelectorAll('p, .section-title, .stat-card .label, .kpi-label, .tool-name, .cat-name, .module-name, .activity-name, .product-card h3, .ent-name, .law-name, .notice-title');
  for(var i=0; i<Math.min(paragraphs.length, 20); i++){
    var t = paragraphs[i].textContent.trim();
    if(t.length > 5) pText += t + '。';
  }

  var fullText = (h1 || title) + '。' + pText;
  if(fullText.length > 500) fullText = fullText.substring(0, 500) + '...';

  var utter = new SpeechSynthesisUtterance(fullText);
  utter.lang = 'zh-CN';
  utter.rate = 1.0;
  utter.pitch = 1.0;
  utter.onstart = function(){
    isSpeaking = true;
    setStatus('正在朗读页面内容...', '#10b981');
  };
  utter.onend = function(){
    isSpeaking = false;
    setStatus('朗读完毕', '#64748b');
  };
  utter.onerror = function(){
    isSpeaking = false;
    setStatus('朗读出错', '#fca5a5');
  };
  TTS.speak(utter);
}

function stopSpeaking(){
  if(TTS){
    TTS.cancel();
    isSpeaking = false;
  }
}

document.getElementById('va-btn-read').addEventListener('click', speakPage);
document.getElementById('va-btn-stop').addEventListener('click', function(){
  stopSpeaking();
  stopListening();
  setStatus('已停止', '#64748b');
});

function setStatus(msg, color){
  var el = document.getElementById('va-status');
  el.textContent = msg;
  el.style.color = color || '#64748b';
}

// 浏览器兼容性提示
if(!SR && !TTS){
  fab.style.opacity = '0.5';
  fab.title = '当前浏览器不支持语音功能，请使用Chrome/Edge';
}

})();
