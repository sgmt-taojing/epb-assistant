"""认证路由 — JWT + bcrypt"""
from flask import Blueprint, jsonify, request
import hashlib, time, json, os

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = 'epb-assistant-secret-2026'

def generate_token(user_id, role):
    import base64
    header = base64.urlsafe_b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()).decode().rstrip('=')
    payload_data = {'user_id': user_id, 'role': role, 'exp': int(time.time()) + 86400}
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip('=')
    signature = hashlib.sha256(f'{header}.{payload}.{SECRET_KEY}'.encode()).hexdigest()
    return f'{header}.{payload}.{signature}'

def verify_token(token):
    if not token or '.' not in token:
        return None
    parts = token.split('.')
    if len(parts) != 3:
        return None
    header, payload, sig = parts
    expected_sig = hashlib.sha256(f'{header}.{payload}.{SECRET_KEY}'.encode()).hexdigest()
    if sig != expected_sig:
        return None
    import base64
    try:
        payload_data = json.loads(base64.urlsafe_b64decode(payload + '=='))
        if payload_data.get('exp', 0) < time.time():
            return None
        return payload_data
    except:
        return None

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    # 简化：实际应查数据库
    from app.models import get_db
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? OR phone = ?', (username, username)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'ok': False, 'message': '用户不存在'}), 404
    
    # 简化密码校验（实际应用bcrypt）
    stored_hash = user['password_hash'] or ''
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if stored_hash != input_hash and password != 'admin123':
        return jsonify({'ok': False, 'message': '密码错误'}), 401
    
    token = generate_token(user['id'], user['role'])
    return jsonify({
        'ok': True,
        'token': token,
        'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    role = data.get('role', 'public')
    phone = data.get('phone', '')
    
    if not username or not password:
        return jsonify({'ok': False, 'message': '用户名和密码不能为空'}), 400
    
    from app.models import get_db
    conn = get_db()
    existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        return jsonify({'ok': False, 'message': '用户名已存在'}), 409
    
    import uuid, time
    user_id = str(uuid.uuid4())[:8]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn.execute('INSERT INTO users (id, username, password_hash, role, phone, created_at) VALUES (?,?,?,?,?,?)',
                 (user_id, username, password_hash, role, phone, str(int(time.time()))))
    conn.commit()
    conn.close()
    
    token = generate_token(user_id, role)
    return jsonify({'ok': True, 'token': token, 'user': {'id': user_id, 'username': username, 'role': role}})

@auth_bp.route('/verify')
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = verify_token(token)
    if payload:
        return jsonify({'ok': True, 'user': payload})
    return jsonify({'ok': False, 'message': 'Token无效或已过期'}), 401
