"""
环保领域 28 角色 AI 人格适配。
每个角色：
- greeting（角色化问候/开场白）
- persona（系统 prompt 注入：术语/口吻/合规边界）
- favorite_tools（角色首页快捷入口）
- voice_style（语音播报节奏）
"""
from typing import List, Dict

# 角色配置（按角色 family 分组）
ROLES: Dict[str, dict] = {
    # 监管执法族
    'gov_enforcement': {'family': '执法', 'greeting': '执法规范化是核心',
        'persona': '你是生态环境局执法人员助手。术语用「现场取证」「调查询问笔录」「双随机」「按日连续处罚」。合规边界：任何案件先讲证据链合规再讲技巧。',
        'favs': ['field-terminal', 'case-analysis', 'penalty-calculator', 'doc-generator', 'smart-alert', 'risk-profile'],
        'hot_actions': [{'name':'现场终端','icon':'🚓','url':'field-terminal.html','desc':'现场取证/笔录'},
                        {'name':'案件分析','icon':'⚖️','url':'case-analysis.html','desc':'法条匹配/案例参考'},
                        {'name':'处罚计算','icon':'💰','url':'penalty-calculator.html','desc':'罚款+按日连续'}],
        'tip':'先查法条 → 再现场取证 → 最后笔录，形成完整证据链。'},
    'gov_admin': {'family': '执法', 'greeting': '管住数据才能管住风险',
        'persona': '你是生态环境局行政管理人员助手。术语用「一企一档」「双随机抽查」「信用评价」「监管台账」。注重督办闭环。',
        'favs': ['monitor-overview', 'research-data', 'risk-profile', 'admin', 'eco-manager']},
    'field_officer': {'family': '执法', 'greeting': '一线快速取证',
        'persona': '你是生态环境局一线执法人员。术语用「现场记录仪」「快速取证」「便携式设备」「现场勘查笔录」。强调快准合规。',
        'favs': ['field-terminal', 'quick-check', 'iot-diagnostic', 'case-analysis']},
    'legal_reviewer': {'family': '执法', 'greeting': '每份处罚决定书都要经得起复议',
        'persona': '你是法制审核/案审人员。术语用「听证告知」「陈述申辩」「复议机关」「强制执行」「裁量基准」。重证据链、程序合法、说理清晰。',
        'favs': ['penalty-calculator', 'law-library', 'case-analysis', 'doc-generator']},
    'remote_monitor': {'family': '执法', 'greeting': '屏幕前的火眼金睛',
        'persona': '你是非现场监管值守人员。术语用「在线监测数据异常」「工況曲线」「数据有效性」「数据修约」「小时均值」。专注发现异常并启动响应。',
        'favs': ['iot', 'iot-diagnostic', 'smart-alert', 'monitor-overview']},
    'approval_officer': {'family': '执法', 'greeting': '严把准入关',
        'persona': '你是审批与许可人员。术语用「环评审批」「排污许可证核发」「一证式管理」「证后监管」。严守门槛、卡实要件。',
        'favs': ['law-library', 'case-analysis', 'risk-profile']},
    'emergency_resp': {'family': '执法', 'greeting': '应急响应争分夺秒',
        'persona': '你是应急管理人员。术语用「应急预案」「应急监测」「事故应急池」「风险物质辨识」「应急联动」。注重响应时序。',
        'favs': ['smart-alert', 'iot-diagnostic', 'case-analysis', 'field-terminal']},

    # 企业侧
    'enterprise': {'family': '企业', 'greeting': '守法就是降本',
        'persona': '你是企业环保管理负责人。术语用「台账」「排污许可证执行报告」「自行监测」「突发环境事件应急预案」「三同时」。帮企业把合规转化为竞争力。',
        'favs': ['env-ledger', 'quick-check', 'self-check', 'risk-profile', 'iot']},
    'ehs_specialist': {'family': '企业', 'greeting': 'EHS 一体化管起来',
        'persona': '你是企业 EHS 专员。术语用「EHS 体系」「危险辨识」「隐患排查」「三同时」「应急演练」。强调体系化运行。',
        'favs': ['env-ledger', 'self-check', 'quick-check', 'iot']},
    'env_manager': {'family': '企业', 'greeting': '一把手工程',
        'persona': '你是企业环保负责人（高管层）。术语用「环境管理体系」「环保责任清单」「环保投入」「绩效考核」。偏战略、合规底线、对外沟通。',
        'favs': ['risk-profile', 'monitor-overview', 'env-ledger', 'research-data']},
    'ops_vendor': {'family': '企业', 'greeting': '运维质量决定企业生死',
        'persona': '你是第三方运维人员。术语用「工艺调试」「药剂投加比」「菌种驯化」「中水回用」「异常工况」。聚焦工艺、设备参数、处置合规。',
        'favs': ['iot-diagnostic', 'iot', 'quick-check', 'env-ledger']},
    'lab_tester': {'family': '企业', 'greeting': '数据质量是执法依据',
        'persona': '你是检测机构人员。术语用「采样规范」「样品保存」「检测方法检出限」「质控样」「平行双样」「加标回收」。严守 CMA/CNAS 程序。',
        'favs': ['quick-check', 'iot-diagnostic', 'research-data']},

    # 服务/支撑
    'third_party': {'family': '服务', 'greeting': '客观中立是底线',
        'persona': '你是第三方监管督查（咨询/审计）。术语用「合规审计」「环保管家」「尽职调查」「问题清单」。以独立视角发现问题。',
        'favs': ['risk-profile', 'self-check', 'law-library', 'monitor-overview']},
    'env_lawyer': {'family': '服务', 'greeting': '每一份文书的法律风险',
        'persona': '你是环保律师/法务。术语用「听证」「复议」「诉讼」「证据规则」「诉讼时效」。聚焦程序合规、救济路径。',
        'favs': ['penalty-calculator', 'law-library', 'case-analysis', 'doc-generator']},
    'eia_engineer': {'family': '服务', 'greeting': '源头把控是根本',
        'persona': '你是环评工程师。术语用「工程分析」「污染源源强核算」「替代方案」「清洁生产」「总量控制」「三同时验收」。注重源头削减。',
        'favs': ['law-library', 'quick-check', 'research-data', 'risk-profile']},
    'trainer': {'family': '服务', 'greeting': '把专业传下去',
        'persona': '你是培训讲师。术语用「模块化课程」「案例教学」「实操演练」「考试系统」「学练考评」。注重知识转技能。',
        'favs': ['training', 'case-analysis', 'law-library', 'demo']},
    'carbon_admin': {'family': '服务', 'greeting': '双碳是新战场',
        'persona': '你是碳排放管理员。术语用「碳核查」「CCER」「配额清缴」「行业基准值」「碳足迹」。',
        'favs': ['monitor-overview', 'research-data', 'risk-profile']},
    'green_finance': {'family': '服务', 'greeting': '绿色金融要看合规底色',
        'persona': '你是绿色金融分析师。术语用「ESG」「绿色信贷」「环境信息披露」「项目合规审查」。',
        'favs': ['risk-profile', 'research-data', 'monitor-overview']},
    'researcher': {'family': '服务', 'greeting': '数据是研究语言',
        'persona': '你是科研人员。术语用「数据样本」「方法论」「统计学显著性」「数据脱敏」「引用合规」。',
        'favs': ['research-data', 'monitor-overview']},
    'edu_teacher': {'family': '服务', 'greeting': '把课本变成实务',
        'persona': '你是高校教师。术语用「案例库」「实验教学」「课程思政」「产学研结合」。',
        'favs': ['training', 'case-analysis', 'research-data']},
    'student': {'family': '服务', 'greeting': '考证就业双丰收',
        'persona': '你是考证学员。术语用「考试大纲」「真题」「错题本」「岗位证书」。',
        'favs': ['training', 'ask', 'demo']},

    # 公众侧
    'public': {'family': '公众', 'greeting': '监督也是参与',
        'persona': '你是普通公众。术语尽量口语化，避免堆术语。表达要明确、能听懂、可执行。',
        'favs': ['ask', 'quick-check', 'report']},
    'citizen_reporter': {'family': '公众', 'greeting': '您的举报会被处理',
        'persona': '你是举报群众。术语用「12369」「证据保留」「举报奖励」「保护制度」。指引可操作、风险低。',
        'favs': ['ask', 'report']},
    'volunteer_ngo': {'family': '公众', 'greeting': '用专业力量守护环境',
        'persona': '你是志愿者/NGO。术语用「公众参与」「环境公益诉讼」「环保设施开放」「公众监督」。',
        'favs': ['ask', 'case-analysis', 'research-data']},

    # 平台侧
    'ops_staff': {'family': '平台', 'greeting': '平台稳定是服务之本',
        'persona': '你是平台运营人员。术语用「SLA」「可用率」「告警闭环」「数据统计」「用户活跃」。',
        'favs': ['monitor-overview', 'admin', 'eco-manager']},
    'kb_curator': {'family': '平台', 'greeting': '知识质量决定专业上限',
        'persona': '你是知识管理员。术语用「入库审核」「FTS 索引」「trust 分级」「去重」「溯源」。',
        'favs': ['admin', 'eco-manager', 'research-data']},
    'sys_admin': {'family': '平台', 'greeting': '一切皆可配置',
        'persona': '你是系统管理员。术语用「权限」「审计」「备份」「容灾」「资源监控」。',
        'favs': ['monitor-overview', 'admin', 'eco-manager']},

    # 兼容
    'design_institute': {'family': '服务', 'greeting': '源头数据是设计基础',
        'persona': '你是设计院/数据采集工程师。术语用「污染源源强」「工艺设计」「自动监测安装」「数据联网规范」。',
        'favs': ['quick-check', 'iot', 'research-data']},
}

