#!/usr/bin/env python3
"""
EPB Assistant → 自有 KB 蒸馏脚本
R118-G3 修真（2026-08-16）：反向污染修真

原行为：EPB 案例 → 命理宝鉴 mingli 主 KB（反向污染）
修真行为：EPB 案例 → epb-assistant 自有 KB（kb_formal）

修真原因：违反 KNOWLEDGE_DISTILLATION_SOP 单向流动原则
        - epb-assistant 是独立业务项目（环保执法），不是命理项目
        - 环保知识属于 epb-assistant 自己的知识域
        - 修真后所有 epb 知识写到 epb-assistant/db/epb.db 的 kb_formal 表

输出位置：epb-assistant/db/epb.db (kb_formal 表)
"""

import sqlite3
import json
import datetime
import hashlib
import os
import sys

# R118-G3 修真：DST_DB 从 mingli 改为 epb 自身
DST_DB = '/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/db/epb.db'
SRC_DB = '/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/db/epb.db'

# R118-G3 修真：使用项目自有 module 标识（前缀环境保护）
MODULE_PREFIX = 'epb-'


def register_source(dst, title, trust=0.85):
    """在 source_index 登记来源（R118-G3 修真：限定 epb 域）"""
    now = datetime.datetime.now().isoformat()
    src_id = f'SRC-EPB-{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}'
    try:
        dst.execute(
            "INSERT INTO source_index (src_id, src_type, title, author, url, trust_score, tags, access_level, created_at, path, format, size_bytes, module) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (src_id, 'SRC-DISTILL-EPB', title, 'epb-assistant-distill',
             'projects/epb-assistant/scripts/distill-epb-to-kb.py', trust,
             'environmental,law,case,violation,compliance', 'internal', now,
             'projects/epb-assistant/', 'sqlite', os.path.getsize(SRC_DB), 'epb-assistant')
        )
    except sqlite3.OperationalError:
        # R118-G3 修真：epb.db 可能没有 source_index 表（如该表设计在 mingli 模式），跳过
        pass
    return src_id


def kb_formal_exists(dst, fp):
    """检查自有 kb_formal 是否已有该指纹"""
    try:
        return dst.execute('SELECT entry_id FROM kb_formal WHERE fingerprint=?', (fp,)).fetchone()
    except sqlite3.OperationalError:
        return None


def insert_kb_formal(dst, src_id, title, content, category, tags, trust, now):
    """R118-G3 修真：写入 epb 自有 kb_formal"""
    fp = hashlib.sha256(content.encode()).hexdigest()[:16]
    if kb_formal_exists(dst, fp):
        return False
    try:
        dst.execute(
            'INSERT INTO kb_formal (module, title, content, src_id, category, keywords, summary, raw_metadata, status, tags, confidence, source_ids, fingerprint, created_at, updated_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (f'{MODULE_PREFIX}case', title, content, src_id, category,
             tags, '', '{}', 'staged', tags, trust, src_id, fp, now, now)
        )
        return True
    except sqlite3.OperationalError as e:
        print(f'[warn] kb_formal 插入跳过: {e}')
        return False


def distill_cases(src, dst, src_id):
    """蒸馏 EPB 案例库"""
    src.row_factory = sqlite3.Row
    cases = src.execute('SELECT * FROM cases ORDER BY date DESC').fetchall()
    now = datetime.datetime.now().isoformat()
    total = 0
    for row in cases:
        title = f'[{row.get("type", "案例")}] {row.get("party", "未知当事人")[:40]}'
        content = f"""# {title}

- **当事人**: {row.get('party', '')}
- **类型**: {row.get('type', '')}
- **来源**: {row.get('source', '')}
- **状态**: {row.get('status', '')}
- **风险等级**: {row.get('risk_level', '')}

## 案情事实
{row.get('fact', '')}

## 处罚结果
{row.get('result', '')}

---
*来源: epb-assistant 案例库 · trust=0.85*
"""
        if insert_kb_formal(dst, src_id, title, content, 'environmental-case',
                           '环保,案例,执法', 0.85, now):
            total += 1
    return total


def distill_laws(src, dst, src_id):
    """蒸馏环保法规"""
    src.row_factory = sqlite3.Row
    try:
        laws = src.execute('SELECT * FROM laws').fetchall()
    except sqlite3.OperationalError:
        return 0
    now = datetime.datetime.now().isoformat()
    total = 0
    for row in laws:
        title = f'[法规] {row.get("name", "")[:80]}'
        content = f"""# {title}

- **法规名称**: {row.get('name', '')}
- **类别**: {row.get('category', '')}
- **效力**: {row.get('effective', '')}

## 条款
{row.get('content', '')}

---
*来源: epb-assistant 法规库 · trust=0.85*
"""
        if insert_kb_formal(dst, src_id, title, content, 'environmental-law',
                           '环保,法规', 0.85, now):
            total += 1
    return total


def main():
    if not os.path.exists(SRC_DB):
        print(f'源库不存在: {SRC_DB}，跳过')
        return
    print(f'[R118-G3] epb-assistant 自蒸馏 → {DST_DB}')
    src = sqlite3.connect(SRC_DB)
    dst = sqlite3.connect(DST_DB)
    src_id = register_source(dst, 'epb-assistant 自有 KB 蒸馏', 0.85)
    total = 0
    total += distill_cases(src, dst, src_id)
    total += distill_laws(src, dst, src_id)
    dst.commit()
    src.close()
    dst.close()
    print(f'✓ epb-assistant 自蒸馏: {total} 条 (src: {src_id})')
    print(f'  写入目标: {DST_DB} (kb_formal)')
    print(f'  R118-G3 修真：已停止向 mingli 主 KB 写入，改为写入 epb 自身 KB')


if __name__ == '__main__':
    main()
