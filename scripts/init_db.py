#!/usr/bin/env python3
"""
环保智能体平台 — SQLite 数据库初始化与数据迁移脚本
将所有 JSON 文件数据迁移到结构化数据库，后续 API 读写全部走数据库。
"""

import os, json, sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'db')
DB_FILE = os.path.join(DB_DIR, 'epb.db')

def load_json(name):
    path = os.path.join(DB_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def init_db():
    """创建所有表结构"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    c = conn.cursor()

    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        role_name TEXT,
        role_icon TEXT,
        org TEXT,
        permissions TEXT,
        registered_at TEXT,
        last_login TEXT
    )''')

    # 角色配置表
    c.execute('''CREATE TABLE IF NOT EXISTS roles (
        role_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        icon TEXT,
        description TEXT,
        modules TEXT,
        checklist TEXT,
        permissions TEXT,
        org_required INTEGER DEFAULT 1,
        org_label TEXT,
        org_placeholder TEXT
    )''')

    # 案例表
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        date TEXT,
        title TEXT NOT NULL,
        party TEXT,
        type TEXT,
        source TEXT,
        fact TEXT,
        law TEXT,
        result TEXT,
        status TEXT,
        tags TEXT,
        risk_level TEXT,
        criminal INTEGER DEFAULT 0,
        fetched_at TEXT
    )''')

    # 法规表
    c.execute('''CREATE TABLE IF NOT EXISTS laws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        law_name TEXT NOT NULL,
        article TEXT,
        full_text TEXT,
        bracket TEXT,
        case_count INTEGER DEFAULT 0,
        total_articles INTEGER DEFAULT 0,
        updated TEXT
    )''')

    # 违法类型映射表
    c.execute('''CREATE TABLE IF NOT EXISTS violation_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        sub_type TEXT NOT NULL,
        violations TEXT,
        penalties TEXT,
        criminal_threshold TEXT,
        criminal_law TEXT,
        criminal_sentence TEXT,
        evidence TEXT,
        measures TEXT,
        risk_level TEXT,
        keywords TEXT,
        discretion TEXT
    )''')

    # 举报表
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        reporter_name TEXT,
        reporter_phone TEXT,
        anonymous INTEGER DEFAULT 0,
        target_company TEXT,
        target_address TEXT,
        type TEXT,
        description TEXT,
        location_province TEXT,
        location_city TEXT,
        location_district TEXT,
        location_detail TEXT,
        images TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        updated_at TEXT,
        notes TEXT
    )''')

    # 任务表
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        type TEXT,
        source TEXT,
        target TEXT,
        content TEXT,
        deadline TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'pending',
        assigned_to TEXT,
        logs TEXT,
        evidence TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')

    # 设备表
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT,
        vendor TEXT,
        model TEXT,
        serial_no TEXT,
        assigned_to TEXT,
        status TEXT DEFAULT 'offline',
        battery INTEGER DEFAULT 0,
        storage_free INTEGER DEFAULT 0,
        temperature REAL DEFAULT 0,
        config TEXT,
        registered_at TEXT,
        last_active TEXT
    )''')

    # 设备数据日志表
    c.execute('''CREATE TABLE IF NOT EXISTS device_data_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        device_type TEXT,
        battery INTEGER,
        storage INTEGER,
        data TEXT,
        received_at TEXT
    )''')

    # 企业表
    c.execute('''CREATE TABLE IF NOT EXISTS enterprises (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT,
        address TEXT,
        lng REAL,
        lat REAL,
        permit_no TEXT,
        pollutants TEXT,
        monitoring_points TEXT,
        contact_person TEXT,
        contact_phone TEXT,
        credit_level TEXT,
        risk_level TEXT,
        last_check_date TEXT,
        status TEXT
    )''')

    # 监测站点表
    c.execute('''CREATE TABLE IF NOT EXISTS stations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT,
        enterprise_id TEXT,
        location TEXT,
        lng REAL,
        lat REAL,
        indicators TEXT,
        device_model TEXT,
        status TEXT DEFAULT 'offline',
        last_data_time TEXT
    )''')

    # 知识图谱表
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge_graph (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        sub_category TEXT,
        content TEXT,
        laws TEXT,
        description TEXT
    )''')

    # 培训场景表
    c.execute('''CREATE TABLE IF NOT EXISTS training_scenarios (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        icon TEXT,
        type TEXT,
        description TEXT,
        opening TEXT,
        responses TEXT
    )''')

    # 审计日志表
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_phone TEXT,
        action TEXT,
        target TEXT,
        detail TEXT,
        ip_address TEXT,
        created_at TEXT
    )''')

    conn.commit()
    print('✅ 数据库表结构创建完成')
    return conn

def migrate_data(conn):
    """从 JSON 文件迁移数据到数据库"""
    c = conn.cursor()

    # 1. 迁移用户
    users_data = load_json('users.json')
    if users_data and users_data.get('users'):
        for u in users_data['users']:
            try:
                c.execute('''INSERT OR REPLACE INTO users 
                    (phone, name, role, role_name, role_icon, org, permissions, registered_at, last_login)
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                    (u.get('phone',''), u.get('name',''), u.get('role',''),
                     u.get('roleName',''), u.get('roleIcon',''), u.get('org',''),
                     json.dumps(u.get('permissions',[]), ensure_ascii=False),
                     u.get('registeredAt',''), u.get('lastLogin','')))
            except Exception as e:
                print(f'  ⚠️ 用户迁移: {e}')
        print(f'  ✅ 用户: {len(users_data["users"])} 条')

    # 2. 迁移角色配置
    if users_data and users_data.get('roles'):
        for rid, r in users_data['roles'].items():
            try:
                c.execute('''INSERT OR REPLACE INTO roles
                    (role_id, name, icon, description, modules, checklist, permissions, org_required, org_label, org_placeholder)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (rid, r.get('name',''), r.get('icon',''), r.get('desc',''),
                     json.dumps(r.get('modules',[]), ensure_ascii=False),
                     json.dumps(r.get('checklist',[]), ensure_ascii=False),
                     json.dumps(r.get('permissions',[]), ensure_ascii=False),
                     1 if r.get('org_required') else 0,
                     r.get('org_label',''), r.get('org_placeholder','')))
            except Exception as e:
                print(f'  ⚠️ 角色迁移: {e}')
        print(f'  ✅ 角色: {len(users_data["roles"])} 条')

    # 3. 迁移案例
    cases_data = load_json('cases.json')
    if cases_data:
        for case in cases_data:
            try:
                c.execute('''INSERT OR REPLACE INTO cases
                    (id, date, title, party, type, source, fact, law, result, status, tags, risk_level, criminal, fetched_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (case.get('id',''), case.get('date',''), case.get('title',''),
                     case.get('party',''), case.get('type',''), case.get('source',''),
                     case.get('fact',''), json.dumps(case.get('law',[]), ensure_ascii=False),
                     case.get('result',''), case.get('status',''),
                     json.dumps(case.get('tags',[]), ensure_ascii=False),
                     case.get('risk_level',''), 1 if case.get('criminal') else 0,
                     case.get('fetchedAt','')))
            except Exception as e:
                print(f'  ⚠️ 案例迁移 {case.get("id","")}: {e}')
        print(f'  ✅ 案例: {len(cases_data)} 条')

    # 4. 迁移法规
    law_data = load_json('law_index.json')
    if law_data and law_data.get('laws'):
        count = 0
        for law_name, law_info in law_data['laws'].items():
            for prov in law_info.get('provisions', []):
                try:
                    c.execute('''INSERT INTO laws
                        (law_name, article, full_text, bracket, case_count, total_articles, updated)
                        VALUES (?,?,?,?,?,?,?)''',
                        (law_name, prov.get('article',''), prov.get('full',''),
                         prov.get('bracket',''), prov.get('case_count',0),
                         law_info.get('total_articles',0), law_data.get('updated','')))
                    count += 1
                except Exception as e:
                    pass
        print(f'  ✅ 法规: {count} 条')

    # 5. 迁移违法映射
    mapping_data = load_json('law_mapping.json')
    if mapping_data and mapping_data.get('violation_types'):
        count = 0
        for cat, subtypes in mapping_data['violation_types'].items():
            for sub_type, v in subtypes.items():
                try:
                    crim = v.get('criminal', {})
                    c.execute('''INSERT INTO violation_types
                        (category, sub_type, violations, penalties, criminal_threshold, criminal_law,
                         criminal_sentence, evidence, measures, risk_level, keywords, discretion)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (cat, sub_type,
                         json.dumps(v.get('violations',[]), ensure_ascii=False),
                         json.dumps(v.get('penalties',[]), ensure_ascii=False),
                         crim.get('threshold',''), crim.get('law',''), crim.get('sentence',''),
                         json.dumps(v.get('evidence',[]), ensure_ascii=False),
                         json.dumps(v.get('measures',[]), ensure_ascii=False),
                         v.get('risk_level',''),
                         json.dumps(v.get('keywords',[]), ensure_ascii=False),
                         json.dumps(v.get('discretion',{}), ensure_ascii=False)))
                    count += 1
                except Exception as e:
                    pass
        print(f'  ✅ 违法映射: {count} 条')

    # 6. 迁移举报
    reports_data = load_json('reports.json')
    if reports_data:
        for r in reports_data:
            try:
                reporter = r.get('reporter', {})
                target = r.get('target', {})
                location = r.get('location', {})
                c.execute('''INSERT OR REPLACE INTO reports
                    (id, reporter_name, reporter_phone, anonymous, target_company, target_address,
                     type, description, location_province, location_city, location_district, location_detail,
                     images, status, created_at, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (r.get('id',''), reporter.get('name',''), reporter.get('phone',''),
                     1 if reporter.get('anonymous') else 0,
                     target.get('company',''), target.get('address',''),
                     r.get('type',''), r.get('description',''),
                     location.get('province',''), location.get('city',''),
                     location.get('district',''), location.get('detail',''),
                     json.dumps(r.get('images',[]), ensure_ascii=False),
                     r.get('status','pending'), r.get('created_at',''), r.get('updated_at','')))
            except Exception as e:
                pass
        print(f'  ✅ 举报: {len(reports_data)} 条')

    # 7. 迁移任务
    tasks_data = load_json('tasks.json')
    if tasks_data:
        for t in tasks_data:
            try:
                c.execute('''INSERT OR REPLACE INTO tasks
                    (id, title, type, source, target, content, deadline, priority, status,
                     assigned_to, logs, evidence, created_at, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (t.get('id',''), t.get('title',''), t.get('type',''),
                     t.get('source',''), t.get('target',''), t.get('content',''),
                     t.get('deadline',''), t.get('priority','medium'),
                     t.get('status','pending'), t.get('assigned_to',''),
                     json.dumps(t.get('logs',[]), ensure_ascii=False),
                     json.dumps(t.get('evidence',[]), ensure_ascii=False),
                     t.get('created_at',''), t.get('updated_at','')))
            except Exception as e:
                pass
        print(f'  ✅ 任务: {len(tasks_data)} 条')

    # 8. 迁移设备
    dev_data = load_json('devices.json')
    if dev_data and dev_data.get('devices'):
        for d in dev_data.get('devices', []):
            try:
                health = d.get('health', {})
                c.execute('''INSERT OR REPLACE INTO devices
                    (id, name, type, vendor, model, serial_no, assigned_to, status,
                     battery, storage_free, temperature, config, registered_at, last_active)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (d.get('id',''), d.get('name',''), d.get('type',''),
                     d.get('vendor',''), d.get('model',''), d.get('serial_no',''),
                     d.get('assigned_to',''), d.get('status','offline'),
                     health.get('battery',0), health.get('storage_free',0),
                     health.get('temperature',0),
                     json.dumps(d.get('config',{}), ensure_ascii=False),
                     d.get('registered_at',''), d.get('last_active','')))
            except Exception as e:
                pass
        print(f'  ✅ 设备: {len(dev_data["devices"])} 条')

    # 9. 迁移企业
    ent_data = load_json('enterprises.json')
    if ent_data and ent_data.get('enterprises'):
        for e in ent_data['enterprises']:
            try:
                c.execute('''INSERT OR REPLACE INTO enterprises
                    (id, name, type, address, lng, lat, permit_no, pollutants,
                     monitoring_points, contact_person, contact_phone, credit_level,
                     risk_level, last_check_date, status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (e.get('id',''), e.get('name',''), e.get('type',''),
                     e.get('address',''), e.get('lng',0), e.get('lat',0),
                     e.get('permit_no',''),
                     json.dumps(e.get('pollutants',[]), ensure_ascii=False),
                     json.dumps(e.get('monitoring_points',[]), ensure_ascii=False),
                     e.get('contact_person',''), e.get('contact_phone',''),
                     e.get('credit_level',''), e.get('risk_level',''),
                     e.get('last_check_date',''), e.get('status','')))
            except Exception as ex:
                pass
        print(f'  ✅ 企业: {len(ent_data["enterprises"])} 条')

    # 10. 迁移监测站点
    st_data = load_json('stations.json')
    if st_data and st_data.get('stations'):
        for s in st_data['stations']:
            try:
                c.execute('''INSERT OR REPLACE INTO stations
                    (id, name, type, enterprise_id, location, lng, lat, indicators,
                     device_model, status, last_data_time)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                    (s.get('id',''), s.get('name',''), s.get('type',''),
                     s.get('enterprise_id',''), s.get('location',''),
                     s.get('lng',0), s.get('lat',0),
                     json.dumps(s.get('indicators',[]), ensure_ascii=False),
                     s.get('device_model',''), s.get('status','offline'),
                     s.get('last_data_time','')))
            except Exception as e:
                pass
        print(f'  ✅ 监测站点: {len(st_data["stations"])} 条')

    conn.commit()
    return conn

def verify_migration(conn):
    """验证迁移结果"""
    c = conn.cursor()
    tables = ['users', 'roles', 'cases', 'laws', 'violation_types', 'reports',
              'tasks', 'devices', 'enterprises', 'stations', 'device_data_log', 'audit_log']
    print('\n=== 数据库验证 ===')
    total = 0
    for t in tables:
        c.execute(f'SELECT COUNT(*) FROM {t}')
        n = c.fetchone()[0]
        total += n
        print(f'  {t}: {n} 条')
    print(f'  总计: {total} 条')
    return total

if __name__ == '__main__':
    print('========== 环保智能体平台 — 数据库初始化 ==========\n')
    conn = init_db()
    print('\n--- 数据迁移 ---')
    migrate_data(conn)
    verify_migration(conn)
    conn.close()
    print(f'\n✅ 数据库已创建: {DB_FILE}')
    print(f'   文件大小: {os.path.getsize(DB_FILE)} bytes')
