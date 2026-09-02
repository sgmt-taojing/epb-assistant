// === AI 实时检查指导（语音教练）===
// 依赖 voice-assistant.js 已注入浮窗；本模块扩展"现场教练模式"：
// 连续聆听 → /api/voice_coach 意图识别 → 本地 TTS 播报（P95 < 500ms）
// 无专业知识的人说"这项怎么查"即得手把手指导
(function(){
'use strict';
if (window.__VOICE_COACH_LOADED) return;
window.__VOICE_COACH_LOADED = true;

var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
var TTS = window.speechSynthesis;
if (!SR) { console.log('[voice-coach] 浏览器不支持语音识别'); return; }

// ---- 状态 ----
var listening = false;
var rec = null;
var lastHeard = '';
var CONTEXT = { checkPoint: '', checklist: null };

// ---- UI：教练按钮（挂在语音助手旁） ----
var fab = document.createElement('div');
fab.id = 'vc-fab';
fab.innerHTML = '🧭';
fab.title = 'AI 现场教练（连续语音指导）';
fab.style.cssText = [
  'position:fixed','bottom:130px','right:16px','width:52px','height:52px',
  'border-radius:50%','background:linear-gradient(135deg,#059669,#10b981)',
  'color:#fff','font-size:22px','display:flex','align-items:center','justify-content:center',
  'cursor:pointer','z-index:99997','box-shadow:0 4px 12px rgba(16,185,129,.4)',
  'transition:all .3s','user-select:none'
].join(';');

// 教练面板
var panel = document.createElement('div');
panel.id = 'vc-panel';
panel.style.cssText = [
  'position:fixed','bottom:190px','right:16px','width:320px','max-width:calc(100vw - 32px)',
  'background:#0f172a','border:1px solid #065f46','border-radius:12px',
  'padding:16px','z-index:99997','display:none','box-shadow:0 8px 24px rgba(0,0,0,.35)',
  'font-family:-apple-system,BlinkMacSystemFont,sans-serif','color:#e2e8f0'
].join(';');
panel.innerHTML = `
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="font-size:14px;font-weight:600;color:#10b981">🧭 AI 现场教练</span>
    <span id="vc-close" style="cursor:pointer;font-size:18px;color:#64748b">✕</span>
  </div>
  <div id="vc-state" style="font-size:11px;color:#10b981;margin-bottom:8px">● 待命（点击开始连续聆听）</div>
  <div id="vc-live" style="font-size:12px;color:#94a3b8;margin-bottom:10px;min-height:34px;background:#1a2332;border-radius:8px;padding:8px;display:none">您说：…</div>
  <div id="vc-reply" style="font-size:13px;color:#e2e8f0;margin-bottom:10px;min-height:50px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.25);border-radius:8px;padding:10px;line-height:1.6">教练待命。说"这项怎么查""拍什么""问什么话术""紧急情况"即可获得实时指导。</div>
  <div style="margin-bottom:8px;font-size:11px">
    <label style="display:flex;align-items:center;gap:6px;color:#94a3b8;cursor:pointer">
      <input type="checkbox" id="vc-speaker-push" style="accent-color:#10b981">
      📻 同步推送到现场音箱/眼镜（骨传导）
    </label>
  </div>
  <div style="font-size:11px;color:#64748b;line-height:1.7">
    <b style="color:#94a3b8">可以这样问：</b><br>
    • "这项怎么查" / "指导 暗管检查"<br>
    • "拍什么" / "怎么取证"<br>
    • "问什么话术" / "下一步"<br>
    • "泄漏了怎么办"（应急）
  </div>
`;

document.addEventListener('DOMContentLoaded', function(){
  document.body.appendChild(fab);
  document.body.appendChild(panel);
  fab.addEventListener('click', togglePanel);
  document.getElementById('vc-close').addEventListener('click', function(){ panel.style.display='none'; stopListening(); });
});

function togglePanel(){
  panel.style.display = panel.style.display==='none' ? 'block' : 'none';
  if (panel.style.display==='block' && !listening) startListening();
}

// ---- 语音识别（连续模式） ----
function startListening(){
  if (!SR) return;
  listening = true;
  fab.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';
  fab.innerHTML = '🔴';
  setState('● 聆听中（持续）');
  rec = new SR();
  rec.lang = 'zh-CN';
  rec.continuous = true;
  rec.interimResults = false;
  rec.onresult = function(e){
    var text = '';
    for (var i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) text += e.results[i][0].transcript;
    }
    text = text.trim();
    if (text && text !== lastHeard) {
      lastHeard = text;
      onHeard(text);
    }
  };
  rec.onerror = function(e){
    if (e.error === 'not-allowed') { setState('⚠️ 麦克风权限被拒'); stopListening(); }
  };
  rec.onend = function(){
    // 连续模式：意外结束后自动重启
    if (listening) { try { rec.start(); } catch(e){} }
  };
  try { rec.start(); } catch(e){}
  speakLocal('现场教练已就绪，请讲。');
}

function stopListening(){
  listening = false;
  fab.style.background = 'linear-gradient(135deg,#059669,#10b981)';
  fab.innerHTML = '🧭';
  setState('● 待命');
  if (rec) { try { rec.stop(); } catch(e){} }
}

function setState(s){
  var el = document.getElementById('vc-state');
  if (el) el.textContent = s;
}

function showLive(text){
  var el = document.getElementById('vc-live');
  if (el) { el.style.display='block'; el.textContent = '您说：' + text; }
}

function showReply(text){
  var el = document.getElementById('vc-reply');
  if (el) el.textContent = text;
}

// ---- 核心：听到 → 意图 → 指导 → 播报 ----
function onHeard(text){
  showLive(text);
  // 感知当前页面上下文（检查工作台的当前项）
  var ctxEl = document.querySelector('.item.current .name, .item.active .name, #current-check-point');
  CONTEXT.checkPoint = ctxEl ? ctxEl.textContent.replace(/^\d+\.\s*/, '') : '';

  var speakerEl = document.getElementById('vc-speaker-push');
  fetch('/api/voice_coach', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ text: text, context: CONTEXT.checkPoint, push_to_speaker: speakerEl && speakerEl.checked ? 1 : 0 })
  })
  .then(function(r){ return r.json(); })
  .then(function(d){
    if (d && d.ok && d.reply) {
      var sp = d.speaker_push;
      var spTag = sp ? (sp.pushed ? ' <span style="color:#10b981;font-size:11px">📻 已推音箱' + (sp.audio_bytes ? '(' + Math.round(sp.audio_bytes/1024) + 'KB)' : '') + '</span>' : ' <span style="color:#f59e0b;font-size:11px">📻 音箱不可达</span>') : '';
      showReply('🧭 ' + d.reply + spTag);
      // 音箱已推就不本地重复播（防双声）；音箱未开/失败才本地播
      if (!(sp && sp.pushed)) speakLocal(d.reply);
    } else {
      showReply('教练暂时没听懂，可以换种说法。');
    }
  })
  .catch(function(){
    // 断网兜底：本地关键词指导（保底不静默）
    var local = localCoach(text);
    showReply('🧭 ' + local + '（离线模式）');
    speakLocal(local);
  });
}