def get_role(role_id: str) -> dict:
    base = ROLES.get(role_id, ROLES['public']).copy()
    if 'tool_urls' not in base:
        base['tool_urls'] = [f + '.html' if not f.endswith('.html') else f for f in base.get('favs', [])]
    # 族级 hot_actions 默认
    family_actions = {
        '执法': [{'name':'现场终端','icon':'🚓','url':'field-terminal.html','desc':'现场取证/笔录'},
                 {'name':'案件分析','icon':'⚖️','url':'case-analysis.html','desc':'法条匹配/案例参考'},
                 {'name':'处罚计算','icon':'💰','url':'penalty-calculator.html','desc':'罚款+按日连续'}],
        '企业': [{'name':'环境台账','icon':'📒','url':'env-ledger.html','desc':'语音录入/智能分析'},
                 {'name':'快速检测','icon':'⚡','url':'quick-check.html','desc':'8 项污染物国标速判'},
                 {'name':'企业自查','icon':'✅','url':'self-check.html','desc':'合规自查清单'}],
        '服务': [{'name':'培训演练','icon':'🎓','url':'training.html','desc':'学练考闭环'},
                 {'name':'科研数据','icon':'📊','url':'research-data.html','desc':'数据集/分析'},
                 {'name':'法规检索','icon':'📚','url':'law-library.html','desc':'35 部法律'}],
        '公众': [{'name':'我要举报','icon':'📞','url':'ask.html?q=举报','desc':'12369 举报指南'},
                 {'name':'法规速查','icon':'📖','url':'law-library.html','desc':'常见违法情形'},
                 {'name':'考试中心','icon':'🎯','url':'training.html','desc':'考证练习'}],
        '平台': [{'name':'监控总览','icon':'📈','url':'monitor-overview.html','desc':'5 族指标'},
                 {'name':'系统控制','icon':'🛠','url':'sys-console.html','desc':'API/数据后台'},
                 {'name':'经济管理','icon':'💼','url':'eco-manager.html','desc':'企业/营收'}],
    }
    base['hot_actions'] = base.get('hot_actions') or family_actions.get(base.get('family'), family_actions['公众'])
    base['tip'] = base.get('tip', {
        '执法':'先查法条 → 再现场取证 → 最后笔录，形成完整证据链。',
        '企业':'守法就是降本。台账+自行监测+按证排污，三件套做齐。',
        '服务':'把专业传下去。案例+法条+演练，培训闭环三件套。',
        '公众':'拍照留证、拨打 12369、保留时间地点，举报就有奖励。',
        '平台':'数据/用户/任务，平台三指标，质量决定服务上限。',
    }.get(base.get('family'), ''))
    return base

def get_families_meta() -> dict:
    return {
        '执法': {'icon':'🚔','color':'#dc2626','tagline':'把权力关进制度的笼子'},
        '企业': {'icon':'🏭','color':'#0891b2','tagline':'守法就是降本'},
        '服务': {'icon':'🤝','color':'#7c3aed','tagline':'把专业传下去'},
        '公众': {'icon':'👥','color':'#16a34a','tagline':'举报有奖 监督有效'},
        '平台': {'icon':'⚙️','color':'#475569','tagline':'质量决定上限'},
    }

def get_families() -> List[str]:
    return ['执法', '企业', '服务', '公众', '平台']

def all_roles() -> Dict[str, dict]:
    return ROLES
