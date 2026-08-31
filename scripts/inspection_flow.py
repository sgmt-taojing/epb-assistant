#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执法检查端到端流水线（二期 · Phase 2）
流程：企业+检查类型 → 生成检查清单（KB驱动） → 现场记录+证据 → 智能分析+法条匹配 → 文书生成 → 案件落库
全部本地算力，断网可用；每步异常兜底，禁止静默失败。
"""
import json
import os
import re
import sqlite3
import time
import uuid

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'epb.db')

# ---------------- 检查类型 → violation_types 类别映射 ----------------
INSPECTION_CATEGORIES = {
    'water': ['水污染类'],
    'air': ['大气污染类', '监测数据造假类'],
    'solid': ['固体废物类'],
    'permit': ['排污许可类', '排污许可违规类'],
    'eia': ['环评类', '环评违规类'],
    'monitor': ['自动监控类', '监测数据造假类'],
    'noise': ['噪声污染类'],
    'mobile': ['移动源监管类'],
    'radiation': ['辐射污染类'],
    'soil': ['土壤污染类'],
    'eco': ['生态破坏类'],
    'emergency': ['应急响应违规类'],
}

INSPECTION_TYPE_NAMES = {
    'water': '水污染防治', 'air': '大气污染防治', 'solid': '固体废物污染防治',
    'permit': '排污许可', 'eia': '环评审批验收', 'monitor': '自动监控',
    'noise': '噪声污染防治', 'mobile': '移动源监管', 'radiation': '辐射安全',
    'soil': '土壤污染防治', 'eco': '生态保护', 'emergency': '环境应急',
}

# 每类检查的常规前置资料（通用 + 行业无关）
BASE_DOCUMENTS = [
    '排污许可证正副本', '环评批复文件', '环保竣工验收材料',
    '环保管理台账（近12个月）', '监测报告（近6个月）', '环保设施运行记录',
]
BASE_ONSITE = [
    '排污口设置及标识', '环保设施运行现场', '危废暂存间（如涉及）',
    '雨污分流管网', '在线监测站房（如涉及）',
]

_CLEAN_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f<>]')


def _clean(s, limit=200):
    """输入清洗：去控制字符/尖括号、限长"""
    if not isinstance(s, str):
        return ''
    return _CLEAN_RE.sub('', s.strip())[:limit]


def _conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def gen_checklist(data):
    """步骤1：生成检查清单（企业+检查类型 → KB驱动的检查项）"""
    try:
        enterprise = _clean(data.get('enterprise', ''), 80)
        ent_id = _clean(data.get('enterprise_id', ''), 40)
        insp_type = _clean(data.get('inspection_type', ''), 20) or 'water'

        categories = INSPECTION_CATEGORIES.get(insp_type)
        if not categories:
            return {'ok': False, 'error': f'不支持的检查类型: {insp_type}（可选: {"、".join(INSPECTION_CATEGORIES)}）'}, 400

        conn = _conn()
        # 从 violation_types 拉取该类别的所有违法情形 → 检查项
        rows = []
        for cat in categories:
            rows.extend(conn.execute(
                'SELECT category, sub_type, violations, evidence, measures, risk_level, keywords '
                'FROM violation_types WHERE category = ?', (cat,)).fetchall())
        # 企业信息（名称兜底）
        ent = None
        if ent_id:
            ent = conn.execute('SELECT * FROM enterprises WHERE id = ?', (ent_id,)).fetchone()
        elif enterprise:
            ent = conn.execute('SELECT * FROM enterprises WHERE name LIKE ? LIMIT 1', (f'%{enterprise}%',)).fetchone()
        conn.close()

        check_items = []
        for r in rows:
            try:
                violations = json.loads(r['violations'] or '[]')
            except Exception:
                violations = []
            try:
                evidence = json.loads(r['evidence'] or '[]')
            except Exception:
                evidence = []
            try:
                keywords = json.loads(r['keywords'] or '[]')
            except Exception:
                keywords = []
            check_items.append({
                'check_point': f"{r['sub_type']}（{'、'.join(violations[:1]) or '合规性核查'}）",
                'risk_level': r['risk_level'] or '中风险',
                'evidence_required': evidence[:5],
                'keywords': keywords[:6],
            })

        checklist_id = 'CHK-' + time.strftime('%Y%m%d') + '-' + uuid.uuid4().hex[:6].upper()
        return {
            'ok': True,
            'checklist_id': checklist_id,
            'enterprise': (ent['name'] if ent else enterprise) or '未指定企业',
            'enterprise_id': ent['id'] if ent else (ent_id or ''),
            'enterprise_type': ent['type'] if ent else '',
            'enterprise_risk': ent['risk_level'] if ent else '',
            'enterprise_credit': ent['credit_level'] if ent else '',
            'inspection_type': insp_type,
            'inspection_type_name': INSPECTION_TYPE_NAMES.get(insp_type, insp_type),
            'documents_to_review': BASE_DOCUMENTS,
            'onsite_points': BASE_ONSITE,
            'check_items': check_items,
            'total_items': len(check_items),
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }, 200
    except Exception as e:
        return {'ok': False, 'error': f'清单生成失败: {e}'}, 500


def submit_inspection(data):
    """步骤2：现场检查结果提交 → 智能分析 + 法条匹配 + 文书预生成 + 案件落库（端到端）"""
    try:
        checklist_id = _clean(data.get('checklist_id', ''), 40)
        enterprise = _clean(data.get('enterprise', ''), 80) or '未指定企业'
        insp_type = _clean(data.get('inspection_type', ''), 20) or 'water'
        findings = data.get('findings') or []
        if not isinstance(findings, list):
            findings = []
        notes = _clean(data.get('notes', ''), 1000)
        inspector = _clean(data.get('inspector', ''), 30) or '执法人员'

        # ---- 1. 汇总问题项 → 违规关键词集 ----
        problems = []
        for f in findings:
            if not isinstance(f, dict):
                continue
            item = _clean(f.get('check_point', ''), 120)
            if not item:
                continue
            problems.append({
                'check_point': item,
                'result': 'abnormal' if f.get('result') in ('abnormal', 'abnormal_within_limit', 'not_applicable_ok') else str(f.get('result', 'normal')),
                'detail': _clean(f.get('detail', ''), 300),
                'risk_level': _clean(f.get('risk_level', ''), 10),
            })
        abnormal = [p for p in problems if p['result'] != 'normal']
        compliant = len(problems) - len(abnormal)

        # ---- 2. KB 法条匹配（复用 kb_qa 的同义归一与评分）----
        law_matches = []
        fact_text = ';'.join([p['check_point'] + ' ' + p['detail'] for p in abnormal]) or (notes or insp_type)
        try:
            import sys as _sys
            _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import kb_qa
            r = kb_qa.answer(fact_text if fact_text else insp_type)
            for s in (r.get('sources') or [])[:3]:
                law_matches.append({
                    'title': s.get('title', ''),
                    'entry_id': s.get('entry_id', ''),
                    'score': round(float(s.get('score', 0)), 2),
                })
            for s in (r.get('related') or [])[:5]:
                law_matches.append({
                    'title': s.get('title', ''),
                    'entry_id': '',
                    'score': round(float(s.get('score', 0)), 2),
                })
        except Exception:
            law_matches = []

        # ---- 3. 生成案情文本（结构化 → 文书用）----
        dt = time.strftime('%Y-%m-%d %H:%M')
        if abnormal:
            fact_lines = [f"{i+1}. {p['check_point']}" + (f"（{p['detail']}）" if p['detail'] else '') for i, p in enumerate(abnormal)]
            fact = f"现场检查发现：{enterprise}存在以下问题：{'；'.join(fact_lines)}。"
            doc_type = 'zlgztz'  # 责令改正通知书
            doc_name = '责令改正通知书'
        else:
            fact = f"现场检查未发现环境违法行为。共核查 {len(problems)} 项检查点，全部合规。"
            doc_type = 'xcjcbcjl'  # 现场检查笔录
            doc_name = '现场检查笔录'

        # ---- 4. 生成执法文书（真实 docx，失败降级为文本预览）----
        doc_result = {'ok': False, 'error': '未生成'}
        try:
            from doc_generator import generate_doc
            out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outputs')
            os.makedirs(out_dir, exist_ok=True)
            safe_name = f"{doc_type}_{time.strftime('%Y%m%d%H%M%S')}.docx"
            case_data = {
                'party': enterprise,
                'fact': fact,
                'requirement': '立即改正上述行为，并于15日内将改正情况书面报告我局',
                'deadline': time.strftime('%Y年%m月%d日', time.localtime(time.time() + 15 * 86400)),
                'law': '、'.join([m['title'] for m in law_matches[:2]]) or '《中华人民共和国环境保护法》',
                'inspector': inspector,
                'location': enterprise,
                'facts': fact,
                'date': dt,
            }
            path, cid = generate_doc(doc_type, case_data, os.path.join(out_dir, safe_name))
            doc_result = {'ok': True, 'doc_type': doc_type, 'doc_name': doc_name,
                          'download_url': f'/outputs/{os.path.basename(path)}', 'filename': os.path.basename(path)}
        except Exception as e:
            doc_result = {'ok': False, 'error': f'文书生成失败（不影响案件落库）: {e}',
                          'doc_type': doc_type, 'doc_name': doc_name, 'fallback_text': fact}

        # ---- 5. 案件落库（有问题 → 正式案件；无问题 → 检查记录）----
        case_id = 'INSP-' + time.strftime('%Y%m%d') + '-' + uuid.uuid4().hex[:6].upper()
        has_problem = 1 if abnormal else 0
        risk = '高风险' if any(p['risk_level'] == '高风险' for p in abnormal) else ('中风险' if abnormal else '低风险')
        status = 'investigating' if abnormal else 'closed'
        law_json = json.dumps([m['title'] for m in law_matches[:4]], ensure_ascii=False)
        conn = _conn()
        conn.execute(
            'INSERT INTO cases (id, date, title, party, type, source, fact, law, result, status, tags, risk_level, criminal, fetched_at) '
            'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (case_id, time.strftime('%Y-%m-%d'),
             (f"{enterprise}{'·' + '、'.join([p['check_point'][:12] for p in abnormal[:1]]) if abnormal else '合规检查'}·{INSPECTION_TYPE_NAMES.get(insp_type, insp_type)}检查"),
             enterprise, INSPECTION_TYPE_NAMES.get(insp_type, insp_type), '现场检查（智能清单）',
             fact + (f'（检查员备注：{notes}）' if notes else ''),
             law_json,
             '待整改' if abnormal else '合规通过',
             status, json.dumps([p['check_point'][:20] for p in abnormal[:5]], ensure_ascii=False),
             risk, 0, time.strftime('%Y-%m-%dT%H:%M:%S')))
        conn.commit()
        conn.close()

        return {
            'ok': True,
            'case_id': case_id,
            'checklist_id': checklist_id,
            'enterprise': enterprise,
            'inspection_type_name': INSPECTION_TYPE_NAMES.get(insp_type, insp_type),
            'summary': {
                'total_items': len(problems),
                'abnormal_items': len(abnormal),
                'compliant_items': compliant,
                'risk_level': risk,
                'has_problem': bool(abnormal),
            },
            'problems': abnormal,
            'law_matches': law_matches[:6],
            'fact_text': fact,
            'document': doc_result,
            'inspector': inspector,
            'inspected_at': dt,
        }, 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'ok': False, 'error': f'检查提交失败: {e}'}, 500


if __name__ == '__main__':
    # 自测：水污染检查清单
    r, code = gen_checklist({'enterprise': '鲁药东营制药有限公司', 'inspection_type': 'water'})
    print('清单:', code, r.get('total_items'), '项 |', r.get('enterprise'))
    # 自测：提交检查（含2项异常）
    r2, code2 = submit_inspection({
        'checklist_id': r.get('checklist_id'),
        'enterprise': r.get('enterprise'),
        'inspection_type': 'water',
        'inspector': '张执法',
        'findings': [
            {'check_point': '私设暗管', 'result': 'abnormal', 'detail': '厂区西侧发现暗管直排', 'risk_level': '高风险'},
            {'check_point': '危废暂存间标识', 'result': 'abnormal', 'detail': '标识缺失', 'risk_level': '中风险'},
            {'check_point': '排污口规范化', 'result': 'normal', 'detail': ''},
        ],
        'notes': '现场已责令停止排放',
    })
    print('提交:', code2, r2.get('case_id'), '| 异常:', r2.get('summary', {}).get('abnormal_items'), '| 文书:', r2.get('document', {}).get('ok'), r2.get('document', {}).get('doc_name'))