// ---- 本地 TTS ----
function speakLocal(text){
  if (!TTS) return;
  try {
    TTS.cancel();
    var u = new SpeechSynthesisUtterance(text.slice(0, 200));
    u.lang = 'zh-CN';
    u.rate = 1.05;
    TTS.speak(u);
  } catch(e){}
}

// ---- 断网兜底指导（最关键的几条内置） ----
function localCoach(text){
  if (/泄漏|着火|爆炸|中毒|紧急/.test(text)) {
    return '突发情况：人员撤到上风向，拨12369，安全前提下拍照记录，提醒企业启动应急预案。不要擅自处置不明化学品。';
  }
  if (/拍什么|取证|拍照/.test(text)) {
    return '取证三要素：全景带参照物、特写带时间水印、连续视频全过程。';
  }
  if (/问什么|话术/.test(text)) {
    return '问日常管理流程，不问你们违法了吗；让他自己拿记录；与台账交叉验证。全程开执法记录仪。';
  }
  if (/下一步|然后/.test(text)) {
    return '按高风险优先顺序检查下一项，完成一项记录一项。';
  }
  return '网络暂不可用。核心口诀：先看现场、再对台账、有异常先拍照、及时记录。';
}

// ---- 对外接口：检查工作台设置当前项 ----
window.__VC_SET_CONTEXT = function(checkPoint){
  CONTEXT.checkPoint = checkPoint || '';
};
window.__VC_TOGGLE = togglePanel;
})();
