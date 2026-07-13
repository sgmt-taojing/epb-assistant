#!/usr/bin/env python3
"""
环保智能体平台 — 数据库访问层 (DAL)
所有 API 通过此模块读写数据库，不再直接操作 JSON 文件。
"""

import os, json, sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, 'db', 'epb.db')

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def to_json(obj):
    return json.dumps(obj, ensure_ascii=False)

def from_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except:
        return text

# ============ 用户 ============
def db_register_user(user_data):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    phone = user_data.get('phone', '')
    # 检查是否已存在
    c.execute('SELECT id FROM users WHERE phone=?', (phone,))
    existing = c.fetchone()
    if existing:
        c.execute('''UPDATE users SET name=?, role=?, role_name=?, role_icon=?, org=?,
            permissions=?, last_login=? WHERE phone=?''',
            (user_data.get('name',''), user_data.get('role',''),
             user_data.get('roleName',''), user_data.get('roleIcon',''),
             user_data.get('org',''),
             to_json(user_data.get('permissions',[])),
             now, phone))
        conn.commit()
        result = {'ok': True, 'message': '登录成功(已注册用户)', 'user': _row_to_user(c, phone)}
    else:
        c.execute('''INSERT INTO users
            (phone, name, role, role_name, role_icon, org, permissions, registered_at, last_login)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (phone, user_data.get('name',''), user_data.get('role',''),
             user_data.get('roleName',''), user_data.get('roleIcon',''),
             user_data.get('org',''),
             to_json(user_data.get('permissions',[])),
             now, now))
        conn.commit()
        result = {'ok': True, 'message': '注册成功', 'user': _row_to_user(c, phone)}
    conn.close()
    result['userCount'] = db_user_count()
    return result

def db_login_user(phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=?', (phone,))
    row = c.fetchone()
    if row:
        now = datetime.now().isoformat()
        c.execute('UPDATE users SET last_login=? WHERE phone=?', (now, phone))
        conn.commit()
        user = {
            'role': row['role'], 'roleName': row['role_name'],
            'roleIcon': row['role_icon'], 'name': row['name'],
            'org': row['org'], 'phone': row['phone'],
            'permissions': from_json(row['permissions']) or [],
            'registeredAt': row['registered_at']
        }
        conn.close()
        return {'ok': True, 'message': '登录成功', 'user': user}
    conn.close()
    return {'ok': False, 'message': '该手机号尚未注册，请先注册账号'}

def db_list_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY registered_at DESC')
    rows = c.fetchall()
    users = []
    for row in rows:
        phone = row['phone']
        masked = phone[:3] + '****' + phone[-4:] if len(phone) >= 11 else phone
        users.append({
            'role': row['role'], 'roleName': row['role_name'],
            'roleIcon': row['role_icon'], 'name': row['name'],
            'org': row['org'], 'phoneMasked': masked,
            'permissions': from_json(row['permissions']) or [],
            'registeredAt': row['registered_at'], 'lastLogin': row['last_login']
        })
    conn.close()
    return {'ok': True, 'users': users, 'total': len(users)}

def db_user_count():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    n = c.fetchone()[0]
    conn.close()
    return n

def _row_to_user(c, phone):
    c.execute('SELECT * FROM users WHERE phone=?', (phone,))
    row = c.fetchone()
    if not row:
        return {}
    return {
        'role': row['role'], 'roleName': row['role_name'],
        'roleIcon': row['role_icon'], 'name': row['name'],
        'org': row['org'], 'phone': row['phone'],
        'permissions': from_json(row['permissions']) or []
    }

# ============ 案例 ============
def db_list_cases(limit=50, case_type=None):
    conn = get_conn()
    c = conn.cursor()
    if case_type and case_type != 'all':
        c.execute('SELECT * FROM cases WHERE type=? ORDER BY date DESC LIMIT ?', (case_type, limit))
    else:
        c.execute('SELECT * FROM cases ORDER BY date DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    cases = [_row_to_case(row) for row in rows]
    conn.close()
    return {'cases': cases, 'total': len(cases)}

def db_search_cases(keyword, case_type=None, limit=10):
    conn = get_conn()
    c = conn.cursor()
    kw = f'%{keyword}%'
    if case_type:
        c.execute('''SELECT * FROM cases WHERE type=? AND (title LIKE ? OR fact LIKE ?)
            ORDER BY date DESC LIMIT ?''', (case_type, kw, kw, limit))
    else:
        c.execute('''SELECT * FROM cases WHERE title LIKE ? OR fact LIKE ?
            ORDER BY date DESC LIMIT ?''', (kw, kw, limit))
    rows = c.fetchall()
    cases = [_row_to_case(row) for row in rows]
    conn.close()
    return cases

def _row_to_case(row):
    return {
        'id': row['id'], 'date': row['date'], 'title': row['title'],
        'party': row['party'], 'type': row['type'], 'source': row['source'],
        'fact': row['fact'], 'law': from_json(row['law']) or [],
        'result': row['result'], 'status': row['status'],
        'tags': from_json(row['tags']) or [],
        'risk_level': row['risk_level'],
        'criminal': bool(row['criminal']),
        'fetchedAt': row['fetched_at']
    }

def db_case_count():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM cases')
    n = c.fetchone()[0]
    conn.close()
    return n

# ============ 举报 ============
def db_create_report(data):
    conn = get_conn()
    c = conn.cursor()
    today = datetime.now().strftime('%Y%m%d')
    c.execute(f"SELECT COUNT(*) FROM reports WHERE id LIKE 'RPT-{today}%'")
    count = c.fetchone()[0]
    rpt_id = f'RPT-{today}-{count+1:03d}'
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reporter = data.get('reporter', {}) if isinstance(data.get('reporter'), dict) else {}
    target = data.get('target', {}) if isinstance(data.get('target'), dict) else {}
    location = data.get('location', {}) if isinstance(data.get('location'), dict) else {}
    # 兼容扁平结构：location为字符串时放入detail
    if isinstance(data.get('location'), str):
        location = {'detail': data.get('location', '')}
    if not reporter and data.get('phone'):
        reporter = {'phone': data.get('phone', ''), 'name': data.get('name', '')}
    if not target and data.get('company'):
        target = {'company': data.get('company', ''), 'address': data.get('address', '')}
    c.execute('''INSERT INTO reports
        (id, reporter_name, reporter_phone, anonymous, target_company, target_address,
         type, description, location_province, location_city, location_district, location_detail,
         images, status, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (rpt_id, reporter.get('name',''), reporter.get('phone',''),
         1 if reporter.get('anonymous') else 0,
         target.get('company',''), target.get('address',''),
         data.get('type',''), data.get('description',''),
         location.get('province',''), location.get('city',''),
         location.get('district',''), location.get('detail',''),
         to_json(data.get('images',[])),
         'pending', now, now))
    conn.commit()
    conn.close()
    return {'ok': True, 'id': rpt_id, 'message': '举报提交成功', 'created_at': now}

def db_list_reports(phone=None, status=None):
    conn = get_conn()
    c = conn.cursor()
    if phone:
        c.execute('SELECT * FROM reports WHERE reporter_phone=? ORDER BY created_at DESC', (phone,))
    elif status:
        c.execute('SELECT * FROM reports WHERE status=? ORDER BY created_at DESC', (status,))
    else:
        c.execute('SELECT * FROM reports ORDER BY created_at DESC')
    rows = c.fetchall()
    reports = [_row_to_report(row) for row in rows]
    conn.close()
    return {'reports': reports}

def db_update_report(rpt_id, update):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM reports WHERE id=?', (rpt_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {'ok': False, 'error': '举报不存在'}
    new_status = update.get('status', row['status'])
    note = update.get('note', '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('UPDATE reports SET status=?, updated_at=? WHERE id=?', (new_status, now, rpt_id))
    conn.commit()
    conn.close()
    return {'ok': True, 'message': '状态更新成功', 'id': rpt_id, 'status': new_status}

def _row_to_report(row):
    return {
        'id': row['id'],
        'reporter': {'name': row['reporter_name'], 'phone': row['reporter_phone'],
                     'anonymous': bool(row['anonymous'])},
        'target': {'company': row['target_company'], 'address': row['target_address']},
        'type': row['type'], 'description': row['description'],
        'location': {'province': row['location_province'], 'city': row['location_city'],
                     'district': row['location_district'], 'detail': row['location_detail']},
        'images': from_json(row['images']) or [],
        'status': row['status'],
        'created_at': row['created_at'], 'updated_at': row['updated_at']
    }

def db_report_count():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM reports')
    n = c.fetchone()[0]
    conn.close()
    return n

# ============ 任务 ============
def db_create_task(data):
    conn = get_conn()
    c = conn.cursor()
    today = datetime.now().strftime('%Y%m%d')
    c.execute(f"SELECT COUNT(*) FROM tasks WHERE id LIKE 'TASK-{today}%'")
    count = c.fetchone()[0]
    task_id = f'TASK-{today}-{count+1:03d}'
    now = datetime.now().isoformat()
    log_entry = {'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'actor': '系统', 'action': '创建任务', 'note': data.get('title','')}
    c.execute('''INSERT INTO tasks
        (id, title, type, source, target, content, deadline, priority, status,
         assigned_to, logs, evidence, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (task_id, data.get('title',''), data.get('type',''),
         data.get('source','环保局'), data.get('target',''),
         data.get('content',''), data.get('deadline',''),
         data.get('priority','medium'), 'pending', data.get('assigned_to',''),
         to_json([log_entry]), to_json([]), now, now))
    conn.commit()
    conn.close()
    return {'success': True, 'data': {'id': task_id, 'title': data.get('title',''),
            'type': data.get('type',''), 'status': 'pending'}}

def db_list_tasks():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = c.fetchall()
    tasks = [_row_to_task(row) for row in rows]
    conn.close()
    return tasks

def db_update_task(task_id, update):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id=?', (task_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {'success': False, 'error': '任务不存在'}
    new_status = update.get('status', row['status'])
    now = datetime.now().isoformat()
    logs = from_json(row['logs']) or []
    logs.append({'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'actor': '系统', 'action': f'状态变更为{new_status}',
                 'note': update.get('note','')})
    c.execute('UPDATE tasks SET status=?, logs=?, updated_at=? WHERE id=?',
              (new_status, to_json(logs), now, task_id))
    conn.commit()
    conn.close()
    return {'success': True, 'data': {'id': task_id, 'status': new_status}}

def _row_to_task(row):
    return {
        'id': row['id'], 'title': row['title'], 'type': row['type'],
        'source': row['source'], 'target': row['target'],
        'content': row['content'], 'deadline': row['deadline'],
        'priority': row['priority'], 'status': row['status'],
        'assigned_to': row['assigned_to'],
        'logs': from_json(row['logs']) or [],
        'evidence': from_json(row['evidence']) or [],
        'created_at': row['created_at'], 'updated_at': row['updated_at']
    }

def db_task_count():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM tasks')
    n = c.fetchone()[0]
    conn.close()
    return n

# ============ 设备 ============
def db_list_devices():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM devices ORDER BY registered_at DESC')
    rows = c.fetchall()
    devices = [_row_to_device(row) for row in rows]
    conn.close()
    return devices

def db_register_device(device):
    conn = get_conn()
    c = conn.cursor()
    dev_id = device.get('id','')
    if not dev_id:
        today = datetime.now().strftime('%Y%m%d')
        c.execute(f"SELECT COUNT(*) FROM devices WHERE id LIKE 'DEV-{today}%'")
        count = c.fetchone()[0]
        dev_id = f'DEV-{today}-{count+1:03d}'
        device['id'] = dev_id
        device['registered_at'] = datetime.now().strftime('%Y-%m-%d')
    c.execute('''INSERT OR REPLACE INTO devices
        (id, name, type, vendor, model, serial_no, assigned_to, status,
         battery, storage_free, temperature, config, registered_at, last_active)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (dev_id, device.get('name',''), device.get('type',''),
         device.get('vendor',''), device.get('model',''),
         device.get('serial_no',''), device.get('assigned_to',''),
         device.get('status','offline'),
         device.get('health',{}).get('battery',100),
         device.get('health',{}).get('storage_free',0),
         device.get('health',{}).get('temperature',25),
         to_json(device.get('config',{})),
         device.get('registered_at',''), device.get('last_active','')))
    conn.commit()
    conn.close()
    return {'ok': True, 'device': device, 'total': db_device_count()}

def db_device_data(report):
    conn = get_conn()
    c = conn.cursor()
    dev_id = report.get('device_id','')
    now = datetime.now().isoformat()
    # 更新设备状态
    c.execute('SELECT * FROM devices WHERE id=? OR serial_no=?', (dev_id, dev_id))
    row = c.fetchone()
    if row:
        c.execute('''UPDATE devices SET status='online', battery=?, storage_free=?,
            last_active=? WHERE id=?''',
            (report.get('battery', row['battery']),
             report.get('storage', row['storage_free']),
             now, row['id']))
    # 记录数据
    c.execute('''INSERT INTO device_data_log
        (device_id, device_type, battery, storage, data, received_at)
        VALUES (?,?,?,?,?,?)''',
        (dev_id, report.get('type',''),
         report.get('battery',0), report.get('storage',0),
         to_json(report.get('data',{})), now))
    conn.commit()
    c.execute('SELECT COUNT(*) FROM device_data_log')
    total = c.fetchone()[0]
    conn.close()
    return {'ok': True, 'received': True, 'total_logs': total}

def db_device_count():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM devices')
    n = c.fetchone()[0]
    conn.close()
    return n

def _row_to_device(row):
    return {
        'id': row['id'], 'name': row['name'], 'type': row['type'],
        'vendor': row['vendor'], 'model': row['model'],
        'serial_no': row['serial_no'], 'assigned_to': row['assigned_to'],
        'status': row['status'],
        'health': {'battery': row['battery'], 'storage_free': row['storage_free'],
                   'temperature': row['temperature'], 'last_report': row['last_active']},
        'config': from_json(row['config']) or {},
        'registered_at': row['registered_at'], 'last_active': row['last_active']
    }

# ============ 统计 ============
def db_stats():
    conn = get_conn()
    c = conn.cursor()
    stats = {}
    for table in ['cases', 'laws', 'violation_types', 'reports', 'tasks', 'devices', 'users']:
        c.execute(f'SELECT COUNT(*) FROM {table}')
        stats[table] = c.fetchone()[0]
    conn.close()
    return stats

# ============ 角色 ============
def db_get_roles():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM roles')
    rows = c.fetchall()
    roles = {}
    for row in rows:
        roles[row['role_id']] = {
            'name': row['name'], 'icon': row['icon'], 'desc': row['description'],
            'modules': from_json(row['modules']) or [],
            'checklist': from_json(row['checklist']) or [],
            'permissions': from_json(row['permissions']) or [],
            'org_required': bool(row['org_required']),
            'org_label': row['org_label'], 'org_placeholder': row['org_placeholder']
        }
    conn.close()
    return roles

# ============ 审计日志 ============
def db_audit_log(user_phone, action, target='', detail=''):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''INSERT INTO audit_log (user_phone, action, target, detail, created_at)
        VALUES (?,?,?,?,?)''', (user_phone, action, target, detail, now))
    conn.commit()
    conn.close()
