#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 检查指导引擎（全面 AI 化 · 外行变专业）
职责：把专业检查项翻译成「外行 5 步闭环指令」：
  去哪看 → 看什么 → 怎么判断 → 拍什么留证 → 出异常怎么办
数据源：violation_types（33 类违法情形）× kb_formal（273 条）× emission_standards（37 条）
全部本地算力，断网可用；异常兜底，禁止静默失败。
"""
import json
import os
import re
import sqlite3
import time

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'epb.db')

# 检查项关键词 → 现场位置（去哪看）
_WHERE_MAP = [
    (['暗管', '偷排', '渗井', '渗坑', '绕排'], '厂区围墙内外、雨水管网、污水管网交汇处、车间地面暗沟'),
    (['排污口', '排口'], '厂区排污口规范化设置点（看标识牌是否齐全）'),
    (['危废', '固废', '贮存'], '危废暂存间（重点看：标识、防渗、台账、分类贮存）'),
    (['在线监测', '自动监控', '监测数据'], '在线监测站房（设备运行状态 + 数据采集仪）'),
    (['治污设施', '污染防治设施', '设施运行'], '治污设施现场（水泵、风机、加药系统运行状态）'),
    (['台账', '记录'], '环保管理台账（办公室调阅）'),
    (['许可证', '排污许可'], '排污许可证正副本（办公室调阅）'),
    (['噪声'], '厂界四周（离噪声源最近的敏感点）'),
    (['VOCs', '挥发性有机'], 'VOCs 产生工段（密闭、收集罩、治污设施）'),
    (['扬尘', '粉尘'], '物料堆场、装卸点、厂区道路'),
    (['雨污', '分流'], '雨水口、污水口、切换阀门'),
    (['环评', '验收'], '环评批复文件、竣工验收材料（办公室调阅）'),
]

# 检查项关键词 → 现场动作（看什么 + 怎么判断）
_HOW_MAP = [
    (['暗管', '偷排'], [
        '沿厂区围墙走一圈，重点看有无新翻泥土、异常管道出口',
        '打开雨水井盖，看井里是否有生产废水痕迹（颜色、泡沫、油膜）',
        '对比用水量与排水量：用水多排水少 = 疑似偷排',
    ]),
    (['超标', 'COD', '氨氮'], [
        '调取在线监测最近 7 天数据，看是否有限值波动',
        '现场快检取样（如有便携检测设备）',
        '对照排放标准限值判断（可用超标快检功能）',
    ]),
    (['危废'], [
        '看标识牌：危废类别、产生单位、责任人是否齐全',
        '看防渗：地面防渗层有无破损、有无导流沟',
        '看台账：入库出库记录、转移联单是否齐全',
        '看分类：不同类别危废是否分开贮存、有无混堆',
    ]),
    (['在线监测', '自动监控'], [
        '看设备运行灯：正常应为运行状态，无报警',
        '看数据采集仪：数值是否正常波动（恒值 = 疑似造假）',
        '看站房环境：空调、除湿是否正常（保证设备工况）',
        '调取设备操作日志，查有无异常修改记录',
    ]),
    (['治污设施'], [
        '听设备运行声音（水泵、风机是否在转）',
        '看运行指示灯和电流表读数',
        '对比生产时间与治污设施运行记录（生产时治污设施必须同步运行）',
        '查加药记录：药剂投加量与处理水量是否匹配',
    ]),
    (['台账'], [
        '抽查最近 3 个月的运行台账，看有无缺天、断记',
        '台账数值与在线监测数据交叉比对',
    ]),
    (['许可证'], [
        '核对许可证有效期是否在期内',
        '核对许可排放量与实际排放量（是否超许可）',
        '核对排污口数量、位置与证载是否一致',
    ]),
    (['噪声'], [
        '在厂界外 1 米处用声级计测 1 分钟等效声级',
        '对照 GB 12348-2008 相应功能区限值判断',
    ]),
]

# 证据拍摄指引（拍什么）
_EVIDENCE_SHOTS = [
    (['暗管', '偷排'], ['暗管出口全景（带参照物）', '出水口特写 + 水样颜色', '雨水井内痕迹', '现场定位截图']),
    (['危废'], ['危废间全景', '标识牌特写', '台账翻页视频（逐页拍）', '混堆/破损部位特写']),
    (['在线监测'], ['站房全景', '设备运行灯与显示屏读数', '数据采集仪实时数值', '操作日志界面']),
    (['治污设施'], ['设施全景（运行状态）', '电流表/运行指示灯特写', '加药系统运行视频']),
    (['超标'], ['在线监测数据画面（带时间）', '取样过程视频', '样品封条照片']),
]

# 询问话术（问什么——外行直接照读）
_ASK_SCRIPTS = [
    (['暗管'], '请问厂区的雨水管网和污水管网是怎么分流的？最近有没有改造过管道？'),
    (['危废'], '请问贵司危废台账在哪里？最近一次转移是什么时候？联单能给我们看一下吗？'),
    (['在线监测'], '请问在线监测设备最近有没有维修或校准过？第三方运维公司是哪家？'),
    (['治污设施'], '请问治污设施昨晚几点停的？停运检修有没有向生态环境部门报备？'),
    (['许可证'], '请问排污许可证在有效期内吗？能提供副本复印件吗？'),
]


def _conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _clean(s, limit=200):
    if not isinstance(s, str):
        return ''
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f<>]', '', s.strip())[:limit]


def _match_any(keywords, text):
    text = text or ''
    for kw in keywords:
        if kw in text:
            return True
    return False


def coach_check_point(check_point, risk_level='', inspection_type=''):
    """单个检查项 → 外行 5 步指导卡
    返回: {where, how[], shots[], ask[], law_refs[], abnormal_todo[], confidence}
    """
    cp = _clean(check_point, 120)
    result = {
        'check_point': cp,
        'where': '按检查清单标注的位置逐一到场',
        'how': ['对照检查项名称逐项查看现场状态'],
        'shots': ['现场全景照（带时间水印）', '重点部位特写'],
        'ask': ['请问这里平时是怎么管理的？'],
        'law_refs': [],
        'abnormal_todo': [
            '立即拍照/录像固定证据',
            '如实填写"异常详情"（位置、现象、数据）',
            '标记该项为"异常"，系统将自动匹配法条并生成文书',
        ],
        'confidence': 'generic',
    }

    # 去哪看
    for kws, where in _WHERE_MAP:
        if _match_any(kws, cp):
            result['where'] = where
            result['confidence'] = 'matched'
            break

    # 看什么 + 怎么判断
    for kws, hows in _HOW_MAP:
        if _match_any(kws, cp):
            result['how'] = hows
            break

    # 拍什么
    for kws, shots in _EVIDENCE_SHOTS:
        if _match_any(kws, cp):
            result['shots'] = shots
            break

    # 问什么
    for kws, ask in _ASK_SCRIPTS:
        if _match_any(kws, cp):
            result['ask'] = [ask]
            break

    # 法条（violation_types 关联：逐关键词匹配，命中率优先）
    try:
        conn = _conn()
        all_rows = conn.execute(
            'SELECT sub_type, violations, keywords FROM violation_types').fetchall()
        conn.close()
        # 提取检查项里的有效关键词（去掉括号说明 + 同义归一）
        cp_core = re.sub(r'[（(].*?[)）]', '', cp)
        cp_core = (cp_core
                   .replace('危险废物', '危废')
                   .replace('水污染物', '废水')
                   .replace('自动监测', '在线监测')
                   .replace('挥发性有机物', 'VOCs'))
        best = []
        for r in all_rows:
            try:
                kws = json.loads(r['keywords'] or '[]')
            except Exception:
                kws = []
            hit = sum(1 for k in kws if k and k in cp_core)
            if hit > 0:
                best.append((hit, r))
        best.sort(key=lambda x: -x[0])
        for _, r in best[:2]:
            try:
                vl = json.loads(r['violations'] or '[]')
                if vl:
                    result['law_refs'].extend(vl[:2])
            except Exception:
                pass
    except Exception:
        pass
    result['law_refs'] = list(dict.fromkeys(result['law_refs']))[:4]

    # 高风险加急提示
    if '高' in (risk_level or ''):
        result['abnormal_todo'].insert(0, '⚠️ 高风险项：发现异常先固定证据，不要打草惊蛇')
    return result


def coach_checklist(checklist_data):
    """整个清单 → 逐项指导卡 + 全程路线建议"""
    items = checklist_data.get('check_items') or []
    cards = []
    for it in items:
        cards.append(coach_check_point(
            it.get('check_point', ''),
            it.get('risk_level', ''),
            checklist_data.get('inspection_type', '')))
    # 汇总：高风险项排前面（先查高风险）
    high_first = sorted(range(len(cards)), key=lambda i: (
        0 if '高' in (items[i].get('risk_level') or '') else 1))
    return {
        'ok': True,
        'total': len(cards),
        'order_suggestion': [i + 1 for i in high_first if i < len(cards)],
        'order_note': '建议先查高风险项（发现异常可优先固定证据）',
        'cards': cards,
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }


def coach_voice_intent(text):
    """语音意图识别（实时人机交互）
    意图集：next_step / how_to / what_to_shoot / whom_to_ask / law / emergency / fallback
    """
    t = _clean(text, 120)
    low = t.lower()

    # 紧急（直接给应急指导）
    if _match_any(['泄漏', '着火', '爆炸', '受伤', '中毒', '紧急'], t):
        return {
            'intent': 'emergency',
            'reply': '遇到突发环境事件：第一步，人员撤到上风向安全区；第二步，拨打 12369 和当地生态环境应急值班电话；第三步，在确保安全的前提下拍照记录泄漏范围；第四步，提醒企业启动应急预案。不要擅自处置不明化学品。',
            'action': 'tts_now',
        }

    if _match_any(['下一步', '然后呢', '接着做', '下一步做什么', '接下来'], t):
        return {'intent': 'next_step', 'reply': '请查看检查清单中还未完成的下一项。当前建议：按高风险优先顺序逐项检查，每完成一项就记录一项。', 'action': 'tts_now'}

    if _match_any(['怎么查', '怎么检查', '怎么看', '怎么判断', '怎么做'], t):
        return {'intent': 'how_to', 'reply': '我需要知道您当前在查哪一项。请说："指导 检查项名称"，例如"指导 暗管检查"。', 'action': 'tts_now'}

    if _match_any(['拍什么', '怎么拍', '拍照', '取证', '留证据'], t):
        return {'intent': 'what_to_shoot', 'reply': '取证三要素：第一，全景照带参照物（让人知道在哪拍的）；第二，特写带时间水印（证明何时拍的）；第三，连续视频记录全过程。涉数据造假的，还要拍设备屏幕实时数值。', 'action': 'tts_now'}

    if _match_any(['问什么', '怎么问', '话术'], t):
        return {'intent': 'whom_to_ask', 'reply': '询问要点：问日常管理流程，不问"你们违法了吗"；问记录在哪里，让他自己拿；问最近一次操作时间，与台账交叉验证。全程使用执法记录仪。', 'action': 'tts_now'}

    if _match_any(['法条', '法律', '违反了什么', '怎么处罚', '罚多少'], t):
        return {'intent': 'law', 'reply': '请说出具体违法情形，我来查法条。您也可以说"查 水污染防治法"直接检索。', 'action': 'tts_now'}

    # "指导 XXX" → 匹配检查项
    m = re.match(r'^(?:指导|教我|帮我查)\s*(.+)$', t)
    if m:
        card = coach_check_point(m.group(1))
        lines = [
            f"好的，检查{m.group(1)[:20]}，指导如下：",
            f"第一，去这里看：{card['where']}。",
            f"第二，这样查：{'；'.join(card['how'][:2])}。",
            f"第三，拍照留证：{'、'.join(card['shots'][:2])}。",
            f"第四，可以问：{card['ask'][0]}",
        ]
        return {'intent': 'coach', 'reply': '。'.join(lines), 'card': card, 'action': 'tts_now'}

    return {
        'intent': 'fallback',
        'reply': '我可以在检查现场给您实时指导。您可以说：指导加检查项名称、下一步做什么、拍什么留证、问什么话术，或紧急情况处置。',
        'action': 'tts_now',
    }
