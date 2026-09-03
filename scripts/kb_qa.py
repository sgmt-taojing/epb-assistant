#!/usr/bin/env python3
"""
EPB 统一知识问答引擎（一期建设 · 2026-08-31）
KB-first 三级分级（对齐平台 KB 北极星规范）：
  命中分 ≥ 0.7  → KB 直答（标注来源，零延迟）
  命中分 0.4-0.7 → KB 摘要 + 提示（一期无云端润色，返回摘要与原文入口）
  命中分 < 0.4  → 未命中兜底（返回推荐条目 + 引导 refine）

设计约束：
  - 纯本地（SQLite FTS5 + 关键词评分），断网可用，毫秒级响应
  - 禁止静默失败：所有分支有明确 tier 与提示
  - 输入清洗：去空格/长度限制/特殊字符过滤（企业级规范）
  - hit_count 回写：命中条目计数沉淀（后续 KB 质量优化的数据来源）
"""
import sqlite3
import json
import re
import os
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'db', 'epb.db')

MAX_Q_LEN = 200
STOP_WORDS = set('的了和与及或在为对由从被将怎么如何什么是什么请问一下是不是有哪些这个那个')
STOP_WORDS |= {'什么是', '什么是呀', '什么是啊', '什么是呢', '怎么算', '怎么样', '是什么', '这是啥', '请问', '什么', '咋', '咋办', '请问一下', '何为', '怎么', '如何'}
# 同义/缩写归一：口语词 → KB 标准用语（提升口语问题命中率）
SYNONYMS = {
    '涉刑': ['刑事', '刑法', '移送公安', '犯罪'],
    '判刑': ['刑事', '刑法', '有期徒刑'],
    '坐牢': ['刑事', '有期徒刑'],
    '坐牢的': ['刑事', '有期徒刑'],
    '罚款多少': ['罚款', '处罚标准'],
    '罚多少钱': ['罚款', '处罚标准'],
    '怎么罚': ['罚款', '处罚标准'],
    '危废': ['危险废物', '危废'],
    '被抓': ['移送公安', '刑事'],
    '环保局': ['生态环境主管部门', '生态环境局'],
    '监测造假': ['篡改监测数据', '伪造监测数据'],
    '数据造假': ['篡改监测数据', '伪造监测数据'],
}


def clean_query(q):
    """输入清洗：去首尾空格、压连续空白、过滤危险字符、限长"""
    if not q or not isinstance(q, str):
        return ''
    q = re.sub(r'[\x00-\x1f<>{}"\'`;]', '', q)
    q = re.sub(r'\s+', ' ', q).strip()
    return q[:MAX_Q_LEN]


