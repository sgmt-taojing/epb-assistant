/**
 * EPB 角色体系 v3 — 6 族 22 类环保从业人员
 * 用途：登录注册角色选择、角色路由（登录直达工作台）、页面级权限判断
 * 依据：SUPER_AGENT_UPGRADE_PLAN_v3（2026-08-31）
 */
(function(global){
  'use strict';

  var ROLES = [
    // A 执法族（政府侧）
    { key:'field_officer',    family:'执法族', name:'一线执法人员',     icon:'👮', home:'/field-terminal.html',
      desc:'现场检查、证据采集、文书生成', pages:['field-terminal','penalty-calculator','doc-generator','evidence-toolkit','law-library','training'] },
    { key:'legal_reviewer',   family:'执法族', name:'法制审核/案审',   icon:'⚖️', home:'/penalty-calculator.html',
      desc:'裁量审核、程序合规性校验', pages:['penalty-calculator','case-analysis','law-library','knowledge-graph'] },
    { key:'remote_monitor',   family:'执法族', name:'非现场监管值守', icon:'📡', home:'/supervision.html',
      desc:'在线监测研判、预警处置', pages:['supervision','smart-alert','remote-enforcement','iot','sensor-dashboard'] },
    { key:'approval_officer', family:'执法族', name:'审批与许可',      icon:'📑', home:'/approval-service.html',
      desc:'环评许可要件核对、批复', pages:['approval-service','law-library','knowledge-graph'] },
    { key:'emergency_resp',   family:'执法族', name:'应急管理',        icon:'🚨', home:'/emergency-center.html',
      desc:'突发事件处置、预案检索', pages:['emergency-center','report','iot'] },

    // B 企业族
    { key:'ehs_specialist',   family:'企业族', name:'企业EHS专员',    icon:'🏭', home:'/ehs.html',
      desc:'台账管理、合规自查、执行报告', pages:['ehs','self-check','m-self-check','law-library','training'] },
    { key:'env_manager',      family:'企业族', name:'企业环保负责人', icon:'👔', home:'/risk-profile.html',
      desc:'风险画像、信用评级、整改跟踪', pages:['risk-profile','credit-rating','ai-report','ehs'] },
    { key:'ops_vendor',       family:'企业族', name:'第三方运维',      icon:'🔧', home:'/device-mgmt.html',
      desc:'运维工单、留痕记录', pages:['device-mgmt','iot','iot-diagnostic'] },
    { key:'lab_tester',       family:'企业族', name:'检测机构人员',    icon:'🧪', home:'/knowledge.html',
      desc:'方法标准速查、报告规范性', pages:['knowledge','law-library'] },

    // C 专业服务族
    { key:'env_lawyer',       family:'专业服务族', name:'环保律师/法务', icon:'🧑‍⚖️', home:'/case-analysis.html',
      desc:'案例法条检索、程序审查', pages:['case-analysis','law-library','knowledge-graph','case-analysis'] },
    { key:'eia_engineer',     family:'专业服务族', name:'环评工程师',   icon:'📐', home:'/engineering-plan.html',
      desc:'政策跟踪、编制依据', pages:['engineering-plan','approval-service','law-library'] },
    { key:'trainer',          family:'专业服务族', name:'培训讲师',     icon:'🧑‍🏫', home:'/training.html',
      desc:'课程管理、AI出题、学情看板', pages:['training','knowledge'] },
    { key:'carbon_admin',     family:'专业服务族', name:'碳排放管理员', icon:'🌫️', home:'/carbon-mgmt.html',
      desc:'碳核算、碳资产台账', pages:['carbon-mgmt','energy','eco-statistics'] },
    { key:'green_finance',    family:'专业服务族', name:'绿色金融',     icon:'💚', home:'/green-finance.html',
      desc:'环境风险评分、承保参考', pages:['green-finance','risk-profile','credit-rating'] },

    // D 研究教育族
    { key:'researcher',       family:'研究教育族', name:'科研人员',     icon:'🔬', home:'/research-data.html',
      desc:'脱敏研究数据集申请与下载', pages:['research-data','open-data','knowledge-graph'] },
    { key:'edu_teacher',      family:'研究教育族', name:'高校教师',     icon:'🎓', home:'/research-data.html',
      desc:'教学案例包、课程数据集', pages:['research-data','open-data','training'] },
    { key:'student',          family:'研究教育族', name:'学员/考证',    icon:'📚', home:'/training.html',
      desc:'学练考评、错题辨析', pages:['training','m-portal','knowledge'] },

    // E 公众族
    { key:'citizen_reporter', family:'公众族', name:'举报群众',        icon:'🗣️', home:'/report.html',
      desc:'拍照举报、进度查询', pages:['report','m-report','eco-science'] },
    { key:'volunteer_ngo',    family:'公众族', name:'志愿者/NGO',      icon:'🌿', home:'/open-data.html',
      desc:'公开数据获取、监督工具', pages:['open-data','eco-science','public-interact'] },

    // F 运营族
    { key:'ops_staff',        family:'运营族', name:'平台运营',        icon:'🛠️', home:'/dashboard.html',
      desc:'运营看板、工单处理', pages:['dashboard','ops-monitor','workspace'] },
    { key:'kb_curator',       family:'运营族', name:'知识管理员',      icon:'🗂️', home:'/knowledge.html',
      desc:'知识采集与审核入库', pages:['knowledge','knowledge-graph','law-library'] },
    { key:'sys_admin',        family:'运营族', name:'系统管理员',      icon:'⚙️', home:'/admin.html',
      desc:'权限、租户、审计日志', pages:['admin','sys-console'] }
  ];

  var ROLE_MAP = {};
  ROLES.forEach(function(r){ ROLE_MAP[r.key] = r; });

  // 兼容旧角色值（存量用户平滑迁移）
  var LEGACY = {
    gov_enforcement: 'field_officer',
    enterprise: 'ehs_specialist',
    public: 'citizen_reporter',
    supervisor: 'remote_monitor'
  };

  function normalize(roleKey){
    if(!roleKey) return null;
    if(ROLE_MAP[roleKey]) return roleKey;
    if(LEGACY[roleKey]) return LEGACY[roleKey];
    return null;
  }

  function getRole(roleKey){
    var k = normalize(roleKey);
    return k ? ROLE_MAP[k] : null;
  }

  function roleHome(roleKey){
    var r = getRole(roleKey);
    return r ? r.home : '/index.html';
  }

  function families(){
    var seen = {}, out = [];
    ROLES.forEach(function(r){
      if(!seen[r.family]){ seen[r.family]=true; out.push({family:r.family, count:0}); }
    });
    return out;
  }

  global.EPB_ROLES = {
    list: ROLES,
    map: ROLE_MAP,
    legacy: LEGACY,
    normalize: normalize,
    get: getRole,
    home: roleHome
  };
})(window);
