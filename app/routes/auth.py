"""认证路由 — JWT（HS256）+ 口令哈希

安全基线（2026-08-31 修真）：
1. 移除 admin123 硬编码后门 —— 密码必须走 SHA-256(盐) 哈希比对，绝不存明文
2. SECRET_KEY 不再硬编码 —— 优先读环境变量 EPB_JWT_SECRET，
   缺失时生成随机密钥（单进程内稳定），并打印一次性告警
3. 登录失败统一返回「手机号或密码错误」—— 不泄露用户是否存在（防枚举）
4. Token 过期 24h；verify 失败返回 401
"""
from flask import Blueprint, jsonify, request
import hashlib, time, json, os, secrets, hmac

auth_bp = Blueprint('auth', __name__)

# ---- 密钥管理：环境变量优先，缺失则进程内随机（本地演示安全兜底） ----
_secret_warned = False
def _load_secret():
    global _secret_warned
    env_key = os.environ.get('EPB_JWT_SECRET', '')
    if env_key:
        return env_key.encode('utf-8')
    if not _secret_warned:
        print('[WARN][auth] EPB_JWT_SECRET 未设置，已生成进程内随机密钥（重启后旧 Token 全部失效）。'
              '生产部署请在环境变量或 macOS Keychain 中配置。')
        _secret_warned = True
    return secrets.token_bytes(32)

SECRET_KEY = _load_secret()

# ---- 口令哈希：SHA-256(password + 盐)，盐随机 hex ----
def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f'{salt}${digest}'

def verify_password(password: str, stored: str):
    if not stored or '$' not in stored:
        return False
    salt, _ = stored.split('$', 1)
    expect = hash_password(password, salt)
    return hmac.compare_digest(expect, stored)

def generate_token(user_id, role):
    import base64
    header = base64.urlsafe_b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()).decode().rstrip('=')
    payload_data = {'user_id': user_id, 'role': role, 'exp': int(time.time()) + 86400}
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip('=')
    signature = hmac.new(SECRET_KEY, f'{header}.{payload}'.encode(), hashlib.sha256).hexdigest()
    return f'{header}.{payload}.{signature}'

def verify_token(token):
    if not token or '.' not in token:
        return None
    parts = token.split('.')
    if len(parts) != 3:
        return None
    header, payload, sig = parts
    expected_sig = hmac.new(SECRET_KEY, f'{header}.{payload}'.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None
    import base64
    try:
        payload_data = json.loads(base64.urlsafe_b64decode(payload + '=='))
        if payload_data.get('exp', 0) < time.time():
            return None
        return payload_data
    except Exception:
        return None

def _find_user(conn, username):
    """按手机号或姓名查用户，兼容两套 users 表结构（有/无 username 列）"""
    cols = [c[1] for c in conn.execute('PRAGMA table_info(users)').fetchall()]
    conds = ['phone = ?']
    params = [username, username]
    if 'name' in cols:
        conds.append('name = ?')
    if 'username' in cols:
        conds.append('username = ?')
        params.append(username)
    return conn.execute(
        f"SELECT * FROM users WHERE {' OR '.join(conds)}",
        tuple(params)
    ).fetchone()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or data.get('phone') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({'ok': False, 'message': '请输入账号和密码'}), 400
    if len(username) > 64 or len(password) > 128:
        return jsonify({'ok': False, 'message': '输入过长'}), 400

    from app.models import get_db
    conn = get_db()
    try:
        user = _find_user(conn, username)
    finally:
        conn.close()

    # 统一失败文案，防账号枚举；恒定时间比对避免时序侧信道
    fail = (jsonify({'ok': False, 'message': '手机号或密码错误'}), 401)
    if not user:
        verify_password(password, 'aabbccdd$0000')  # 恒定时间空跑
        return fail
    stored_hash = (user['password_hash'] if 'password_hash' in user.keys() else '') or ''
    if not verify_password(password, stored_hash):
        return fail

    token = generate_token(user['id'], user['role'])
    _keys = user.keys()
    return jsonify({
        'ok': True,
        'token': token,
        'user': {'id': user['id'],
                 'username': (user['name'] if 'name' in _keys and user['name'] else None) or
                             (user['username'] if 'username' in _keys else None),
                 'phone': (user['phone'] if 'phone' in _keys else None),
                 'role': user['role']}
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    phone = (data.get('phone') or data.get('username') or '').strip()
    name = (data.get('name') or '').strip() or phone
    password = (data.get('password') or '').strip()
    role = data.get('role', 'public')
    if not phone:
        return jsonify({'ok': False, 'message': '手机号不能为空'}), 400
    if not password or len(password) < 6:
        return jsonify({'ok': False, 'message': '密码至少 6 位'}), 400
    if len(phone) > 20 or len(name) > 64:
        return jsonify({'ok': False, 'message': '输入过长'}), 400
    if role not in ('public', 'enterprise', 'inspector', 'admin'):
        return jsonify({'ok': False, 'message': '角色不合法'}), 400

    from app.models import get_db
    import uuid
    conn = get_db()
    try:
        existing = conn.execute('SELECT id FROM users WHERE phone = ?', (phone,)).fetchone()
        if existing:
            return jsonify({'ok': False, 'message': '该手机号已注册'}), 409
        user_id = conn.execute(
            'INSERT INTO users (phone, name, role, role_name, role_icon, org, permissions, registered_at, password_hash) '
            'VALUES (?,?,?,?,?,?,?,?,?)',
            (phone, name, role, role, '👥', '个人', '[]', str(int(time.time())), hash_password(password))
        ).lastrowid
        conn.commit()
    finally:
        conn.close()

    token = generate_token(user_id, role)
    return jsonify({'ok': True, 'token': token, 'user': {'id': user_id, 'username': name, 'phone': phone, 'role': role}})

@auth_bp.route('/verify')
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = verify_token(token)
    if payload:
        return jsonify({'ok': True, 'user': payload})
    return jsonify({'ok': False, 'message': 'Token无效或已过期'}), 401
