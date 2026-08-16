#!/usr/bin/env python3
"""
从 epb.db 把数据导出到 JSON 文件，让 file_server 的 API 能读到完整数据
"""
import sqlite3, json, os, sys

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'epb.db')
DB_DIR = os.path.dirname(DB)


def rows_to_dicts(cursor):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def export_table(name, json_name=None):
    json_name = json_name or name
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = rows_to_dicts(conn.execute(f'SELECT * FROM {name}'))
    conn.close()

    out_path = os.path.join(DB_DIR, f'{json_name}.json')

    # 已有JSON结构（包壳），只在 enterprises / law_index 等使用
    if json_name == 'enterprises' and os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            shell = json.load(f)
        shell['enterprises'] = rows
        shell['updated'] = '2026-07-21'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(shell, f, ensure_ascii=False, indent=2)
        print(f'  {json_name}.json: 合并 {len(rows)} 条到壳')
    elif json_name == 'devices' and os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            shell = json.load(f)
        shell['devices'] = rows
        shell['updated'] = '2026-07-21'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(shell, f, ensure_ascii=False, indent=2)
        print(f'  {json_name}.json: 合并 {len(rows)} 条到壳')
    elif json_name == 'law_index' and os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            shell = json.load(f)
        shell['laws'] = rows
        shell['updated'] = '2026-07-21'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(shell, f, ensure_ascii=False, indent=2)
        print(f'  {json_name}.json: 合并 {len(rows)} 条到壳')
    else:
        # 直接写列表
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print(f'  {json_name}.json: 写入 {len(rows)} 条')

    return len(rows)


def main():
    print('=== 从 DB 导出到 JSON ===')
    counts = {}
    counts['enterprises'] = export_table('enterprises')
    counts['devices'] = export_table('devices')
    counts['cases'] = export_table('cases')
    counts['users'] = export_table('users')
    counts['laws'] = export_table('laws', 'law_index')
    print('')
    print(f'  ✅ 导出完成')

if __name__ == '__main__':
    main()