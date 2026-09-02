#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
入企语音结构化采集引擎（便捷性建设 2026-09-03）
说一段话 → 结构化环保台账记录（无需打字填表）
支持：药剂投加 / 水量 / 监测数据 / 设备启停 / 异常事件 / 危废转移
"""
import re

# 单位归一
_UNIT = {
    '吨': 't', '立方': 'm³', '立方米': 'm³', '公斤': 'kg', '千克': 'kg', '斤': 'kg/2',
    '克': 'g', '毫克': 'mg', '升': 'L', '毫克每升': 'mg/L',
}

def _num(s):
    try:
        v = float(s)
        return v
    except Exception:
        return None

def parse_intake(text):
    """口语 → 结构化台账记录"""
    text = (text or '').strip()
    result = {
        'ok': True,
        'records': [],       # 结构化记录列表
        'warnings': [],
        'raw': text[:200],
    }
    if not text:
        return {'ok': False, 'error': 'text 不能为空'}

    # ── 1. 药剂投加（PAC/PAM/次氯酸钠/片碱/石灰/聚合氯化铝…） ──
    for m in re.finditer(r'(PAC|PAM|次氯酸钠|片碱|液碱|石灰|聚合氯化铝|硫酸亚铁|葡萄糖|碳源|药剂)[^0-9]{0,6}([0-9]+(?:\.[0-9]+)?)\s*(公斤|千克|kg|克|g|吨|升|L)', text):
        chem, val, unit = m.group(1), _num(m.group(2)), m.group(3)
        if val is not None:
            result['records'].append({
                'type': '药剂投加', 'item': chem, 'value': val, 'unit': unit,
                'category': '治污设施运行',
            })

    # ── 2. 水量/处理量 ──
    for m in re.finditer(r'(进水|出水|处理水量|废水量|水量)[^0-9]{0,6}([0-9]+(?:\.[0-9]+)?)\s*(吨|立方|立方米|m³)', text):
        item, val, unit = m.group(1), _num(m.group(2)), m.group(3)
        if val is not None:
            result['records'].append({
                'type': '水量', 'item': item, 'value': val, 'unit': 'm³',
                'category': '治污设施运行',
            })

    # ── 3. 监测数据（COD/氨氮/pH/SS/总磷…） ──
    for m in re.finditer(r'(COD|氨氮|总磷|总氮|SS|pH|悬浮物|BOD)[^0-9]{0,8}([0-9]+(?:\.[0-9]+)?)', text):
        item, val = m.group(1), _num(m.group(2))
        if val is not None:
            result['records'].append({
                'type': '监测数据', 'item': item, 'value': val, 'unit': 'mg/L' if item != 'pH' else '',
                'category': '排放监测',
            })

    # ── 4. 设备启停 ──
    for m in re.finditer(r'(风机|水泵|曝气|压滤机|加药泵|刮泥机|治污设施|设备)[^，。]{0,10}(启动|开机|运行|停机|停止|停运|故障|维修)', text):
        result['records'].append({
            'type': '设备状态', 'item': m.group(1), 'value': m.group(2),
            'unit': '', 'category': '设备运行',
        })

    # ── 5. 异常事件 ──
    for kw in ('超标', '异常', '泄漏', '冒烟', '异味', '报警', '停电', '事故'):
        if kw in text:
            result['records'].append({
                'type': '异常事件', 'item': kw, 'value': True, 'unit': '',
                'category': '异常记录', 'note': text[:60],
            })
            break

    # ── 6. 危废转移 ──
    m = re.search(r'(危废|废机油|废活性炭|污泥|废包装桶|废酸|废碱)[^0-9]{0,8}([0-9]+(?:\.[0-9]+)?)\s*(吨|公斤|千克|kg)', text)
    if m:
        result['records'].append({
            'type': '危废/固废', 'item': m.group(1), 'value': _num(m.group(2)), 'unit': m.group(3),
            'category': '固废管理',
        })

    # 识别时段
    if re.search(r'上午|早上|早晨', text): result['period'] = '上午'
    elif re.search(r'下午|中午', text): result['period'] = '下午'
    elif re.search(r'晚上|夜间|凌晨', text): result['period'] = '夜间'
    else: result['period'] = '未明确'

    if not result['records']:
        result['ok'] = False
        result['error'] = '未识别到环保数据。试着说：药剂加了XX公斤 / 进水XX吨 / COD XX'
        result['examples'] = [
            '今天上午加药 PAM 25公斤，进水 800吨',
            '出水 COD 42，氨氮 1.2',
            '2号风机故障停机，下午维修',
            '转移废活性炭 3吨',
        ]
    return result


def records_to_ledger(records, enterprise='', recorder='语音采集'):
    """结构化记录 → 台账行（可入台账表）"""
    import time
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    lines = []
    for r in records:
        lines.append({
            'time': ts,
            'enterprise': enterprise,
            'category': r['category'],
            'item': r['type'] + '·' + str(r['item']),
            'value': r['value'],
            'unit': r.get('unit', ''),
            'recorder': recorder,
        })
    return lines
