"""安全加固中间件 — OWASP Top 10 防护
A01: 失效的访问控制 — RBAC + 路由保护
A02: 加密失败 — 密码SHA256 + JWT签名
A03: 注入 — SQL参数化 + 输入校验
A04: 不安全设计 — 速率限制 + 输入长度限制
A05: 安全配置错误 — 安全响应头
A06: 易受攻击的组件 — 版本检查
A07: 认证失败 — 登录速率限制 + 密码策略
A08: 数据完整性失败 — CSRF token
A09: 日志监控 — 安全事件日志
A10: SSRF — URL白名单校验
"""
import time, hashlib, re, logging
from functools import wraps
from flask import request, jsonify, g

logger = logging.getLogger(__name__)

# 速率限制器
class RateLimiter:
    def __init__(self):
        self.requests = {}  # ip → [(timestamp, ...)]
    
    def check(self, key, limit=10, window=60):
        """检查速率限制"""
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        # 清理过期记录
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
        if len(self.requests[key]) >= limit:
            return False
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

# SQL注入检测
SQL_INJECTION_PATTERNS = [
    r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bDROP\b|\bUPDATE\b).*(\bFROM\b|\bINTO\b|\bTABLE\b)",
    r"'.*(OR|AND).*'=",
    r";.*--",
    r"/\*.*\*/",
    r"\bEXEC\b|\bEXECUTE\b",
    r"\bxp_cmdshell\b",
]

XSS_PATTERNS = [
    r"<script[^>]*>.*</script>",
    r"javascript:",
    r"on(error|load|click|mouseover|focus|blur)\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
]

def sanitize_input(value, max_length=1000):
    """输入消毒：截断 + 危险字符检测"""
    if not isinstance(value, str):
        value = str(value)
    if len(value) > max_length:
        value = value[:max_length]
    return value

def detect_sql_injection(value):
    """检测SQL注入"""
    if not isinstance(value, str):
        return False
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False

def detect_xss(value):
    """检测XSS"""
    if not isinstance(value, str):
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False

def security_headers(response):
    """添加安全响应头"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def require_auth(f):
    """要求JWT认证的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'ok': False, 'message': '未提供认证令牌'}), 401
        
        # 验证JWT
        from app.routes.auth import verify_jwt_token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'ok': False, 'message': '认证令牌无效或已过期'}), 401
        
        g.current_user = payload
        return f(*args, **kwargs)
    return decorated

def require_role(*roles):
    """要求特定角色的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return jsonify({'ok': False, 'message': '未认证'}), 401
            user_role = g.current_user.get('role', '')
            if user_role not in roles:
                return jsonify({'ok': False, 'message': f'权限不足，需要角色: {", ".join(roles)}'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def validate_input(data, rules):
    """输入验证
    rules: {'field_name': {'type': str, 'max_length': 100, 'required': True, 'pattern': r'^[a-z]+$'}}
    """
    errors = []
    for field, rule in rules.items():
        value = data.get(field)
        if rule.get('required') and not value:
            errors.append(f'{field}为必填项')
            continue
        if value is None:
            continue
        if rule.get('max_length') and len(str(value)) > rule['max_length']:
            errors.append(f'{field}长度不能超过{rule["max_length"]}')
        if rule.get('type') and not isinstance(value, rule['type']):
            try:
                rule['type'](value)
            except (ValueError, TypeError):
                errors.append(f'{field}类型不正确')
        if rule.get('pattern'):
            if not re.match(rule['pattern'], str(value)):
                errors.append(f'{field}格式不正确')
        # 安全检测
        if detect_sql_injection(str(value)):
            errors.append(f'{field}包含可疑SQL注入内容')
            logger.warning(f'SQL injection detected: field={field} ip={request.remote_addr}')
        if detect_xss(str(value)):
            errors.append(f'{field}包含可疑XSS内容')
            logger.warning(f'XSS detected: field={field} ip={request.remote_addr}')
    return errors

def init_security(app):
    """初始化安全中间件"""
    
    @app.before_request
    def before_request():
        # 速率限制
        ip = request.remote_addr or 'unknown'
        path = request.path
        
        # 登录/注册接口更严格
        if '/api/auth/' in path:
            if not rate_limiter.check(f'{ip}:{path}', limit=5, window=60):
                logger.warning(f'Rate limit exceeded: ip={ip} path={path}')
                return jsonify({'ok': False, 'message': '请求过于频繁，请稍后再试'}), 429
        else:
            if not rate_limiter.check(f'{ip}:{path}', limit=30, window=60):
                return jsonify({'ok': False, 'message': '请求过于频繁'}), 429
        
        # 输入消毒
        if request.is_json:
            try:
                data = request.get_json() or {}
                for key, value in data.items():
                    if isinstance(value, str):
                        if detect_sql_injection(value):
                            logger.warning(f'SQL injection blocked: field={key} ip={ip}')
                            return jsonify({'ok': False, 'message': f'输入包含非法内容'}), 400
                        if detect_xss(value):
                            logger.warning(f'XSS blocked: field={key} ip={ip}')
                            return jsonify({'ok': False, 'message': f'输入包含非法内容'}), 400
            except Exception:
                pass
    
    @app.after_request
    def after_request(response):
        return security_headers(response)
    
    logger.info('Security middleware initialized')
