// === 环保智慧执法 · 全局AI助手（多角色版）===
// 基于规则引擎+知识库的智能问答，支持公众/企业/政府/监管/执法五角色
// 注入方式：在 </body> 前引入 <script src="ai-assistant.js"></script>

(function(){
'use strict';

// 知识库
var KNOWLEDGE = {
  '水污染防治法': '《水污染防治法》第八十三条：超标排放水污染物的，处十万元以上一百万元以下的罚款；情节严重的，责令停业、关闭。',
  '大气污染防治法': '《大气污染防治法》第九十九条：超标排放大气污染物的，处十万元以上一百万元以下的罚款；情节严重的，责令停业、关闭。',
  '固体废物': '《固体废物污染环境防治法》第一百零二条：擅自倾倒、堆放工业固体废物，处所需处置费用一倍以上三倍以下的罚款，不足十万元的按十万元计算。',
  '环境保护法': '《环境保护法》第六十三条：通过暗管、渗井、渗坑或篡改监测数据等逃避监管方式排放污染物的，处十日以上十五日以下拘留。',
  '噪声': '《噪声污染防治法》第七十五条：超过噪声排放标准排放工业噪声的，处二万元以上二十万元以下的罚款。',
  '排污许可': '《排污许可管理条例》第三十三条：未取得排污许可证排放污染物的，处二十万元以上一百万元以下的罚款。',
  '土壤': '《土壤污染防治法》第八十七条：未按规定进行土壤污染状况调查的，处二万元以上二十万元以下的罚款。',
  '行政处罚': '环境行政处罚包括警告、罚款、责令停产整顿、吊销许可证等。罚款金额根据违法性质、情节和危害程度确定。',
  '三同时': '"三同时"制度：环保设施必须与主体工程同时设计、同时施工、同时投产使用。',
  '危废': '危废管理要求：①贮存间防渗防漏防雨、标识齐全；②转移填联单、交有资质单位处置；③建立危废管理台账。',
  '环保信用': '环保信用分四级：绿牌（诚信）、蓝牌（良好）、黄牌（警示）、红牌（不良）。红牌企业面临联合惩戒。',
  '碳排放': '全国碳市场CEA价格约68元/吨。企业排放超配额需购买配额或CCER抵消。',
  '自行监测': '持证排污企业必须按许可证要求开展自行监测：自动监测+手动监测，数据上传全国排污许可平台。',
  '应急': '突发环境事件分四级：Ⅰ级（特别重大）、Ⅱ级（重大）、Ⅲ级（较大）、Ⅳ级（一般）。企业必须编制应急预案并备案。',
  '环评': '环评分三级：报告书（重大影响）、报告表（轻度影响）、登记表（影响很小，网上备案即可）。',
};

// 问答规则（按角色标注）
var QA_RULES = [
  // === 公众角色 ===
  {role:'公众', k:['如何举报','怎么举报','举报方法','怎么投诉'], a:'📋 举报渠道：\n① 拨打12369环保热线（24小时）\n② 全国生态环境信访投诉平台\n③ <a href="m-report.html" style="color:#60a5fa">本平台在线举报</a>\n\n举报时请提供：企业名称/地址、污染类型、发生时间。举报人信息严格保密，处理后及时反馈。'},
  {role:'公众', k:['空气不好','雾霾','PM2.5','空气质量'], a:'💨 查看实时空气质量：访问<a href="sensor-dashboard.html" style="color:#60a5fa">天地一体感知</a>查看6个空气站实时数据。\n\nAQI分级：0-50优、51-100良、101-150轻度污染、>150建议戴口罩。详情见<a href="eco-science.html" style="color:#60a5fa">环保科普</a>。'},
  {role:'公众', k:['水污染','河水脏','河水臭','排污口'], a:'💧 如发现水体异常（变色、异味、死鱼等），请立即拍照记录并<a href="m-report.html" style="color:#60a5fa">一键举报</a>。水质数据可在<a href="sensor-dashboard.html" style="color:#60a5fa">感知中心</a>查看6个水质监测站实时数据。'},
  {role:'公众', k:['噪声扰民','噪音','吵','广场舞'], a:'🔊 噪声举报分类：\n• 工业/施工噪声 → 拨打12369（环保部门）\n• 社会生活噪声（装修/商铺/广场舞）→ 拨打110（公安部门）\n\n可通过<a href="m-report.html" style="color:#60a5fa">移动举报</a>提交噪声投诉。'},
  {role:'公众', k:['环保积分','志愿者','参加活动'], a:'👥 欢迎参与环保！访问<a href="public-interact.html" style="color:#60a5fa">公众互动中心</a>：\n• 8种积分任务（举报+50分、学习+5分）\n• 5个志愿活动可报名\n• 8种积分兑换商品\n• 5级等级体系（环保新星→环保大使）'},
  {role:'公众', k:['垃圾分类','垃圾怎么分','废物分类'], a:'🗑️ 固废分类：\n• 生活垃圾：厨余/废纸/塑料→分类投放\n• 危废：废电池/废机油/过期药品→指定回收点\n• 建筑垃圾：混凝土/砖瓦→资源化利用\n\n详情见<a href="eco-science.html" style="color:#60a5fa">环保科普</a>固废分类板块。'},
  {role:'公众', k:['环保科普','环保知识','学习环保'], a:'🌱 环保科普中心提供5个板块：\n• 空气质量（AQI解读+防护建议）\n• 水环境（5类水质标准+污染识别）\n• 固废分类（6类+危废应急）\n• 举报指南（渠道+流程+保护）\n• 常见问题（8条FAQ）\n\n访问<a href="eco-science.html" style="color:#60a5fa">环保科普</a>开始学习。'},

  // === 企业角色 ===
  {role:'企业', k:['排污许可证','排污许可申请','许可证怎么办','许可证到期'], a:'📋 排污许可申领流程：\n① 判断管理类别（重点/简化/登记）\n② 全国平台注册 permit.mee.gov.cn\n③ 填报申请材料\n④ 提交→技术审查→核发\n\n重点管理5年有效期，需提前30日申请延续。详见<a href="approval-service.html" style="color:#60a5fa">环保审批服务</a>。'},
  {role:'企业', k:['环评','环评怎么办','环评报告','环境影响评价'], a:'📝 环评审批流程：\n① 项目备案 → ② 确定环评等级 → ③ 委托编制 → ④ 公众参与（报告书）→ ⑤ 报送审批 → ⑥ 技术评估 → ⑦ 审批决定\n\n报告书60工作日、报告表30工作日、登记表即办。详见<a href="approval-service.html" style="color:#60a5fa">审批服务</a>。'},
  {role:'企业', k:['危废怎么管理','危废要求','危废贮存','危废处置'], a:'⚠️ 危废管理四步法：\n① 贮存：防渗防漏防雨+标识齐全+分类存放\n② 台账：记录产生量、贮存量、转移量\n③ 转移：填写转移联单，交有资质单位\n④ 备案：年度管理计划备案\n\n查看<a href="env-ledger.html" style="color:#60a5fa">企业环保台账</a>管理危废记录。'},
  {role:'企业', k:['自行监测','监测要求','在线监测','监测怎么做'], a:'📊 自行监测要求：\n• 自动监测：重点排污企业24h在线（COD/氨氮/pH等）\n• 手动监测：按许可证频次（季度/月度）\n• 数据上传：全国排污许可平台\n• 设备校准：定期标定\n\n详见<a href="env-ledger.html" style="color:#60a5fa">企业台账-监测数据</a>。'},
  {role:'企业', k:['环保信用','信用评级','绿牌','红牌'], a:'⭐ 环保信用评价：\n• 绿牌（90+分）：专项资金优先+信贷绿色通道+减少检查\n• 蓝牌（75-89分）：正常管理\n• 黄牌（60-74分）：加大检查+限制资金\n• 红牌（<60分）：联合惩戒+高频检查\n\n查看<a href="credit-rating.html" style="color:#60a5fa">信用评级</a>了解评分标准。'},
  {role:'企业', k:['设备推荐','治污设备','环保设备','技改'], a:'🛒 推荐访问<a href="equipment-mall.html" style="color:#60a5fa">设备商城</a>，14款产品覆盖7大领域：\n• 废水处理（MBR一体机，年省11.3万）\n• VOCs治理（催化燃烧，年省21万）\n• 危废改造（标准化套装，年省15万+）\n• 污泥干化（年省43.8万）\n每款都有真实案例和ROI分析。'},
  {role:'企业', k:['贷款','融资','资金','绿色金融'], a:'💰 绿色金融产品：\n• 环保技改专项贷（3.85%，≤500万）\n• 绿色供应链票据贴现（2.95%，T+1）\n• 排污权抵押贷款（4.20%，≤300万）\n• 碳配额质押融资（4.50%）\n\n还有4项补贴政策可申领。详见<a href="green-finance.html" style="color:#60a5fa">绿色金融</a>。'},
  {role:'企业', k:['碳排放','碳交易','碳配额','双碳'], a:'🌱 碳排放管理：\n• 8家企业纳入碳交易\n• CEA价格68元/吨，CCER 42元/吨\n• 华源化工配额已用92%（预警）\n• 减碳路径：光伏/余热回收/电机变频\n\n详见<a href="carbon-mgmt.html" style="color:#60a5fa">碳排放管理</a>。'},
  {role:'企业', k:['环保管家','第三方','服务商','运维'], a:'🔧 <a href="eco-manager.html" style="color:#60a5fa">环保管家</a>提供10家第三方服务商：\n• 监测检测（CMA认证）\n• 污染治理（MBR/除尘/脱硫脱硝）\n• 环评咨询（环评/排污许可/应急预案）\n• 运维服务（在线监测/用电监控/SaaS）\n可在线对接，查看评分和响应时间。'},
  {role:'企业', k:['台账','记录','环保档案'], a:'📚 <a href="env-ledger.html" style="color:#60a5fa">企业环保台账</a>包含8类：\n• 排污许可证+环评报告+应急预案\n• 危废管理计划+自行监测方案\n• 治污设施运行记录+危废转移联单\n• 环境管理制度\n台账保存期不少于3年。'},
  {role:'企业', k:['自查','合规检查','自我检查'], a:'✅ 使用<a href="self-check.html" style="color:#60a5fa">合规自查</a>或<a href="m-self-check.html" style="color:#60a5fa">移动自查</a>：\n• 选择行业类型\n• 逐项检查合规状态\n• 生成自查报告\n• 发现问题及时整改'},
  {role:'企业', k:['应急预案','应急备案','突发环境事件'], a:'🆘 应急预案要求：\n① 编制突发环境事件应急预案\n② 向环保部门备案\n③ 定期演练（每年至少1次）\n④ 应急物资储备\n\n应急预案有效期3年，到期需修订重新备案。详见<a href="approval-service.html" style="color:#60a5fa">审批服务</a>。'},

  // === 执法角色 ===
  {role:'执法', k:['COD超标','COD超过','超标处罚'], a:'⚖️ COD超标处罚：\n• 依据：《水污染防治法》第八十三条\n• 罚款：10-100万元\n• 使用<a href="penalty-calculator.html" style="color:#60a5fa">自由裁量计算器</a>精确计算\n• 连续超标3天以上建议立案\n• COD>300mg/L（超标3倍）涉嫌犯罪，移送公安'},
  {role:'执法', k:['执法流程','办案流程','案件办理'], a:'📋 执法全流程8步：\n线索发现→立案审批→现场检查→证据固定→案件审查→处罚决定→执行监督→结案归档\n\n详见<a href="enforcement-guide.html" style="color:#60a5fa">执法流程引导</a>，含证据清单和AI建议。'},
  {role:'执法', k:['涉刑','犯罪','移送公安','刑事'], a:'⚠️ 涉刑移送情形：\n• 饮用水源保护区排放有毒物质\n• 重金属超标3倍以上\n• 暗管/渗井/渗坑偷排\n• 篡改伪造监测数据\n\n依据《刑法》第338条，移送公安机关。使用<a href="penalty-calculator.html" style="color:#60a5fa">裁量计算器</a>会自动预警涉刑风险。'},
  {role:'执法', k:['文书','笔录','处罚决定书'], a:'📄 <a href="doc-generator.html" style="color:#60a5fa">执法文书AI生成</a>支持4种：\n• 现场检查笔录\n• 询问笔录\n• 行政处罚决定书\n• 责令改正通知书\n\n输入案件要素，AI自动生成标准格式文书。'},
  {role:'执法', k:['取证','证据','现场检查'], a:'🧰 <a href="evidence-toolkit.html" style="color:#60a5fa">取证工具箱</a>提供8种工具：\n拍照取证/录音记录/采样登记/GPS定位/测距/便携检测/文书生成/裁量计算\n\n含10条证据采集清单和12项执法检查清单。'},
  {role:'执法', k:['案例分析','案情分析','违法分析'], a:'🧠 <a href="case-analysis.html" style="color:#60a5fa">案例智能分析</a>：\n输入案情描述，AI自动输出7项分析：\n违法行为识别→法条匹配→证据评估→处罚建议→涉刑预警→相似案例→执法建议'},
  {role:'执法', k:['企业风险','风险评估','执法重点'], a:'🎯 <a href="risk-profile.html" style="color:#60a5fa">企业风险画像</a>：\n5维度评估8家企业（合规/监测/历史/整改/应急）\n高风险3家→优先执法\n中风险2家→加强巡查\n低风险5家→减少检查频次'},

  // === 监管角色 ===
  {role:'监管', k:['在线监测','非现场','远程执法'], a:'👁️ <a href="remote-enforcement.html" style="color:#60a5fa">非现场执法</a>：\n• 12家企业实时监控状态\n• 6条预警列表（超标/异常/离线/已处理）\n• AI分析结论+分级执法建议\n• P0优先级24h内现场核查'},
  {role:'监管', k:['预警','告警','异常'], a:'🚨 <a href="smart-alert.html" style="color:#60a5fa">智能预警系统</a>：\n• 6条规则引擎（超标/异常/用电/空间/趋势/遥感）\n• 45条预警（7紧急+15一般+23提示）\n• 平均响应12.5分钟\n• 处置率96%'},
  {role:'监管', k:['督察','督察整改','反馈问题'], a:'🔍 <a href="inspection.html" style="color:#60a5fa">督察整改</a>：\n• 20条问题台账（3紧急+5整改中+12已销号）\n• 分领域进度（水75%/气83%/固废50%）\n• 整改动态时间线\n• 80%完成率'},

  // === 政府角色 ===
  {role:'政府', k:['数据','统计','排放量','年报'], a:'📊 数据分析工具：\n• <a href="data-cockpit.html" style="color:#60a5fa">数据驾驶舱</a>：8项KPI+趋势+排行+AI建议\n• <a href="eco-statistics.html" style="color:#60a5fa">生态统计</a>：排污系数+排放量核算+年度数据\n• <a href="ai-report.html" style="color:#60a5fa">AI周报月报</a>：自动汇总+智能分析'},
  {role:'政府', k:['应急','突发事件','应急指挥'], a:'🆘 <a href="emergency-center.html" style="color:#60a5fa">应急指挥中心</a>：\n• 当前事件：华源化工废水泄漏（Ⅱ级）\n• 7步处置时间线\n• 8人应急队伍\n• 8类资源调度\n• 5条通讯记录'},
  {role:'政府', k:['地图','一张图','分布','热力图'], a:'🗺️ <a href="env-map.html" style="color:#60a5fa">环境一张图</a>：\n• GIS风险热力图（10企业点位）\n• 6个区域统计\n• 企业风险排行\n• 12个监测站点'},
  {role:'政府', k:['无人机','航拍','巡查'], a:'🚁 <a href="drone-patrol.html" style="color:#60a5fa">无人机巡查</a>：\n• 3架无人机实时状态\n• 6个巡查任务（含夜间热成像）\n• AI识别（可见光+热成像）\n• 本周12架次，发现5个问题'},
  {role:'政府', k:['能力评估','执法队伍','人员考核'], a:'👥 <a href="capacity-assess.html" style="color:#60a5fa">执法能力评估</a>：\n• 团队5维度评分（均分82.5）\n• 4人能力画像\n• 薄弱环节：法规掌握（72分）\n• 本月培训计划+个人发展建议'},
];

// 角色快捷问题
var ROLE_QUESTIONS = {
  '公众': ['如何举报？','空气质量怎么看？','噪声扰民怎么办？','怎么参加志愿活动？'],
  '企业': ['排污许可证怎么办？','危废怎么管理？','环保信用怎么评？','有环保设备推荐吗？','能申请环保贷款吗？'],
  '执法': ['COD超标怎么处罚？','执法流程是什么？','生成执法文书','涉刑移送标准'],
  '监管': ['在线监测预警','智能预警系统','督察整改进度'],
  '政府': ['数据驾驶舱','应急指挥中心','无人机巡查','执法队伍评估'],
};

var DEFAULT_ANSWER = '我是环保智慧执法AI助手 🤖\n\n我可以帮您：\n• 📢 公众：举报/科普/志愿活动\n• 🏭 企业：许可/台账/信用/设备/金融\n• 🚔 执法：流程/文书/裁量/取证/分析\n• 👁️ 监管：预警/非现场/督察\n• 🏛️ 政府：数据/应急/地图/无人机\n\n请直接输入问题，或选择您的角色获取专属问题。';

// 创建UI
var fab = document.createElement('div');
fab.id = 'ai-fab';
fab.innerHTML = '🤖';
fab.style.cssText = [
  'position:fixed','bottom:70px','right:72px','width:52px','height:52px',
  'border-radius:50%','background:linear-gradient(135deg,#10b981,#34d399)',
  'color:#fff','font-size:22px','display:flex','align-items:center','justify-content:center',
  'cursor:pointer','z-index:99999','box-shadow:0 4px 12px rgba(16,185,129,.4)',
  'transition:all .3s','user-select:none','-webkit-tap-highlight-color:transparent'
].join(';');

var chat = document.createElement('div');
chat.id = 'ai-chat';
chat.style.cssText = [
  'position:fixed','bottom:130px','right:16px','width:340px','max-width:calc(100vw - 32px)',
  'height:500px','max-height:calc(100vh - 160px)',
  'background:#0a0e1a','border:1px solid #1e293b','border-radius:16px',
  'z-index:99999','display:none','flex-direction:column',
  'box-shadow:0 8px 32px rgba(0,0,0,.4)','overflow:hidden',
  'font-family:-apple-system,BlinkMacSystemFont,sans-serif'
].join(';');

chat.innerHTML = `
  <div style="padding:12px 16px;background:#111827;border-bottom:1px solid #1e293b;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:14px;font-weight:600;color:#60a5fa">🤖 AI助手</div>
      <div style="font-size:10px;color:#64748b">五角色智能问答 · 环保智慧执法</div>
    </div>
    <span id="ai-close" style="cursor:pointer;font-size:18px;color:#64748b">✕</span>
  </div>
  <div style="padding:8px 12px;background:#0d1117;border-bottom:1px solid #1e293b;display:flex;gap:4px;flex-wrap:wrap">
    <button class="ai-role active" data-role="公众" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">📢 公众</button>
    <button class="ai-role" data-role="企业" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">🏭 企业</button>
    <button class="ai-role" data-role="执法" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">🚔 执法</button>
    <button class="ai-role" data-role="监管" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">👁️ 监管</button>
    <button class="ai-role" data-role="政府" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">🏛️ 政府</button>
  </div>
  <div id="ai-messages" style="flex:1;overflow-y:auto;padding:12px;scroll-behavior:smooth">
    <div style="background:#1a2332;border-radius:12px 12px 12px 4px;padding:10px 12px;margin-bottom:8px;margin-right:40px;font-size:13px;color:#e2e8f0;line-height:1.6">
      您好！我是环保AI助手 🤖<br><br>请选择您的角色（上方按钮），我会推荐专属问题。<br>也可以直接输入任何环保相关问题。
    </div>
  </div>
  <div id="ai-quick-area" style="padding:6px 12px;display:flex;gap:6px;flex-wrap:wrap;border-top:1px solid #1e293b;background:#0d1117">
  </div>
  <div style="padding:10px 12px;background:#111827;border-top:1px solid #1e293b">
    <div style="display:flex;gap:8px">
      <input id="ai-input" type="text" placeholder="输入问题，Enter发送..." style="flex:1;padding:10px 12px;background:#1a2332;border:1px solid #1e293b;border-radius:8px;color:#e2e8f0;font-size:13px;outline:none">
      <button id="ai-send" style="padding:10px 14px;border:none;border-radius:8px;background:#3b82f6;color:#fff;font-size:13px;font-weight:600;cursor:pointer">发送</button>
    </div>
  </div>
`;

document.body.appendChild(fab);
document.body.appendChild(chat);

var currentRole = '公众';

// 显示/隐藏
var isOpen = false;
fab.addEventListener('click', function(){
  isOpen = !isOpen;
  chat.style.display = isOpen ? 'flex' : 'none';
  fab.style.transform = isOpen ? 'scale(1.1)' : 'scale(1)';
  if(isOpen){
    renderQuickQuestions();
    setTimeout(function(){ document.getElementById('ai-input').focus(); }, 100);
  }
});

document.getElementById('ai-close').addEventListener('click', function(){
  isOpen = false;
  chat.style.display = 'none';
  fab.style.transform = 'scale(1)';
});

// 角色切换
document.querySelectorAll('.ai-role').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.querySelectorAll('.ai-role').forEach(function(b){
      b.classList.remove('active');
      b.style.background = '#1a2332';
      b.style.color = '#93c5fd';
    });
    btn.classList.add('active');
    btn.style.background = '#3b82f6';
    btn.style.color = '#fff';
    currentRole = btn.getAttribute('data-role');
    renderQuickQuestions();
    addMessage('已切换为【' + currentRole + '】角色，以下是推荐问题：', false);
  });
});

