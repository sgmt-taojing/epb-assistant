"""数据模型 — SQLite + sqlite3 原生（无需ORM）"""
import sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'epb.db')

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
    return conn

def init_db():
    """从 api-data/*.json 导入数据到 SQLite"""
    conn = get_db()
    c = conn.cursor()
    
    # 建表
    tables = [
        '''CREATE TABLE IF NOT EXISTS enterprises (
            id TEXT PRIMARY KEY, name TEXT, type TEXT, address TEXT,
            lng REAL, lat REAL, permit_no TEXT, pollutants TEXT,
            credit_level TEXT, risk_level TEXT, status TEXT,
            contact_person TEXT, contact_phone TEXT,
            last_check_date TEXT, monitoring_points TEXT)''',
        '''CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY, name TEXT, type TEXT, vendor TEXT,
            model TEXT, serial_no TEXT, assigned_to TEXT, status TEXT,
            health TEXT, config TEXT, registered_at TEXT, last_active TEXT)''',
        '''CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY, date TEXT, title TEXT, party TEXT,
            type TEXT, source TEXT, fact TEXT, law TEXT, result TEXT,
            status TEXT, tags TEXT, risk_level TEXT, criminal INTEGER,
            fetchedAt TEXT)''',
        '''CREATE TABLE IF NOT EXISTS laws (
            id TEXT PRIMARY KEY, title TEXT, category TEXT,
            promulgated_by TEXT, effective_date TEXT, content TEXT)''',
        '''CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY, title TEXT, description TEXT,
            status TEXT, assignee TEXT, priority TEXT,
            created_at TEXT, updated_at TEXT)''',
        '''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, username TEXT, password_hash TEXT,
            role TEXT, enterprise_id TEXT, phone TEXT, email TEXT,
            created_at TEXT, last_login TEXT)''',
        '''CREATE TABLE IF NOT EXISTS iot_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT, param TEXT, value REAL,
            timestamp TEXT, quality TEXT,
            unit TEXT DEFAULT '-', standard TEXT DEFAULT '-')''',
        '''CREATE TABLE IF NOT EXISTS standards (
            id TEXT PRIMARY KEY, name TEXT, category TEXT,
            params TEXT)'''
    ]
    for t in tables:
        c.execute(t)
    
    # 导入数据
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'api-data')
    import_map = [
        ('enterprises.json', 'enterprises', ['id','name','type','address','lng','lat','permit_no','pollutants','credit_level','risk_level','status','contact_person','contact_phone','last_check_date','monitoring_points']),
        ('devices.json', 'devices', None),  # 动态处理
        ('cases.json', 'cases', None),
        ('tasks.json', 'tasks', None),
        ('users.json', 'users', None),
    ]
    
    for fname, table, cols in import_map:
        fpath = os.path.join(base, fname)
        if not os.path.isfile(fpath):
            continue
        data = json.load(open(fpath))
        key = list(data.keys())[0] if data else None
        if not key: continue
        rows = data[key]
        if not rows: continue
        
        # 清空表
        c.execute(f'DELETE FROM {table}')
        
        for row in rows:
            # 序列化复杂字段
            for k, v in list(row.items()):
                if isinstance(v, (list, dict)):
                    row[k] = json.dumps(v, ensure_ascii=False)
            cols = list(row.keys())
            placeholders = ','.join(['?' for _ in cols])
            col_names = ','.join(cols)
            values = [row.get(col) for col in cols]
            try:
                c.execute(f'INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})', values)
            except Exception as e:
                pass  # 字段不匹配跳过
    
    conn.commit()
    conn.close()
    print(f'数据库初始化完成: {DB_PATH}')

if __name__ == '__main__':
    init_db()