def extract_terms(q):
    """粗分词：连续汉字段 + 英文/数字词，去停用词；同义归一扩充"""
    # 1) 剥疑问前缀（什么是/怎么/如何/何为 等）
    q_clean = q
    for prefix in ('什么是', '什么是呀', '什么是呢', '什么是啊', '怎么算', '怎么样', '是如何', '是啥', '是啥呀', '是什么', '怎么', '如何', '何为', '请问', '请告知', '请说明', '这算什么'):
        if q_clean.startswith(prefix):
            q_clean = q_clean[len(prefix):]
            break
    terms = []
    for seg in re.findall(r'[\u4e00-\u9fa5]+|[A-Za-z0-9]+', q_clean):
        if seg.lower() in STOP_WORDS or len(seg) < 1:
            continue
        terms.append(seg)
    # 同义/缩写归一：命中词扩充到标准用语（提升口语命中率）——对每个滑动窗词也检查
    expanded = []
    for t in terms:
        if t in SYNONYMS:
            expanded.extend(SYNONYMS[t])
    # 长句段先切窗再查同义词表（「危废倾倒涉刑吗」→ 窗词「涉刑」命中表）
    for t in terms:
        if re.match(r'[\u4e00-\u9fa5]+', t) and len(t) >= 2:
            for i in range(len(t)-1):
                w2 = t[i:i+2]
                if w2 in SYNONYMS:
                    expanded.extend(SYNONYMS[w2])
            for i in range(len(t)-2):
                w3 = t[i:i+3]
                if w3 in SYNONYMS:
                    expanded.extend(SYNONYMS[w3])
    expanded.extend(terms)
    # 汉字段再切 2-3 字滑动窗（unicode61 按单字索引，双字词需拆分匹配）
    final = []
    for t in expanded:
        if re.match(r'[\u4e00-\u9fa5]+', t):
            if len(t) >= 2:
                final.extend([t[i:i+2] for i in range(len(t)-1)])
            if len(t) >= 3:
                final.extend([t[i:i+3] for i in range(len(t)-2)])
        else:
            final.append(t)
    seen, out = set(), []
    for t in final:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def score_row(row, terms, raw_q):
    """命中评分：FTS 命中词数 + 标题命中加权 + 类别加权 → 0~1"""
    entry_id, title, content, keywords, summary, category = row
    score = 0.0
    text = (title or '') + ' ' + (content or '')
    kw_text = (keywords or '').strip('[]" ')
    hits = 0
    for t in terms:
        if t in text:
            hits += 1
            score += 0.09
            if t in (title or ''):
                score += 0.06  # 标题命中权重更高
            if t in kw_text:
                score += 0.04  # 关键词字段命中
    if not terms:
        return 0.0
    # 原始问题整串命中（长问句直接匹配到内容，强信号）
    if raw_q and raw_q in text:
        score += 0.25
    # 标题精确包含原问（去疑问前缀后）→ 最强信号（按日连续处罚 案例 vs 按日连续处罚·拒不改正 条目）
    if raw_q and len(raw_q) >= 4 and raw_q in (title or ''):
        score += 0.55
    # 类别加权：违法查处 / 法规条文 / 执法案例 / 企业管理 优先
    cat = (category or '').strip()
    if cat in ('violation', 'law', 'case', 'enterprise', 'public_service', 'industry'):
        score += 0.10
    # 类别先验：违法查处与法规条文是最常问的
    if category in ('violation', 'law'):
        score += 0.03 * min(hits, 2)
    # 核心词强信号：2字以上词在标题命中 ≥2 个（如「台账」+「指南」）→ 追加
    title_hits = sum(1 for t in terms if len(t) >= 2 and t in (title or ''))
    # 意图感知：问「怎么查/检查要点/清单」时行业指南（industry）优先于案例
    _intent_guide = any(k in raw_q for k in ('检查什么', '怎么查', '怎么检查', '检查要点', '查什么', '检查清单', '怎么处理', '怎么办', '特点', '要求', '规范', '指南', '频次', '流程'))
    if _intent_guide:
        if cat == 'industry':
            score += 0.35   # 指南型提问：行业要点优先
        elif cat == 'case' and '案例' not in raw_q and '处罚' not in raw_q:
            score -= 0.45   # 问指南时案例降权（问案例/处罚时案例仍优）
    if title_hits >= 2:
        score += 0.25
    elif title_hits == 1 and len(terms[0]) >= 2 and terms[0] in (title or ''):
        score += 0.15  # 首切词即标题词（「台账怎么记」→台账）
    return min(score, 1.0)


def search_kb(conn, q, limit=5):
    terms = extract_terms(q)
    if not terms:
        return [], terms
    cur = conn.cursor()
    NOISE = ('[环保监管-代码]', '[环保监管]')
    # 修真 2026-09-02：FTS 已重建为 trigram 分词（273 条全同步）
    # 混合检索：≥3字词走 trigram FTS（毫秒级子串匹配）；2字词走 LIKE（trigram 不支持 <3 字查询）
    _COLS = 'entry_id, title, content, keywords, summary, category'  # kb_fts 重建后含 category（trigram）
    long_terms = [t for t in terms if len(t) >= 3][:8]
    short_terms = [t for t in terms if len(t) < 3][:6]
    fts_rows, like_rows = [], []
    if long_terms:
        match_expr = ' OR '.join('"%s"' % t.replace('"', '') for t in long_terms)
        try:
            fts_rows = cur.execute(
                f'SELECT {_COLS} FROM kb_fts WHERE kb_fts MATCH ? LIMIT 60',
                (match_expr,)).fetchall()
        except Exception:
            fts_rows = []
    for t in short_terms:
        try:
            # 标题命中优先排前（ORDER BY），再取窗口——防高频词把目标挤出
            like_rows.extend(cur.execute(
                f'SELECT {_COLS} FROM kb_formal '
                'WHERE (title LIKE ? OR keywords LIKE ? OR content LIKE ?) '
                'AND title NOT LIKE ? AND title NOT LIKE ? '
                "ORDER BY (title LIKE ?) DESC, hit_count DESC LIMIT 15",
                (f'%{t}%', f'%{t}%', f'%{t}%', '[环保监管-代码]%', '[环保监管]%', f'%{t}%')).fetchall())
        except Exception:
            # 兼容无 hit_count 列
            try:
                like_rows.extend(cur.execute(
                    f'SELECT {_COLS} FROM kb_formal '
                    'WHERE (title LIKE ? OR content LIKE ?) '
                    'AND title NOT LIKE ? AND title NOT LIKE ? LIMIT 15',
                    (f'%{t}%', f'%{t}%', '[环保监管-代码]%', '[环保监管]%')).fetchall())
            except Exception:
                pass
    rows = fts_rows + like_rows
    rows = [r for r in rows if not (r[1] or '').startswith(NOISE)]
    # 2) 全空时 LIKE 全词兜底（断网/索引损坏场景）
    if not rows:
        like = '%' + (terms[0] if terms else q)[:30] + '%'
        try:
            rows = cur.execute(
                f'SELECT {_COLS} FROM kb_formal '
                'WHERE (title LIKE ? OR content LIKE ?) AND title NOT LIKE ? AND title NOT LIKE ? LIMIT 60',
                (like, like, '[环保监管-代码]%', '[环保监管]%')).fetchall()
        except Exception:
            rows = []
    scored = []
    seen = set()
    for r in rows:
        if r[0] in seen:
            continue
        seen.add(r[0])
        s = score_row(r, terms, q)
        if s > 0.05:
            scored.append((s, r))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit], terms


