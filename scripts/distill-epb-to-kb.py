#!/usr/bin/env python3
"""
EPB Assistant → 命理宝鉴 KB 蒸馏脚本
- 蒸馏 101 个真实执法案例（水/气/固废/噪声/危废）
- 蒸馏 35 条环保法规
- 蒸馏 33 个违规类型
- 输出: 160+ KB 条目到 yidao.db kb_staging
"""
import sqlite3, json, datetime, hashlib, os, sys

DST_DB = '/Users/tom/.openclaw-autoclaw/workspace/projects/mingli-baojian/server/database/yidao.db'
SRC_DB = '/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/db/epb.db'

def register_source(dst, title, trust=0.85):
    now = datetime.datetime.now().isoformat()
    src_id = f'SRC-EPB-ASSISTANT-{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}'
    dst.execute(
        "INSERT INTO source_index (src_id, src_type, title, author, url, trust_score, tags, access_level, created_at, path, format, size_bytes, module) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (src_id, 'SRC-DISTILL-EPB', title, 'epb-assistant-distill', 'projects/epb-assistant/', trust, 'environmental,law,case,violation,compliance', 'internal', now, 'projects/epb-assistant/', 'sqlite', os.path.getsize(SRC_DB), 'epb')
    )
    return src_id

def distill_cases(src, dst, src_id):
    src.row_factory = sqlite3.Row
    cases = src.execute('SELECT * FROM cases ORDER BY date DESC').fetchall()
    now = datetime.datetime.now().isoformat()
    synced, skipped = 0, 0
    for row in cases:
        title = f"[EPB案例] {row['title']}"
        law_list = json.loads(row['law']) if row['law'] else []
        tags_list = json.loads(row['tags']) if row['tags'] else []
        content = f"""# {title}

## 案件概要
- **日期**: {row['date']}
- **当事人**: {row['party']}
- **类型**: {row['type']}
- **来源**: {row['source']}
- **状态**: {row['status']}
- **风险等级**: {row['risk_level']}
- **刑事**: {"是" if row['criminal'] else "否"}

## 案情事实
{row['fact']}

## 适用法规
{', '.join(law_list) if law_list else '无'}

## 处罚结果
{row['result']}

## 标签
{', '.join(tags_list)}

---
*来源: epb-assistant 移动源监管案例库 · trust=0.85*
"""
        fp = hashlib.sha256(content.encode()).hexdigest()[:16]
        if dst.execute('SELECT entry_id FROM kb_staging WHERE fingerprint=?', (fp,)).fetchone():
            skipped += 1
            continue
        cat = f'epb-case-{row["type"].split("类")[0] if "类" in row["type"] else row["type"]}'
        dst.execute(
            """INSERT INTO kb_staging
               (module, title, content, src_id, category, keywords, summary,
                raw_metadata, status, tags, confidence, source_ids, fingerprint, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                'epb-case', title, content, src_id, cat,
                f"环保,执法,案例,{row['type']},{row['risk_level']}",
                row['fact'][:200],
                json.dumps({'case_id': row['id'], 'date': row['date'], 'type': row['type'], 'risk_level': row['risk_level'], 'criminal': bool(row['criminal'])}),
                'staged', ', '.join(tags_list), 0.85,
                json.dumps([src_id]), fp, now, now
            )
        )
        synced += 1
    return synced, skipped, len(cases)

def distill_laws(src, dst, src_id):
    src.row_factory = sqlite3.Row
    laws = src.execute('SELECT * FROM laws ORDER BY id').fetchall()
    now = datetime.datetime.now().isoformat()
    synced, skipped = 0, 0
    for row in laws:
        title = f"[EPB法规] {row['law_name']}"
        content = f"""# {title}

## 法规全文
{row['full_text'] if row['full_text'] else '（详见原文）'}

## 条款信息
- **条款**: {row['article'] if row['article'] else '全文'}
- **关联案例数**: {row['case_count']}
- **总条款数**: {row['total_articles']}
- **更新日期**: {row['updated']}

---
*来源: epb-assistant 法规库 · trust=0.85*
"""
        fp = hashlib.sha256(content.encode()).hexdigest()[:16]
        if dst.execute('SELECT entry_id FROM kb_staging WHERE fingerprint=?', (fp,)).fetchone():
            skipped += 1
            continue
        dst.execute(
            """INSERT INTO kb_staging
               (module, title, content, src_id, category, keywords, summary,
                raw_metadata, status, tags, confidence, source_ids, fingerprint, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                'epb-law', title, content, src_id, 'epb-law',
                f"环保,法规,法律,{row['law_name']}",
                (row['full_text'] or row['article'] or '')[:200],
                json.dumps({'law_name': row['law_name'], 'article': row['article'], 'case_count': row['case_count'], 'updated': row['updated']}),
                'staged', f"环保法规,{row['law_name']}", 0.88,
                json.dumps([src_id]), fp, now, now
            )
        )
        synced += 1
    return synced, skipped, len(laws)