// 快捷问题
function renderQuickQuestions(){
  var area = document.getElementById('ai-quick-area');
  var qs = ROLE_QUESTIONS[currentRole] || [];
  area.innerHTML = qs.map(function(q){
    return '<button class="ai-quick" data-q="' + q + '" style="padding:4px 10px;border-radius:12px;background:#1a2332;border:1px solid #1e293b;color:#93c5fd;font-size:11px;cursor:pointer">' + q + '</button>';
  }).join('');
  
  area.querySelectorAll('.ai-quick').forEach(function(btn){
    btn.addEventListener('click', function(){
      var q = btn.getAttribute('data-q');
      sendQuestion(q);
    });
  });
}

// 发送
document.getElementById('ai-send').addEventListener('click', function(){
  var input = document.getElementById('ai-input');
  var q = input.value.trim();
  if(q){ sendQuestion(q); input.value = ''; }
});

document.getElementById('ai-input').addEventListener('keydown', function(e){
  if(e.key === 'Enter'){
    var q = this.value.trim();
    if(q){ sendQuestion(q); this.value = ''; }
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

  // 检查规则（优先匹配当前角色）
  var roleMatch = [];
  var otherMatch = [];
  for(var i=0; i<QA_RULES.length; i++){
    var rule = QA_RULES[i];
    for(var j=0; j<rule.k.length; j++){
      if(q.indexOf(rule.k[j]) >= 0){
        if(rule.role === currentRole){
          roleMatch.push(rule);
        } else {
          otherMatch.push(rule);
        }
        break;
      }
    }
  }

  if(roleMatch.length > 0) return roleMatch[0].a;
  if(otherMatch.length > 0) return otherMatch[0].a;

  // 页面导航
  var navMap = {
    '商城':'equipment-mall.html','设备':'equipment-mall.html','法规':'law-library.html','法律':'law-library.html',
    '驾驶舱':'data-cockpit.html','预警':'smart-alert.html','地图':'env-map.html','无人机':'drone-patrol.html',
    '应急':'emergency-center.html','信用':'credit-rating.html','风险':'risk-profile.html',
    '裁量':'penalty-calculator.html','文书':'doc-generator.html','科普':'eco-science.html',
    '台账':'env-ledger.html','审批':'approval-service.html','碳':'carbon-mgmt.html',
    '金融':'green-finance.html','管家':'eco-manager.html','互动':'public-interact.html',
    '举报':'m-report.html','流程':'enforcement-guide.html','取证':'evidence-toolkit.html',
    '培训':'training.html','图谱':'knowledge-graph.html','统计':'eco-statistics.html',
    '督察':'inspection.html','总览':'overview.html','门户':'m-portal.html',
    '控制台':'sys-console.html','分析':'case-analysis.html','非现场':'remote-enforcement.html',
  };
  for(var key in navMap){
    if(q.indexOf(key) >= 0){
      return '正在为您打开' + key + '页面 → <a href="' + navMap[key] + '" style="color:#60a5fa;font-weight:600">点击进入</a>';
    }
  }

  return DEFAULT_ANSWER;
}

function sendQuestion(q){
  addMessage(q, true);
  setTimeout(function(){
    var answer = getAnswer(q);
    addMessage(answer, false);
  }, 300);
}

// 首次提示
if(!sessionStorage.getItem('ai_welcomed')){
  sessionStorage.setItem('ai_welcomed', '1');
  setTimeout(function(){
    fab.style.animation = 'bounce 0.5s ease 2';
    setTimeout(function(){ fab.style.animation = ''; }, 2000);
  }, 3000);
}

var style = document.createElement('style');
style.textContent = '@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}';
document.head.appendChild(style);

})();
