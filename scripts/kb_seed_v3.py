#!/usr/bin/env python3
"""
EPB 知识入库脚本（一期建设 · 2026-08-31）
把项目内已有结构化数据蒸馏入 kb_formal 自有知识库，并建 FTS5 索引：
  1. violation_types（33 类违法行为）→ 每类一条 KB（法条+处罚+证据+措施+裁量）
  2. cases（106 个执法案例）→ 每案一条 KB（案情+法条+结果）
  3. laws（有效法条行）→ 法条条目
  4. 环保局知识库.md / 环保执法案例库.md 已在库（跳过重复）

入库规则（蒸馏 SOP）：
  - entry_id 稳定可追溯（KB-EPB-{来源}-{hash}）
  - trust 分级：结构化业务表 0.9（项目内沉淀）、案例 0.85
  - module 统一 epb-assistant（隔离红线）
  - 幂等：重复运行跳过已存在 entry_id

用法：venv/bin/python scripts/kb_seed_v3.py   （或 python3 scripts/kb_seed_v3.py）
"""
import sqlite3
import json
import hashlib
import os
import sys
import re
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'db', 'epb.db')

def _eid(prefix, *parts):
    h = hashlib.md5(('|'.join(str(p) for p in parts)).encode('utf-8')).hexdigest()[:12]
    return f'KB-EPB-{prefix}-{h}'

def _now():
    return datetime.now().isoformat(timespec='seconds')

def _kw(text, n=12):
    """粗粒度关键词提取：去停用词后取高频 2-6 字词（简单可靠，不引外部依赖）"""
    stop = set('的了和与及或在为对由从被将按照规定以下以上其他相关情况进行应当不得可以依法予以违反没收罚款责令改正'.replace(' ', ''))
    words = re.findall(r'[\u4e00-\u9fa5]{2,6}', text or '')
    freq = {}
    for w in words:
        if set(w) & stop and len(set(w) - stop) == 0:
            continue
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda x: -x[1])[:n]
    return json.dumps([w for w, _ in top], ensure_ascii=False)

def _summary(text, n=120):
    t = re.sub(r'\s+', ' ', text or '').strip()
    return t[:n]

def upsert(cur, entry_id, module, title, content, category, src_id, trust, tags, keywords, summary):
    cur.execute('SELECT 1 FROM kb_formal WHERE entry_id=?', (entry_id,))
    if cur.fetchone():
        return False
    cur.execute(
        'INSERT INTO kb_formal (entry_id, module, title, content, category, src_id, trust_score, hit_count, tags, keywords, summary, created_at, updated_at) '
        'VALUES (?,?,?,?,?,?,?,0,?,?,?,?,?)',
        (entry_id, module, title, content, category, src_id, trust, tags, keywords, summary, _now(), _now())
    )
    return True

def seed_violations(cur):
    """33 类违法行为 → KB：这是问答最高频的命中源（执法人员问'暗管怎么查/罚多少'）"""
    n = 0
    rows = cur.execute('SELECT category, sub_type, violations, penalties, criminal_threshold, criminal_law, criminal_sentence, evidence, measures, risk_level, keywords, discretion FROM violation_types').fetchall()
    for r in rows:
        (category, sub_type, violations, penalties, crim_th, crim_law, crim_sent, evidence, measures, risk, kw_json, discretion) = r
        try:
            vio_list = json.loads(violations) if violations else []
            pen_list = json.loads(penalties) if penalties else []
            ev_list = json.loads(evidence) if evidence else []
            ms_list = json.loads(measures) if measures else []
        except Exception:
            vio_list, pen_list, ev_list, ms_list = [], [], [], []
        parts = [f'【违法类型】{category} · {sub_type}（风险等级：{risk or "中"}）']
        if vio_list:
            parts.append('【适用法条】' + '；'.join(vio_list))
        if pen_list:
            parts.append('【处罚标准】' + '；'.join(pen_list))
        if crim_th:
            parts.append(f'【刑事门槛】{crim_th} → {crim_law or ""}（{crim_sent or ""}）'.strip())
        if ev_list:
            parts.append('【证据清单】' + '；'.join(ev_list))
        if ms_list:
            parts.append('【处置措施】' + '；'.join(ms_list))
        try:
            disc = json.loads(discretion) if discretion else {}
            if disc:
                base = disc.get('base', '')
                factors = disc.get('factors', {})
                lines = [f'【裁量基准】{base}'] if base else ['【裁量基准】']
                for fname, fv in factors.items():
                    if isinstance(fv, dict):
                        lines.append(f'  {fname}：' + '；'.join(f'{k}→{v}' for k, v in fv.items()))
                parts.append('\n'.join(lines))
        except Exception:
            pass
        content = '\n'.join(parts)
        try:
            extra_kw = json.loads(kw_json) if kw_json else []
        except Exception:
            extra_kw = []
        kws = list(dict.fromkeys(extra_kw + json.loads(_kw(content))))
        eid = _eid('VIO', category, sub_type)
        title = f'[违法查处] {category}·{sub_type}'
        if upsert(cur, eid, 'epb-assistant', title, content, 'violation', 'violation_types 表（33类违法查处规程）', 0.9,
                  json.dumps({'domain': '违法查处', 'category': category, 'risk': risk or '中'}, ensure_ascii=False),
                  json.dumps(kws, ensure_ascii=False), _summary(f'{category}{sub_type}：{pen_list[0] if pen_list else ""}')):
            n += 1
    return n