def distill_violations(src, dst, src_id):
    """蒸馏 33 个违规类型 → KB 条目（category+sub_type 字段）"""
    src.row_factory = sqlite3.Row
    vts = src.execute('SELECT * FROM violation_types ORDER BY id').fetchall()
    now = datetime.datetime.now().isoformat()
    synced, skipped = 0, 0
    for row in vts:
        vname = row['sub_type'] or f'类型{row["id"]}'
        title = f"[EPB违规类型] {row['category']}-{vname}"
        content = f"""# {title}

## 违规内容
{row['violations'] or vname}

## 分类信息
- **类型ID**: {row['id']}
- **类别**: {row['category']}
- **子类型**: {row['sub_type']}
- **风险等级**: {row['risk_level'] or '未知'}
- **刑事门槛**: {row['criminal_threshold'] or '无'}
- **刑事条款**: {row['criminal_law'] or '无'}
- **刑事量刑**: {row['criminal_sentence'] or '无'}

## 证据要求
{row['evidence'] or '详见法规'}

## 处置措施
{row['measures'] or '详见法规'}

## 处罚依据
{row['penalties'] or '详见法规'}

## 关键词
{row['keywords'] or ''}

---
*来源: epb-assistant 违规类型库 · trust=0.85*
"""
        fp = hashlib.sha256(content.encode()).hexdigest()[:16]
        if dst.execute('SELECT entry_id FROM kb_staging WHERE fingerprint=?', (fp,)).fetchone():
            skipped += 1
            continue
        dst.execute(
            """INSERT INTO kb_staging
               (module, title, content, src_id, category, keywords, summary,
                raw_metadata, status, tags, confidence, source_ids, fingerprint, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                'epb-violation', title, content, src_id, 'epb-violation',
                f"环保,违规,类型,{row['category']},{vname}",
                f"{row['category']}-{vname}",
                json.dumps({'violation_id': row['id'], 'category': row['category'], 'sub_type': row['sub_type'], 'risk_level': row['risk_level']}),
                'staged', f"环保违规,{row['category']},{vname}", 0.85,
                json.dumps([src_id]), fp, now, now
            )
        )
        synced += 1
    return synced, skipped, len(vts)

def main():
    if not os.path.exists(SRC_DB):
        print(f'✗ 源数据库不存在: {SRC_DB}')
        sys.exit(1)

    src = sqlite3.connect(SRC_DB)
    dst = sqlite3.connect(DST_DB)
    now = datetime.datetime.now().isoformat()

    src_id = register_source(dst, 'EPB Assistant 移动源监管蒸馏（案例+法规+违规类型）', 0.85)
    dst.commit()
    print(f'✓ Source: {src_id}')

    c_synced, c_skipped, c_total = distill_cases(src, dst, src_id)
    print(f'✓ 案例蒸馏: {c_synced} 新增 / {c_skipped} 跳过 / {c_total} 总计')

    l_synced, l_skipped, l_total = distill_laws(src, dst, src_id)
    print(f'✓ 法规蒸馏: {l_synced} 新增 / {l_skipped} 跳过 / {l_total} 总计')

    v_synced, v_skipped, v_total = distill_violations(src, dst, src_id)
    print(f'✓ 违规类型蒸馏: {v_synced} 新增 / {v_skipped} 跳过 / {v_total} 总计')

    dst.commit()

    total = c_synced + l_synced + v_synced
    print(f'\n=== EPB 蒸馏汇总 ===')
    print(f'  案例: {c_synced} 条')
    print(f'  法规: {l_synced} 条')
    print(f'  违规类型: {v_synced} 条')
    print(f'  总计: {total} 条')

    # FTS5 验证（用 kb_staging_fts 全文索引）
    print(f'\n=== FTS5 验证 ===')
    test_keywords = ['偷排', '罚款', '超标', '危废', '暗管']
    for kw in test_keywords:
        hits = dst.execute(
            "SELECT COUNT(*) FROM kb_staging_fts WHERE kb_staging_fts MATCH ?", (kw,)
        ).fetchone()[0]
        print(f'  MATCH "{kw}": {hits} 命中')

    backup_dir = '/Users/tom/.openclaw-autoclaw/workspace/projects/mingli-baojian/data/backups'
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = f'{backup_dir}/yidao-epb-{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.db'
    import shutil
    shutil.copy(DST_DB, backup_path)
    print(f'\n✓ 备份: {backup_path}')

    src.close()
    dst.close()

if __name__ == '__main__':
    main()