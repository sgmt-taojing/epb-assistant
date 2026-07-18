// === 环保智慧执法 · 全局AI助手 ===
// 基于规则引擎+知识库的智能问答，无需后端AI服务
// 注入方式：在 </body> 前引入 <script src="ai-assistant.js"></script>

(function(){
'use strict';

// 知识库
var KNOWLEDGE = {
  // 法规问答
  '水污染防治法': '《水污染防治法》第八十三条：企业事业单位和其他生产经营者排放水污染物超过国家或者地方规定的水污染物排放标准的，由县级以上人民政府环境保护主管部门责令改正或者责令限制生产、停产整治，并处十万元以上一百万元以下的罚款；情节严重的，报经有批准权的人民政府批准，责令停业、关闭。',
  '大气污染防治法': '《大气污染防治法》第九十九条：超过大气污染物排放标准或者重点大气污染物排放总量控制指标排放大气污染物的，处十万元以上一百万元以下的罚款；情节严重的，责令停业、关闭。',
  '固体废物': '《固体废物污染环境防治法》第一百零二条：擅自倾倒、堆放、丢弃、遗撒工业固体废物，处所需处置费用一倍以上三倍以下的罚款，所需处置费用不足十万元的，按十万元计算。',
  '环境保护法': '《环境保护法》第六十三条：通过暗管、渗井、渗坑、灌注或者篡改、伪造监测数据，或者不正常运行防治污染设施等逃避监管的方式违法排放污染物的，尚不构成犯罪的，处十日以上十五日以下拘留。',
  '噪声': '《噪声污染防治法》第七十五条：超过噪声排放标准排放工业噪声的，处二万元以上二十万元以下的罚款。',
  '排污许可': '《排污许可管理条例》第三十三条：未取得排污许可证排放污染物的，处二十万元以上一百万元以下的罚款。',
  '土壤': '《土壤污染防治法》第八十七条：土壤污染责任人未按照规定进行土壤污染状况调查的，处二万元以上二十万元以下的罚款。',
  '行政处罚': '《环境行政处罚办法》规定：环境行政处罚包括警告、罚款、责令停产整顿、吊销许可证等。罚款金额根据违法行为性质、情节和危害程度确定。',
  '三同时': '"三同时"制度：建设项目的环保设施必须与主体工程同时设计、同时施工、同时投产使用。新建项目必须执行，否则不得投入生产。',
  '危废': '危险废物管理要求：①产生危废的企业必须建立危废贮存间（防渗、防漏、防雨）；②危废转移必须填写转移联单；③危废必须交有资质的单位处置；④建立危废管理台账。',
  '环保信用': '企业环境信用评价：绿牌（环保诚信）、蓝牌（环保良好）、黄牌（环保警示）、红牌（环保不良）。红牌企业将面临联合惩戒：限制贷款、禁止招投标、高频检查等。',
  '碳排放': '碳排放管理：全国碳市场目前覆盖发电行业，CEA（碳排放配额）价格约68元/吨。企业排放量超过配额需购买配额或CCER抵消。超标排放将面临处罚。',
  '自行监测': '持证排污企业必须按照排污许可证要求开展自行监测：①自动监测（在线监测设备24h运行）；②手动监测（按许可证规定频次）；③数据上传至全国排污许可平台。',
  '应急': '突发环境事件分级：特别重大（Ⅰ级）、重大（Ⅱ级）、较大（Ⅲ级）、一般（Ⅳ级）。企业必须编制突发环境事件应急预案并备案，定期演练。',
  '环评': '环境影响评价分三级：报告书（重大影响）、报告表（轻度影响）、登记表（影响很小，网上备案即可）。新建项目必须先完成环评审批才能开工建设。',
};

// 问答规则
var QA_RULES = [
  {k:['COD超标','COD超过','COD排放超标'], a:'COD超标属于水污染物超标排放，依据《水污染防治法》第八十三条，处罚10-100万元。建议使用<a href="penalty-calculator.html" style="color:#60a5fa">自由裁量计算器</a>精确计算处罚金额。如连续超标3天以上，建议立案查处。'},
  {k:['如何举报','怎么举报','举报方法'], a:'环保举报渠道：①拨打12369环保热线（24小时）；②全国生态环境信访投诉举报平台；③本平台<a href="m-report.html" style="color:#60a5fa">在线举报</a>。举报时请提供：被举报对象、污染类型、发生时间、具体位置。举报人信息严格保密。'},
  {k:['执法流程','办案流程','案件流程'], a:'执法全流程：线索发现→立案审批→现场检查→证据固定→案件审查→处罚决定→执行监督→结案归档。详见<a href="enforcement-guide.html" style="color:#60a5fa">执法流程引导</a>。'},
  {k:['危废怎么管理','危废要求','危废贮存'], a:'危废管理要点：①贮存间防渗防漏防雨、标识齐全；②分类贮存、建立台账；③转移填联单、交有资质单位处置；④年度管理计划备案。详见<a href="env-ledger.html" style="color:#60a5fa">企业环保台账</a>。'},
  {k:['排污许可证','排污许可申请','许可证怎么办'], a:'排污许可申领流程：①判断管理类别（重点/简化/登记）；②在全国平台注册；③填报申请材料；④提交申请；⑤技术审查；⑥核发许可证。详见<a href="approval-service.html" style="color:#60a5fa">环保审批服务</a>。'},
  {k:['AQI','空气质量指数','空气质量怎么看'], a:'AQI分为六级：0-50优（绿色）、51-100良（黄色）、101-150轻度污染（橙色）、151-200中度污染（红色）、201-300重度污染（紫色）、>300严重污染（褐红色）。AQI>150建议佩戴口罩。详见<a href="eco-science.html" style="color:#60a5fa">环保科普</a>。'},
  {k:['涉刑','犯罪','移送公安','刑事'], a:'涉嫌污染环境罪的情形：①在饮用水水源一级保护区排放有毒物质；②非法排放含重金属超标3倍以上；③通过暗管渗井等逃避监管方式排放；④篡改伪造监测数据。涉嫌犯罪的应移送公安机关。依据《刑法》第338条。'},
  {k:['设备推荐','治污设备','环保设备'], a:'推荐访问<a href="equipment-mall.html" style="color:#60a5fa">设备商城</a>，14款产品覆盖7大领域，每款都有真实案例和降本增效分析。例如：MBR废水处理一体机（年省11.3万）、VOCs催化燃烧（年省21万）、危废标准化改造（年省15万+）。'},
  {k:['企业风险','风险评估','企业评分'], a:'企业风险画像从5个维度评估：合规、监测、历史记录、整改、应急。查看<a href="risk-profile.html" style="color:#60a5fa">企业风险画像</a>了解8家样本企业的风险评估结果和执法建议。'},
  {k:['环保信用','信用评级','绿牌红牌'], a:'环保信用分四级：绿牌（诚信，90+分）、蓝牌（良好，75-89分）、黄牌（警示，60-74分）、红牌（不良，<60分）。红牌企业面临联合惩戒。详见<a href="credit-rating.html" style="color:#60a5fa">环保信用评级</a>。'},
  {k:['在线监测','CEMS','自动监测'], a:'在线监测系统(CEMS)要求：重点排污企业必须安装在线监测设备，数据实时上传环保监管平台。监测参数包括SO₂、NOx、颗粒物、O₂、温压流等。详见<a href="remote-enforcement.html" style="color:#60a5fa">非现场执法</a>。'},
  {k:['罚款','处罚金额','罚多少'], a:'处罚金额由自由裁量决定，考虑因素：超标倍数、持续时长、损害后果、社会影响、主观过错、整改情况、是否初犯、配合调查。建议使用<a href="penalty-calculator.html" style="color:#60a5fa">自由裁量计算器</a>输入案情自动计算。'},
  {k:['培训','学习','考试'], a:'环保培训资源：①<a href="training.html" style="color:#60a5fa">培训学院</a>提供在线学习+考试；②<a href="eco-science.html" style="color:#60a5fa">环保科普</a>面向公众；③<a href="law-library.html" style="color:#60a5fa">法规库</a>可搜索28部法规；④<a href="capacity-assess.html" style="color:#60a5fa">执法能力评估</a>评估团队效能。'},
  {k:['数据','API','接口'], a:'平台开放19个API端点和13个静态JSON数据集，支持第三方接入。访问<a href="open-data.html" style="color:#60a5fa">数据开放门户</a>查看API文档、数据下载和接入指南。'},
  {k:['碳排放','碳交易','双碳'], a:'碳排放管理：全国碳市场CEA价格约68元/吨。8家纳入碳交易企业需关注配额使用情况。华源化工配额已用92%（超额预警）。详见<a href="carbon-mgmt.html" style="color:#60a5fa">碳排放管理</a>。'},
];

// 默认回答
var DEFAULT_ANSWER = '我是环保智慧执法AI助手，可以帮您解答以下问题：\n• 法规咨询（水/气/固废/噪声等）\n• 执法流程指引\n• 处罚金额计算建议\n• 举报方式\n• 设备推荐\n• 企业合规要求\n\n请直接输入您的问题，或尝试语音指令。';

// 创建UI
var fab = document.createElement('div');
fab.id = 'ai-fab';
fab.innerHTML = '🤖';
fab.style.cssText = [
  'position:fixed','bottom:70px','right:72px','width:52px','height:52px',
  'border-radius:50%','background:linear-gradient(135deg,#10b981,#34d399)',
  'color:#fff','font-size:22px','display:flex','align-items:center','justify-content:center',
  'cursor:pointer','z-index:99998','box-shadow:0 4px 12px rgba(16,185,129,.4)',
  'transition:all .3s','user-select:none','-webkit-tap-highlight-color:transparent'
].join(';');

var chat = document.createElement('div');
chat.id = 'ai-chat';
chat.style.cssText = [
  'position:fixed','bottom:130px','right:16px','width:340px','max-width:calc(100vw - 32px)',
  'height:480px','max-height:calc(100vh - 160px)',
  'background:#0a0e1a','border:1px solid #1e293b','border-radius:16px',
  'z-index:99998','display:none','flex-direction:column',
  'box-shadow:0 8px 32px rgba(0,0,0,.4)','overflow:hidden',
  'font-family:-apple-system,BlinkMacSystemFont,sans-serif'
].join(';');

chat.innerHTML = `
  <div style="padding:14px 16px;background:#111827;border-bottom:1px solid #1e293b;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:14px;font-weight:600;color:#60a5fa">🤖 AI助手</div>
      <div style="font-size:10px;color:#64748b">环保智慧执法 · 智能问答</div>
    </div>
    <span id="ai-close" style="cursor:pointer;font-size:18px;color:#64748b">✕</span>
  </div>
  <div id="ai-messages" style="flex:1;overflow-y:auto;padding:12px;scroll-behavior:smooth">
    <div style="background:#1a2332;border-radius:12px;padding:10px 12px;margin-bottom:8px;font-size:13px;color:#e2e8f0;line-height:1.6">
      您好！我是环保AI助手 🤖<br><br>我可以帮您：<br>• 解答环保法规问题<br>• 指引执法流程<br>• 推荐处罚建议<br>• 查询设备/案例<br><br>请直接输入问题，如"COD超标怎么处罚"、"如何举报"、"危废怎么管理"。
    </div>
  </div>
  <div style="padding:10px 12px;background:#111827;border-top:1px solid #1e293b">
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
      <button class="ai-quick" data-q="COD超标怎么处罚" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">COD超标处罚</button>
      <button class="ai-quick" data-q="如何举报" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">如何举报</button>
      <button class="ai-quick" data-q="危废怎么管理" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">危废管理</button>
      <button class="ai-quick" data-q="执法流程" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">执法流程</button>
    </div>
    <div style="display:flex;gap:8px">
      <input id="ai-input" type="text" placeholder="输入问题..." style="flex:1;padding:10px 12px;background:#1a2332;border:1px solid #1e293b;border-radius:8px;color:#e2e8f0;font-size:13px;outline:none">
      <button id="ai-send" style="padding:10px 14px;border:none;border-radius:8px;background:#3b82f6;color:#fff;font-size:13px;font-weight:600;cursor:pointer">发送</button>
    </div>
  </div>
`;

document.body.appendChild(fab);
document.body.appendChild(chat);

// 显示/隐藏
var isOpen = false;
fab.addEventListener('click', function(){
  isOpen = !isOpen;
  chat.style.display = isOpen ? 'flex' : 'none';
  fab.style.transform = isOpen ? 'scale(1.1)' : 'scale(1)';
  if(isOpen){
    setTimeout(function(){ document.getElementById('ai-input').focus(); }, 100);
  }
});

document.getElementById('ai-close').addEventListener('click', function(){
  isOpen = false;
  chat.style.display = 'none';
  fab.style.transform = 'scale(1)';
});

// 快捷问题
document.querySelectorAll('.ai-quick').forEach(function(btn){
  btn.addEventListener('click', function(){
    var q = btn.getAttribute('data-q');
    document.getElementById('ai-input').value = q;
    sendQuestion(q);
  });
});

// 发送
document.getElementById('ai-send').addEventListener('click', function(){
  var input = document.getElementById('ai-input');
  var q = input.value.trim();
  if(q){
    sendQuestion(q);
    input.value = '';
  }
});

document.getElementById('ai-input').addEventListener('keydown', function(e){
  if(e.key === 'Enter'){
    var q = this.value.trim();
    if(q){
      sendQuestion(q);
      this.value = '';
    }
  }
});

// 添加消息
function addMessage(text, isUser){
  var msgs = document.getElementById('ai-messages');
  var div = document.createElement('div');
  if(isUser){
    div.style.cssText = 'background:#3b82f6;border-radius:12px 12px 4px 12px;padding:10px 12px;margin-bottom:8px;margin-left:40px;font-size:13px;color:#fff;line-height:1.6';
  } else {
    div.style.cssText = 'background:#1a2332;border-radius:12px 12px 12px 4px;padding:10px 12px;margin-bottom:8px;margin-right:40px;font-size:13px;color:#e2e8f0;line-height:1.6';
  }
  div.innerHTML = text.replace(/\n/g, '<br>');
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

// AI回答
function getAnswer(question){
  var q = question.toLowerCase().trim();

  // 检查知识库
  for(var key in KNOWLEDGE){
    if(q.indexOf(key.toLowerCase()) >= 0 || key.toLowerCase().indexOf(q) >= 0){
      return KNOWLEDGE[key];
    }
  }

  // 检查规则
  for(var i=0; i<QA_RULES.length; i++){
    var rule = QA_RULES[i];
    for(var j=0; j<rule.k.length; j++){
      if(q.indexOf(rule.k[j]) >= 0){
        return rule.a;
      }
    }
  }

  // 页面导航
  var navMap = {
    '商城':'equipment-mall.html','设备':'equipment-mall.html',
    '法规':'law-library.html','法律':'law-library.html',
    '驾驶舱':'data-cockpit.html','数据':'data-cockpit.html',
    '预警':'smart-alert.html','告警':'smart-alert.html',
    '地图':'env-map.html','一张图':'env-map.html',
    '无人机':'drone-patrol.html',
    '应急':'emergency-center.html',
    '信用':'credit-rating.html',
    '风险':'risk-profile.html',
    '裁量':'penalty-calculator.html','处罚计算':'penalty-calculator.html',
    '文书':'doc-generator.html',
    '科普':'eco-science.html',
    '台账':'env-ledger.html',
    '审批':'approval-service.html',
    '碳':'carbon-mgmt.html',
    '金融':'green-finance.html',
    '管家':'eco-manager.html',
    '互动':'public-interact.html',
    '举报':'m-report.html',
    '流程':'enforcement-guide.html',
    '取证':'evidence-toolkit.html',
    '培训':'training.html',
    '知识图谱':'knowledge-graph.html',
    '统计':'eco-statistics.html',
    '督察':'inspection.html',
    '总览':'overview.html',
    '门户':'m-portal.html',
    '控制台':'sys-console.html',
    '数据开放':'open-data.html',
  };
  for(var key in navMap){
    if(q.indexOf(key) >= 0){
      return '正在为您打开' + key + '页面... <a href="' + navMap[key] + '" style="color:#60a5fa">点击进入</a>';
    }
  }

  return DEFAULT_ANSWER;
}

function sendQuestion(q){
  addMessage(q, true);
  // 模拟AI思考
  setTimeout(function(){
    var answer = getAnswer(q);
    addMessage(answer, false);
  }, 300);
}

// 自动欢迎（首次访问）
if(!sessionStorage.getItem('ai_welcomed')){
  sessionStorage.setItem('ai_welcomed', '1');
  setTimeout(function(){
    fab.style.animation = 'bounce 0.5s ease 2';
    setTimeout(function(){ fab.style.animation = ''; }, 2000);
  }, 3000);
}

// 添加bounce动画
var style = document.createElement('style');
style.textContent = '@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}';
document.head.appendChild(style);

})();
