#!/usr/bin/env python3
"""
补充地方法规到 law_index.json
覆盖山东省、宁夏回族自治区环保地方法规
"""
import json, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'db')
LAW_FILE = os.path.join(DB_DIR, 'law_index.json')

with open(LAW_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

laws = data.get('laws', {})

# 山东省地方法规
SHANDONG_LAWS = {
    "山东省水污染防治条例": {
        "total_articles": 95,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第七章 法律责任",
                "full": "《山东省水污染防治条例》第七十三条：排放水污染物超过排放标准或者重点污染物排放总量控制指标的，由县级以上人民政府环境保护主管部门责令改正或者责令限制生产、停产整治，并处十万元以上一百万元以下的罚款",
                "article": "第73条",
                "bracket": "罚款10-100万元",
                "case_count": 0,
                "cases": []
            },
            {
                "key": "第四章 饮用水水源保护",
                "full": "《山东省水污染防治条例》第四十五条：在饮用水水源保护区内，禁止设置排污口",
                "article": "第45条",
                "bracket": "禁止设排污口",
                "case_count": 0,
                "cases": []
            }
        ]
    },
    "山东省大气污染防治条例": {
        "total_articles": 80,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第五章 法律责任",
                "full": "《山东省大气污染防治条例》第六十一条：超过大气污染物排放标准或者超过重点污染物排放总量控制指标排放大气污染物的，由县级以上人民政府环境保护主管部门责令改正或者限制生产、停产整治，并处十万元以上一百万元以下的罚款",
                "article": "第61条",
                "bracket": "罚款10-100万元",
                "case_count": 0,
                "cases": []
            }
        ]
    },
    "山东省固体废物污染环境防治条例": {
        "total_articles": 60,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第五章 法律责任",
                "full": "《山东省固体废物污染环境防治条例》第四十八条：违反本条例规定，未按照规定收集、贮存、转移、处置固体废物的，由生态环境主管部门责令改正，处以罚款",
                "article": "第48条",
                "bracket": "责令改正+罚款",
                "case_count": 0,
                "cases": []
            }
        ]
    },
    "山东省环境保护条例": {
        "total_articles": 87,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第五章 法律责任",
                "full": "《山东省环境保护条例》第六十九条：企业事业单位和其他生产经营者违法排放污染物，受到罚款处罚，被责令改正，拒不改正的，依法作出处罚决定的行政机关可以自责令改正之日的次日起，按照原处罚数额按日连续处罚",
                "article": "第69条",
                "bracket": "按日连续处罚",
                "case_count": 0,
                "cases": []
            }
        ]
    },
}

# 宁夏回族自治区地方法规
NINGXIA_LAWS = {
    "宁夏回族自治区环境保护条例": {
        "total_articles": 70,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第五章 法律责任",
                "full": "《宁夏回族自治区环境保护条例》第五十五条：违反本条例规定，排放污染物超过国家或者地方规定的污染物排放标准的，由县级以上人民政府生态环境主管部门责令改正或者限制生产、停产整治，并处十万元以上一百万元以下的罚款",
                "article": "第55条",
                "bracket": "罚款10-100万元",
                "case_count": 0,
                "cases": []
            }
        ]
    },
    "宁夏回族自治区水污染防治条例": {
        "total_articles": 68,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第六章 法律责任",
                "full": "《宁夏回族自治区水污染防治条例》第五十八条：企业事业单位和其他生产经营者排放水污染物超过水污染物排放标准或者重点水污染物排放总量控制指标的，由县级以上人民政府生态环境主管部门责令改正或者责令限制生产、停产整治，并处十万元以上一百万元以下的罚款",
                "article": "第58条",
                "bracket": "罚款10-100万元",
                "case_count": 0,
                "cases": []
            }
        ]
    },
    "宁夏回族自治区大气污染防治条例": {
        "total_articles": 62,
        "total_cases": 0,
        "provisions": [
            {
                "key": "第五章 法律责任",
                "full": "《宁夏回族自治区大气污染防治条例》第五十二条：违反本条例规定，排放大气污染物超过排放标准或者重点污染物排放总量控制指标的，由县级以上人民政府生态环境主管部门责令改正或者限制生产、停产整治，并处十万元以上一百万元以下的罚款",
                "article": "第52条",
                "bracket": "罚款10-100万元",
                "case_count": 0,
                "cases": []
            }
        ]
    },
}

# 合并
added = 0
for title, content in {**SHANDONG_LAWS, **NINGXIA_LAWS}.items():
    if title not in laws:
        laws[title] = content
        added += 1

# 更新统计
data['total_laws'] = len(laws)
data['updated'] = '2026-06-24'

# 关联案例
cases = json.load(open(os.path.join(DB_DIR, 'cases.json')))
for title, law in {**SHANDONG_LAWS, **NINGXIA_LAWS}.items():
    if title not in SHANDONG_LAWS and title not in NINGXIA_LAWS:
        continue
    region = '山东' if title.startswith('山东省') else '宁夏'
    matched = []
    for c in cases:
        source = c.get('source', '')
        if region in source:
            matched.append({
                "id": c['id'],
                "title": c.get('title', ''),
                "type": c.get('type', ''),
                "date": c.get('date', ''),
                "risk_level": c.get('risk_level', ''),
                "status": c.get('status', '')
            })
    if matched:
        for prov in law['provisions']:
            prov['case_count'] = len(matched)
            prov['cases'] = matched
        law['total_cases'] = len(matched)

with open(LAW_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"新增地方法规: {added} 部")
print(f"法规总数: {data['total_laws']} 部")
print("\n新增条目:")
for title in {**SHANDONG_LAWS, **NINGXIA_LAWS}:
    if title in laws:
        print(f"  - {title}")
