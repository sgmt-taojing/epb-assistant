#!/usr/bin/env python3
"""
环保执法智能分析模块
功能：案件智能分析、法条推荐、风险评估、证据链检查
"""

import os, json, re
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(os.path.dirname(SKILL_DIR), 'db')
LAW_MAPPING_FILE = os.path.join(DB_DIR, 'law_mapping.json')
CASES_FILE = os.path.join(DB_DIR, 'cases.json')

# 加载数据
def load_law_mapping():
    try:
        with open(LAW_MAPPING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_cases():
    try:
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get('cases', [])
    except:
        return []

# 信息提取
def extract_info(text):
    """从案情描述中提取关键信息"""
    result = {
        'party': None,
        'pollutants': [],
        'excess_ratio': None,
        'amount': None,
        'laws_mentioned': [],
        'violation_type': None,
        'keywords_matched': []
    }
    
    # 当事人提取
    party_pattern = r'(.{2,30}?)(公司|厂|企业|单位|合作社|医院|学院|酒店)'
    party_match = re.search(party_pattern, text)
    if party_match:
        result['party'] = party_match.group(0)
    
    # 污染物提取
    pollutants = ['COD', '氨氮', '总磷', '总氮', '重金属', '镉', '铅', '铬', '汞', '砷',
                  '二氧化硫', '氮氧化物', '颗粒物', 'PM2.5', 'PM10', 'VOCs', '挥发性有机物',
                  '危废', '危险废物', '医疗废物', '废机油', '废酸', '废碱']
    for p in pollutants:
        if p in text:
            result['pollutants'].append(p)
    
    # 超标倍数提取
    excess_pattern = r'超标(\d+\.?\d*)倍|超过.*?(\d+\.?\d*)倍'
    excess_match = re.search(excess_pattern, text)
    if excess_match:
        ratio = excess_match.group(1) or excess_match.group(2)
        result['excess_ratio'] = float(ratio)
    
    # 金额提取
    amount_pattern = r'罚款(\d+\.?\d*)万元|(\d+\.?\d*)万元罚款'
    amount_match = re.search(amount_pattern, text)
    if amount_match:
        result['amount'] = float(amount_match.group(1) or amount_match.group(2))
    
    # 法条提取
    law_pattern = r'《(.+?)》第(\d+)条'
    law_matches = re.findall(law_pattern, text)
    result['laws_mentioned'] = [f'《{m[0]}》第{m[1]}条' for m in law_matches]
    
    # 违法行为关键词匹配
    violation_keywords = {
        '水污染类': ['暗管', '偷排', '渗井', '渗坑', '超标排放废水', '绕排'],
        '大气污染类': ['超标排放', '废气', 'VOCs', '无组织排放', '篡改数据'],
        '固体废物类': ['危废', '非法倾倒', '非法处置', '医疗废物', '台账不规范'],
        '环评类': ['未批先建', '未验先投', '擅自建设', '擅自投产'],
        '排污许可类': ['无证排污', '超许可排污', '排污许可证'],
        '自动监控类': ['在线监测', '篡改', '数据造假', '不正常运行'],
        '噪声污染类': ['噪声超标', '扰民', '夜间施工'],
        '移动源监管类': ['柴油车', '非道路机械', '加油站', '油气回收', '检验机构']
    }
    
    for vtype, keywords in violation_keywords.items():
        for kw in keywords:
            if kw in text:
                result['violation_type'] = vtype
                result['keywords_matched'].append(kw)
    
    return result

# 法条推荐
def recommend_laws(violation_type, keywords, law_mapping):
    """根据违法类型推荐适用法条"""
    recommendations = []
    
    if not law_mapping or 'violation_types' not in law_mapping:
        return recommendations
    
    vtypes = law_mapping['violation_types']
    
    if violation_type in vtypes:
        for violation_name, details in vtypes[violation_type].items():
            # 检查关键词匹配
            v_keywords = details.get('keywords', [])
            if any(kw in ' '.join(keywords) for kw in v_keywords):
                recommendations.append({
                    'violation': violation_name,
                    'violations': details.get('violations', []),
                    'penalties': details.get('penalties', []),
                    'criminal': details.get('criminal'),
                    'evidence': details.get('evidence', []),
                    'measures': details.get('measures', []),
                    'risk_level': details.get('risk_level', '中风险')
                })
    
    return recommendations

# 风险评估
def assess_risk(case_info, law_recs):
    """评估案件风险等级"""
    score = 0
    risk_factors = []
    
    # 污染物权重
    high_risk_pollutants = ['重金属', '镉', '铅', '铬', '汞', '砷', '危废', '医疗废物', '有毒']
    for p in case_info.get('pollutants', []):
        if any(hr in p for hr in high_risk_pollutants):
            score += 30
            risk_factors.append(f"涉及高风险污染物：{p}")
    
    # 超标倍数权重
    excess_ratio = case_info.get('excess_ratio')
    if excess_ratio:
        if excess_ratio >= 10:
            score += 30
            risk_factors.append(f"超标{excess_ratio}倍（严重超标）")
        elif excess_ratio >= 3:
            score += 20
            risk_factors.append(f"超标{excess_ratio}倍")
        elif excess_ratio >= 1:
            score += 10
            risk_factors.append(f"超标{excess_ratio}倍")
    
    # 涉刑判断
    for rec in law_recs:
        if rec.get('criminal'):
            score += 40
            risk_factors.append(f"涉嫌刑事犯罪：{rec['criminal'].get('law', '未知')}")
    
    # 关键词风险
    high_risk_keywords = ['篡改', '造假', '暗管', '偷排', '非法倾倒', '数据造假']
    for kw in case_info.get('keywords_matched', []):
        if any(hr in kw for hr in high_risk_keywords):
            score += 20
            risk_factors.append(f"高风险行为：{kw}")
    
    # 判定等级
    if score >= 70:
        level = "高风险"
        color = "red"
    elif score >= 40:
        level = "中风险"
        color = "orange"
    else:
        level = "低风险"
        color = "green"
    
    return {
        'level': level,
        'score': score,
        'color': color,
        'factors': risk_factors
    }

# 证据链检查
def check_evidence_chain(case_info, law_recs):
    """检查证据链完整性"""
    required_evidence = set()
    
    for rec in law_recs:
        for e in rec.get('evidence', []):
            required_evidence.add(e)
    
    # 基础证据（几乎所有案件都需要）
    base_evidence = ['现场检查笔录', '企业负责人询问笔录', '现场照片/视频']
    for e in base_evidence:
        required_evidence.add(e)
    
    evidence_status = {
        'required': list(required_evidence),
        'missing': [],
        'collected': []
    }
    
    # TODO: 与已收集证据对比（需要用户输入）
    # 这里先返回所需证据清单
    
    return evidence_status

# 相似案例检索
def find_similar_cases(case_info, cases_db, limit=5):
    """检索相似案例"""
    results = []
    keywords = case_info.get('keywords_matched', [])
    violation_type = case_info.get('violation_type')
    
    for case in cases_db:
        score = 0
        case_type = case.get('type', '')
        case_tags = case.get('tags', [])
        case_keywords = case.get('keywords', [])
        
        # 类型匹配
        if violation_type and violation_type in case_type:
            score += 30
        
        # 关键词匹配
        case_text = ' '.join([case.get('title', ''), case.get('fact', ''), 
                              ' '.join(case_tags), ' '.join(case_keywords)])
        for kw in keywords:
            if kw in case_text:
                score += 10
        
        if score > 0:
            results.append({
                'score': score,
                'case': case
            })
    
    results.sort(key=lambda x: -x['score'])
    return [r['case'] for r in results[:limit]]

# 主分析函数
def analyze_case(text):
    """分析案件主函数"""
    law_mapping = load_law_mapping()
    cases_db = load_cases()
    
    # 1. 信息提取
    case_info = extract_info(text)
    
    # 2. 法条推荐
    law_recs = recommend_laws(
        case_info.get('violation_type'),
        case_info.get('keywords_matched', []),
        law_mapping
    )
    
    # 3. 风险评估
    risk = assess_risk(case_info, law_recs)
    
    # 4. 证据链检查
    evidence = check_evidence_chain(case_info, law_recs)
    
    # 5. 相似案例
    similar = find_similar_cases(case_info, cases_db)
    
    return {
        'extracted_info': case_info,
        'law_recommendations': law_recs,
        'risk_assessment': risk,
        'evidence_checklist': evidence,
        'similar_cases': similar
    }

# 生成分析报告
def generate_report(analysis_result, original_text):
    """生成分析报告文本"""
    report = []
    report.append("══════════════════════════════════════")
    report.append("📋 环保执法案件分析报告")
    report.append("══════════════════════════════════════")
    report.append("")
    
    # 案件摘要
    report.append("【案件摘要】")
    report.append(original_text[:100] + "..." if len(original_text) > 100 else original_text)
    report.append("")
    
    # 违法类型
    vi = analysis_result['extracted_info']
    report.append(f"【违法类型判定】🏷")
    report.append(f"  大类：{vi.get('violation_type', '待识别')}")
    report.append(f"  关键词：{', '.join(vi.get('keywords_matched', [])) or '无'}")
    report.append("")
    
    # 风险等级
    risk = analysis_result['risk_assessment']
    report.append(f"【风险等级】⚠️")
    report.append(f"  等级：{risk['level']}（评分：{risk['score']}）")
    if risk['factors']:
        report.append("  风险因素：")
        for f in risk['factors']:
            report.append(f"    • {f}")
    report.append("")
    
    # 适用法规
    law_recs = analysis_result['law_recommendations']
    if law_recs:
        report.append("【适用法规条款】⚖️")
        for i, rec in enumerate(law_recs, 1):
            report.append(f"  {i}. {rec['violation']}")
            report.append(f"     违反条款：{', '.join(rec['violations'])}")
            report.append(f"     处罚依据：{', '.join(rec['penalties'])}")
            if rec.get('criminal'):
                report.append(f"     ⚠️ 涉刑门槛：{rec['criminal']['threshold']}")
                report.append(f"     ⚠️ 刑事条款：{rec['criminal']['law']}")
            report.append("")
    else:
        report.append("【适用法规条款】⚖️")
        report.append("  未找到明确适用的法条，请人工核实或补充案情描述。")
        report.append("")
    
    # 证据要求
    evidence = analysis_result['evidence_checklist']
    report.append("【证据要求】📎")
    for i, e in enumerate(evidence['required'], 1):
        report.append(f"  {i}. {e}")
    report.append("")
    
    # 执法措施
    if law_recs:
        report.append("【执法措施建议】📋")
        for rec in law_recs:
            for i, m in enumerate(rec.get('measures', []), 1):
                report.append(f"  {i}. {m}")
        report.append("")
    
    # 相似案例
    similar = analysis_result['similar_cases']
    if similar:
        report.append("【相似典型案例】📂")
        for i, case in enumerate(similar[:3], 1):
            report.append(f"  {i}. {case.get('title', '未知案例')}")
            report.append(f"     处罚结果：{case.get('result', '未知')}")
            report.append("")
    else:
        report.append("【相似典型案例】📂")
        report.append("  暂无相似案例记录")
        report.append("")
    
    # 下一步操作
    report.append("【下一步操作建议】✅")
    if risk['level'] == '高风险':
        report.append("  1. 立即立案调查")
        report.append("  2. 采取查封扣押措施（必要时）")
        report.append("  3. 涉刑案件5日内移送公安机关")
        report.append("  4. 做好证据固定工作")
    elif risk['level'] == '中风险':
        report.append("  1. 责令改正违法行为")
        report.append("  2. 依法立案处罚")
        report.append("  3. 跟踪整改情况")
    else:
        report.append("  1. 责令改正")
        report.append("  2. 可适用简易程序")
        report.append("  3. 跟踪整改情况")
    
    report.append("")
    report.append("══════════════════════════════════════")
    
    return '\n'.join(report)

# CLI 入口
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 smart_analyzer.py '<案情描述>'")
        print("示例: python3 smart_analyzer.py '某化工厂私设暗管排放含重金属废水，超标5倍'")
        sys.exit(1)
    
    text = sys.argv[1]
    result = analyze_case(text)
    report = generate_report(result, text)
    print(report)