def seed_cases(cur):
    """106 个执法案例 → KB：问'有没有类似案子'时的命中源"""
    n = 0
    rows = cur.execute('SELECT id, title, type, fact, law, result, risk_level, criminal FROM cases').fetchall()
    for (cid, title, ctype, fact, law, result, risk, criminal) in rows:
        parts = [f'【案例】{title}']
        if ctype:
            parts.append(f'【分类】{ctype}（风险：{risk or "中"}）')
        if fact:
            parts.append(f'【案情】{fact}')
        if law:
            parts.append(f'【适用法条】{law}')
        if result:
            parts.append(f'【处理结果】{result}')
        if criminal:
            parts.append('【涉刑】是（移送公安）')
        content = '\n'.join(parts)
        eid = _eid('CASE', cid or title)
        if upsert(cur, eid, 'epb-assistant', f'[执法案例] {title}', content, 'case', f'cases 表（{cid}）', 0.85,
                  json.dumps({'domain': '执法案例', 'type': ctype or '', 'risk': risk or '中'}, ensure_ascii=False),
                  _kw(content), _summary(f'{title}——{fact or ""}')):
            n += 1
    return n

def seed_laws(cur):
    """有效法条行 → KB：问'某某法多少条罚多少'的命中源（跳过空article与垃圾行）"""
    n = 0
    rows = cur.execute("SELECT law_name, article, full_text, bracket, case_count FROM laws WHERE article IS NOT NULL AND article != ''").fetchall()
    for (law_name, article, full_text, bracket, case_count) in rows:
        if not law_name or law_name in ('G', 'H'):
            continue
        body = (full_text or '').strip()
        if not body or len(body) < 10:  # 只有标题没有正文的跳过（等后续补法）
            continue
        parts = [f'【法条】{law_name} 第{article}']
        if bracket:
            parts.append(f'【关联】{bracket}')
        if case_count:
            parts.append(f'【关联案例数】{case_count}')
        parts.append(f'【条文】{body}')
        content = '\n'.join(parts)
        eid = _eid('LAW', law_name, article)
        if upsert(cur, eid, 'epb-assistant', f'[法规条文] {law_name}·第{article}', content, 'law', f'laws 表（{law_name} {article}）', 0.8,
                  json.dumps({'domain': '法规条文', 'law': law_name}, ensure_ascii=False),
                  _kw(content), _summary(body)):
            n += 1
    return n

def build_fts(cur):
    """FTS5 全文索引（问答检索核心，毫秒级）"""
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kb_fts'")
    if cur.fetchone():
        cur.execute('DELETE FROM kb_fts')
        cur.execute("INSERT INTO kb_fts(kb_fts) VALUES('rebuild')")
        return 'rebuilt'
    # unicode61 分词器：SQLite 内置，中文按学字切分配合 OR 匹配已够用（不依赖外部扩展）
    cur.execute('''
        CREATE VIRTUAL TABLE kb_fts USING fts5(
            entry_id UNINDEXED, title, content, keywords, summary,
            tokenize='unicode61'
        )''')
    cur.execute('''
        INSERT INTO kb_fts(entry_id, title, content, keywords, summary)
        SELECT entry_id, title, content, COALESCE(keywords,''), COALESCE(summary,'') FROM kb_formal
    ''')
    return 'created'

def main():
    if not os.path.exists(DB):
        print(f'❌ 数据库不存在: {DB}')
        sys.exit(1)
    conn = sqlite3.connect(DB)
    try:
        cur = conn.cursor()
        before = cur.execute('SELECT COUNT(*) FROM kb_formal').fetchone()[0]
        n1 = seed_violations(cur)
        n2 = seed_cases(cur)
        n3 = seed_laws(cur)
        fts_state = build_fts(cur)
        conn.commit()
        after = cur.execute('SELECT COUNT(*) FROM kb_formal').fetchone()[0]
        fts_n = cur.execute('SELECT COUNT(*) FROM kb_fts').fetchone()[0]
        print(f'✅ 知识入库完成：违法查处 +{n1} · 执法案例 +{n2} · 法规条文 +{n3}')
        print(f'   kb_formal 总量：{before} → {after}')
        print(f'   kb_fts 索引：{fts_state}（{fts_n} 条）')
        by_cat = cur.execute('SELECT category, COUNT(*) FROM kb_formal GROUP BY category ORDER BY COUNT(*) DESC').fetchall()
        for cat, c in by_cat:
            print(f'   - {cat}: {c}')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