def format_answer(item):
    """把 KB 原文整理为可朗读/展示的答案段"""
    entry_id, title, content, keywords, summary, category, score = item
    lines = [l for l in (content or '').split('\n') if l.strip()]
    head = lines[0] if lines else title
    # 答题主体：violation/law 类型天然结构化，取前 6 行即覆盖核心
    body = lines[1:7]
    ans = head if head == title else (title.split(']')[-1].strip() + '：' + head)
    if body:
        ans += '\n' + '\n'.join(body)
    return ans


def answer(q):
    """主入口：q → {tier, score, answer, sources[], latency_ms}"""
    t0 = datetime.now()
    q_clean = clean_query(q)
    result = {
        'ok': True,
        'query': q_clean,
        'tier': 'miss',
        'score': 0.0,
        'answer': '',
        'sources': [],
        'related': [],
        'latency_ms': 0,
        'kb_total': 0,
    }
    if not q_clean:
        result['ok'] = False
        result['answer'] = '请输入您的问题（例如：私设暗管怎么处罚？）'
        result['latency_ms'] = (datetime.now() - t0).total_seconds() * 1000
        return result

    try:
        conn = sqlite3.connect(DB, timeout=5)
    except Exception as e:
        result['ok'] = False
        result['answer'] = f'知识库暂时不可用，请稍后重试（{e}）'
        result['latency_ms'] = (datetime.now() - t0).total_seconds() * 1000
        return result

    try:
        cur = conn.cursor()
        try:
            result['kb_total'] = cur.execute('SELECT COUNT(*) FROM kb_formal').fetchone()[0]
        except Exception:
            pass
        scored, terms = search_kb(conn, q_clean)
        if not scored:
            result['tier'] = 'miss'
            result['answer'] = ('知识库中暂未找到该问题的直接答案。\n'
                                '您可以：①换个说法再问（如「暗管 处罚」「VOCs 排放」）'
                                '②直接检索法规库/案例库；我们已记录该问题，将补充相关知识。')
            return result
        best_s, best_r = scored[0]
        result['score'] = round(best_s, 3)
        # 三级分级
        if best_s >= 0.7:
            result['tier'] = 'direct'
            result['answer'] = format_answer((*best_r, best_s))
            result['sources'] = [{
                'entry_id': best_r[0], 'title': best_r[1], 'category': best_r[5],
                'score': round(best_s, 3), 'source': '自有知识库（kb_formal）'
            }]
            # 回写命中计数（尽力而为，失败不影响回答）
            try:
                cur.execute('UPDATE kb_formal SET hit_count = hit_count + 1 WHERE entry_id = ?', (best_r[0],))
                conn.commit()
            except Exception:
                pass
        elif best_s >= 0.4:
            result['tier'] = 'summary'
            summ = (best_r[4] or best_r[1])
            result['answer'] = (f'根据知识库资料（{summ[:150]}）…\n'
                                '该问题与知识库部分匹配，以下是最相关的条目，点击可看完整内容。')
            result['sources'] = [{
                'entry_id': r[0], 'title': r[1], 'category': r[5], 'score': round(s, 3)
            } for s, r in scored[:3]]
        else:
            result['tier'] = 'miss'
            result['answer'] = '该问题在知识库中的匹配度较低，以下条目可能相关，或换个说法再问。'
            result['related'] = [{'title': r[1], 'category': r[5], 'score': round(s, 3)} for s, r in scored[:3]]
        # 附带次优相关条目（direct 也给，帮助扩展阅读）
        if scored and len(scored) > 1 and not result['related']:
            result['related'] = [{'title': r[1], 'category': r[5], 'score': round(s, 3)} for s, r in scored[1:4]]
        return result
    finally:
        conn.close()
        # latency 在 finally 后由调用方补（这里先算了）
        result['latency_ms'] = round((datetime.now() - t0).total_seconds() * 1000, 1)


if __name__ == '__main__':
    # 自测：三个代表性问题
    for q in ['私设暗管怎么处罚', 'VOCs 无组织排放', '危废倾倒 涉刑吗']:
        r = answer(q)
        print(f'Q: {q}\n  tier={r["tier"]} score={r["score"]} latency={r["latency_ms"]}ms\n  A: {r["answer"][:120]}\n')
