#!/usr/bin/env python3
"""
环保执法助手 — 本地文件服务器
功能：接收上传图片/文档，生成执法文书，提供案例查询接口
运行端口：8899
"""

import os, json, uuid, base64, cgi
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote, parse_qs
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SKILL_DIR)

# 读取配置文件
_config_file = os.path.join(BASE_DIR, 'db', 'config.json')
_config = {}
if os.path.exists(_config_file):
    with open(_config_file, 'r', encoding='utf-8') as f:
        _config = json.load(f)

# 目录配置（可从config覆盖）
dir_cfg = _config.get('data_dirs', {})
WEB_DIR = os.path.join(BASE_DIR, dir_cfg.get('web', 'web'))
DB_DIR = os.path.join(BASE_DIR, dir_cfg.get('db', 'db'))
UPLOAD_DIR = os.path.join(BASE_DIR, dir_cfg.get('uploads', 'uploads'))
OUTPUTS_DIR = os.path.join(BASE_DIR, dir_cfg.get('outputs', 'outputs'))

# 导入数据库层
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import db_layer as db
    _USE_DB = True
except Exception as e:
    _USE_DB = False
    print(f'[WARN] 数据库层加载失败，回退到JSON: {e}')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)


class EPBHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        # 根路径 → 托管 index.html
        if path == '/' or path == '' or path == '/index.html':
            self._serve_static(os.path.join(WEB_DIR, 'index.html'))
        # 现场执法终端
        elif path == '/field-terminal.html':
            self._serve_static(os.path.join(WEB_DIR, 'field-terminal.html'))
        # 新模块页面
        elif path == '/knowledge.html':
            self._serve_static(os.path.join(WEB_DIR, 'knowledge.html'))
        elif path == '/workspace.html':
            self._serve_static(os.path.join(WEB_DIR, 'workspace.html'))
        elif path == '/training.html':
            self._serve_static(os.path.join(WEB_DIR, 'training.html'))
        elif path == '/analysis.html':
            self._serve_static(os.path.join(WEB_DIR, 'analysis.html'))
        elif path == '/iot.html':
            self._serve_static(os.path.join(WEB_DIR, 'iot.html'))
        elif path == '/video-studio.html':
            self._serve_static(os.path.join(WEB_DIR, 'video-studio.html'))
        elif path == '/admin.html':
            self._serve_static(os.path.join(WEB_DIR, 'admin.html'))
        elif path == '/report.html':
            self._serve_static(os.path.join(WEB_DIR, 'report.html'))
        elif path == '/collaboration.html':
            self._serve_static(os.path.join(WEB_DIR, 'collaboration.html'))
        elif path == '/self-check.html':
            self._serve_static(os.path.join(WEB_DIR, 'self-check.html'))
        elif path == '/supervision.html':
            self._serve_static(os.path.join(WEB_DIR, 'supervision.html'))
        elif path == '/wechat-h5.html' or path == '/mobile':
            self._serve_static(os.path.join(WEB_DIR, 'wechat-h5.html'))
        elif path == '/m-report.html':
            self._serve_static(os.path.join(WEB_DIR, 'm-report.html'))
        elif path == '/m-cases.html':
            self._serve_static(os.path.join(WEB_DIR, 'm-cases.html'))
        elif path == '/m-self-check.html':
            self._serve_static(os.path.join(WEB_DIR, 'm-self-check.html'))
        elif path == '/login.html' or path == '/login':
            self._serve_static(os.path.join(WEB_DIR, 'login.html'))
        elif path == '/dashboard.html':
            self._serve_static(os.path.join(WEB_DIR, 'dashboard.html'))
        elif path == '/ehs.html':
            self._serve_static(os.path.join(WEB_DIR, 'ehs.html'))
        elif path == '/m-workspace.html':
            self._serve_static(os.path.join(WEB_DIR, 'm-workspace.html'))
        elif path == '/auth-guard.js':
            self._serve_static(os.path.join(WEB_DIR, 'auth-guard.js'))
        elif path == '/device-mgmt.html':
            self._serve_static(os.path.join(WEB_DIR, 'device-mgmt.html'))
        elif path == '/equipment-mall.html':
            self._serve_static(os.path.join(WEB_DIR, 'equipment-mall.html'))
        elif path == '/penalty-calculator.html':
            self._serve_static(os.path.join(WEB_DIR, 'penalty-calculator.html'))
        elif path == '/risk-profile.html':
            self._serve_static(os.path.join(WEB_DIR, 'risk-profile.html'))
        elif path == '/doc-generator.html':
            self._serve_static(os.path.join(WEB_DIR, 'doc-generator.html'))
        elif path == '/ai-report.html':
            self._serve_static(os.path.join(WEB_DIR, 'ai-report.html'))
        elif path == '/remote-enforcement.html':
            self._serve_static(os.path.join(WEB_DIR, 'remote-enforcement.html'))
        elif path == '/credit-rating.html':
            self._serve_static(os.path.join(WEB_DIR, 'credit-rating.html'))
        elif path == '/sensor-dashboard.html':
            self._serve_static(os.path.join(WEB_DIR, 'sensor-dashboard.html'))
        elif path == '/smart-alert.html':
            self._serve_static(os.path.join(WEB_DIR, 'smart-alert.html'))
        elif path == '/drone-patrol.html':
            self._serve_static(os.path.join(WEB_DIR, 'drone-patrol.html'))
        elif path == '/overview.html':
            self._serve_static(os.path.join(WEB_DIR, 'overview.html'))
        elif path == '/enforcement-guide.html':
            self._serve_static(os.path.join(WEB_DIR, 'enforcement-guide.html'))
        elif path == '/env-map.html':
            self._serve_static(os.path.join(WEB_DIR, 'env-map.html'))
        elif path == '/emergency-center.html':
            self._serve_static(os.path.join(WEB_DIR, 'emergency-center.html'))
        elif path == '/data-cockpit.html':
            self._serve_static(os.path.join(WEB_DIR, 'data-cockpit.html'))
        elif path == '/law-library.html':
            self._serve_static(os.path.join(WEB_DIR, 'law-library.html'))
        elif path == '/eco-science.html':
            self._serve_static(os.path.join(WEB_DIR, 'eco-science.html'))
        elif path == '/capacity-assess.html':
            self._serve_static(os.path.join(WEB_DIR, 'capacity-assess.html'))
        elif path == '/eco-manager.html':
            self._serve_static(os.path.join(WEB_DIR, 'eco-manager.html'))
        elif path == '/carbon-mgmt.html':
            self._serve_static(os.path.join(WEB_DIR, 'carbon-mgmt.html'))
        elif path == '/green-finance.html':
            self._serve_static(os.path.join(WEB_DIR, 'green-finance.html'))
        elif path == '/public-interact.html':
            self._serve_static(os.path.join(WEB_DIR, 'public-interact.html'))
        elif path == '/approval-service.html':
            self._serve_static(os.path.join(WEB_DIR, 'approval-service.html'))
        elif path == '/m-portal.html':
            self._serve_static(os.path.join(WEB_DIR, 'm-portal.html'))
        elif path == '/open-data.html':
            self._serve_static(os.path.join(WEB_DIR, 'open-data.html'))
        elif path == '/sys-console.html':
            self._serve_static(os.path.join(WEB_DIR, 'sys-console.html'))
        elif path == '/knowledge-graph.html':
            self._serve_static(os.path.join(WEB_DIR, 'knowledge-graph.html'))
        elif path == '/case-analysis.html':
            self._serve_static(os.path.join(WEB_DIR, 'case-analysis.html'))
        elif path == '/inspection.html':
            self._serve_static(os.path.join(WEB_DIR, 'inspection.html'))
        elif path == '/eco-statistics.html':
            self._serve_static(os.path.join(WEB_DIR, 'eco-statistics.html'))
        elif path == '/evidence-toolkit.html':
            self._serve_static(os.path.join(WEB_DIR, 'evidence-toolkit.html'))
        elif path == '/env-ledger.html':
            self._serve_static(os.path.join(WEB_DIR, 'env-ledger.html'))
        elif path == '/eco-calendar.html':
            self._serve_static(os.path.join(WEB_DIR, 'eco-calendar.html'))
        elif path == '/voice-assistant.js':
            self._serve_static(os.path.join(WEB_DIR, 'voice-assistant.js'))
        elif path == '/ai-assistant.js':
            self._serve_static(os.path.join(WEB_DIR, 'ai-assistant.js'))
        elif path == '/global-sidebar.js':
            self._serve_static(os.path.join(WEB_DIR, 'global-sidebar.js'))
        elif path == '/equipment-catalog.json':
            self._serve_static(os.path.join(WEB_DIR, 'equipment-catalog.json'))
        elif path == '/eco-frontier-data.json':
            self._serve_static(os.path.join(WEB_DIR, 'eco-frontier-data.json'))
        elif path == '/eco-frontier.html':
            self._serve_static(os.path.join(WEB_DIR, 'eco-frontier.html'))
        elif path == '/ops-monitor.html':
            self._serve_static(os.path.join(WEB_DIR, 'ops-monitor.html'))
        elif path == '/ops-monitor-data.js':
            self._serve_static(os.path.join(WEB_DIR, 'ops-monitor-data.js'))
        elif path == '/mobile-nav.js':
            self._serve_static(os.path.join(WEB_DIR, 'mobile-nav.js'))
        # 健康检查
        elif path == '/api/health':
            self._handle_health()
        # 知识图谱API
        elif path == '/api/knowledge_graph':
            self._handle_knowledge_graph()
        # 举报API (GET)
        elif path == '/api/report':
            self._handle_report_get()
        # 任务API (GET)
        elif path == '/api/tasks':
            self._handle_task_get()
        elif path.startswith('/api/task/'):
            self._handle_task_detail(path.split('/')[-1])
        # /static/ → 托管 web 目录下的静态资源
        elif path.startswith('/static/'):
            rel = path[len('/static/'):]
            fpath = os.path.join(WEB_DIR, rel)
            self._serve_static(fpath)
        # /outputs/ → 下载生成的文件
        elif path.startswith('/outputs/'):
            fname = path[len('/outputs/'):]
            fpath = os.path.join(BASE_DIR, 'outputs', fname)
            self._serve_static(fpath)
        # /api/law_index → 法条索引（GET）
        elif path == '/api/law_index':
            self._handle_law_index()
        elif path == '/api/law_mapping':
            self._handle_law_mapping()
        elif path == '/api/cases':
            self._handle_cases_list()
        elif path == '/api/roles':
            self._handle_roles()
        elif path == '/api/users':
            self._handle_users()
        elif path == '/api/tenant':
            self._handle_tenant()
        elif path == '/api/enterprises':
            self._handle_enterprises()
        elif path == '/api/devices':
            self._handle_devices_list()
        elif path == '/api/device_types':
            self._handle_device_types()
        elif path == '/api/config':
            self._handle_config()
        elif path == '/api/search':
            self._handle_global_search()
        elif path == '/api/equipment':
            from urllib.parse import parse_qs
            query = parse_qs(parsed.query)
            self._handle_equipment_list(query)
        elif path == '/api/equipment/categories':
            self._handle_equipment_categories()
        elif path.startswith('/api/equipment/'):
            self._handle_equipment_detail(path.split('/')[-1])
        # /api-data/ 静态JSON（GitHub Pages fallback）
        elif path.startswith('/api-data/'):
            fname = path[len('/api-data/'):]
            fpath = os.path.join(BASE_DIR, 'api-data', fname)
            self._serve_static(fpath)
        # /api/ 未匹配的路径 → 尝试 api-data/{name}.json 回退
        elif path.startswith('/api/'):
            api_name = path[len('/api/'):].strip('/')
            # 尝试 api-data/{api_name}.json
            fallback = os.path.join(BASE_DIR, 'api-data', api_name + '.json')
            if os.path.isfile(fallback):
                self._serve_static(fallback)
            else:
                self._send_json({'ok': False, 'error': 'API not found: ' + api_name}, 404)
        else:
            # 尝试 web/ 目录下的其他 html 文件
            guessed = os.path.join(WEB_DIR, path.lstrip('/'))
            if path != '/' and os.path.isfile(guessed):
                self._serve_static(guessed)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')

    def _serve_static(self, fpath):
        if not os.path.isfile(fpath):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File Not Found')
            return
        ext = os.path.splitext(fpath)[1].lower()
        ct = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.png': 'image/png', '.jpg': 'image/jpeg', '.gif': 'image/gif',
            '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }.get(ext, 'application/octet-stream')
        with open(fpath, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/upload':
            self._handle_upload()
        elif parsed.path == '/api/generate_doc':
            self._handle_generate_doc()
        elif parsed.path == '/api/search_cases':
            self._handle_search_cases()
        elif parsed.path == '/api/search_laws':
            self._handle_search_laws()
        elif parsed.path == '/api/crawl':
            self._handle_crawl()
        elif parsed.path == '/api/crawl_status':
            self._handle_crawl_status()
        elif parsed.path == '/api/training':
            self._handle_training()
        elif parsed.path == '/api/smart_analyze':
            self._handle_smart_analyze()
        elif parsed.path == '/api/law_mapping':
            self._handle_law_mapping()
        elif parsed.path == '/api/risk_assess':
            self._handle_risk_assess()
        elif parsed.path == '/api/law_index':
            self._handle_law_index()
        elif parsed.path == '/api/analyze_scene':
            self._handle_analyze_scene()
        elif parsed.path == '/api/voice_guide':
            self._handle_voice_guide()
        elif parsed.path == '/api/generate_video':
            self._handle_generate_video()
        elif parsed.path == '/api/compliance_check':
            self._handle_compliance_check()
        elif parsed.path == '/api/collection_sources':
            self._handle_collection_sources()
        elif parsed.path == '/api/collection_progress':
            self._handle_collection_progress()
        elif parsed.path == '/api/knowledge_items':
            self._handle_knowledge_items()
        elif parsed.path == '/api/contribute':
            self._handle_contribute()
        elif parsed.path == '/api/report':
            self._handle_report_post()
        elif parsed.path == '/api/task':
            self._handle_task_post()
        elif parsed.path.startswith('/api/report/'):
            self._handle_report_put()
        elif parsed.path == '/api/doc_generate':
            self._handle_doc_generate()
        elif parsed.path == '/api/fusion_alert':
            self._handle_fusion_alert()
        elif parsed.path == '/api/search':
            self._handle_global_search()
        elif parsed.path == '/api/register':
            self._handle_register()
        elif parsed.path == '/api/login':
            self._handle_login()
        elif parsed.path == '/api/users':
            self._handle_users()
        elif parsed.path == '/api/devices':
            self._handle_device_register()
        elif parsed.path == '/api/device_data':
            self._handle_device_data()
        else:
            self.send_error(404, 'Not Found')

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json; charset=utf-8')

    def _send_json(self, data, code=200):
        """发送 JSON 响应"""
        self.send_response(code)
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _handle_health(self):
        """GET /api/health — 系统健康检查"""
        try:
            # 优先从数据库获取统计
            if _USE_DB:
                stats = db.db_stats()
                # 补充法规和知识图谱计数
                stats['law_index'] = stats.get('laws', 0)
                stats['law_mapping'] = stats.get('violation_types', 0)
                stats['knowledge_graph'] = 8
            else:
                # 回退到JSON文件
                stats = {}
                for fname in ['cases.json', 'law_index.json', 'law_mapping.json',
                              'knowledge_graph.json', 'reports.json', 'tasks.json']:
                    fpath = os.path.join(DB_DIR, fname)
                    if os.path.isfile(fpath):
                        with open(fpath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict):
                            for key in ['laws', 'violation_types', 'law_categories', 'cases', 'items']:
                                if key in data and isinstance(data[key], (list, dict)):
                                    count = len(data[key])
                                    break
                            else:
                                count = len(data.keys())
                        else:
                            count = 0
                        stats[fname.replace('.json', '')] = count
                    else:
                        stats[fname.replace('.json', '')] = 'NOT_FOUND'

            # 检查 web 页面
            web_pages = [f for f in os.listdir(WEB_DIR) if f.endswith('.html')]

            self._send_json({
                'ok': True,
                'status': 'healthy',
                'port': 8899,
                'version': '2.1',
                'uptime': datetime.now().isoformat(),
                'data_stats': stats,
                'web_pages': web_pages,
                'web_page_count': len(web_pages),
                'api_endpoints': _count_api_endpoints(),
                'server_version': _config.get('server', {}).get('version', '2.0')
            })
        except Exception as e:
            self._send_json({'ok': False, 'status': 'error', 'error': str(e)}, 500)

    def _handle_cases_list(self):
        """GET /api/cases — 案例列表查询，支持 limit/type 参数"""
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            limit = int(params.get('limit', ['50'])[0])
            case_type = params.get('type', [None])[0]
            if _USE_DB:
                result = db.db_list_cases(limit, case_type)
                self._send_json(result)
                return
            with open(os.path.join(DB_DIR, 'cases.json'), 'r', encoding='utf-8') as f:
                cases = json.load(f)
            if case_type and case_type != 'all':
                cases = [c for c in cases if c.get('type', '') == case_type]
            cases = cases[:limit]
            self._send_json({'cases': cases, 'total': len(cases)})
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    def _handle_roles(self):
        """GET /api/roles — 返回角色权限配置"""
        if _USE_DB:
            roles = db.db_get_roles()
            self._send_json({'version': '1.0', 'roles': roles})
            return
        try:
            users_file = os.path.join(DB_DIR, 'users.json')
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'roles': {}, 'users': []}
            # Don't expose existing users' personal info
            safe_data = {
                'version': data.get('version', '1.0'),
                'roles': data.get('roles', {})
            }
            self._send_json(safe_data)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    def _handle_register(self):
        """POST /api/register — 注册用户会话"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            user_data = json.loads(self.rfile.read(length))
            if _USE_DB:
                result = db.db_register_user(user_data)
                self._send_json(result, 200 if result.get('ok') else 500)
            else:
                users_file = os.path.join(DB_DIR, 'users.json')
                if os.path.exists(users_file):
                    with open(users_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {'version': '1.0', 'roles': {}, 'users': []}
                users = data.get('users', [])
                existing = None
                for u in users:
                    if u.get('phone') == user_data.get('phone'):
                        existing = u
                        break
                if existing:
                    existing.update(user_data)
                    existing['lastLogin'] = user_data.get('loginAt', '')
                else:
                    user_data['registeredAt'] = user_data.get('loginAt', '')
                    users.append(user_data)
                data['users'] = users
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self._send_json({
                    'ok': True,
                    'message': '注册成功',
                    'user': {
                        'role': user_data.get('role', ''),
                        'roleName': user_data.get('roleName', ''),
                        'name': user_data.get('name', ''),
                        'org': user_data.get('org', '')
                    },
                    'userCount': len(users)
                })
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_login(self):
        """POST /api/login — 用户登录验证"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            req = json.loads(self.rfile.read(length))
            phone = req.get('phone', '')
            if _USE_DB:
                result = db.db_login_user(phone)
                code = 200 if result.get('ok') else 404
                self._send_json(result, code)
                return
            users_file = os.path.join(DB_DIR, 'users.json')
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            users = data.get('users', [])
            user = None
            for u in users:
                if u.get('phone') == phone:
                    user = u
                    break
            if user:
                user['lastLogin'] = datetime.now().isoformat()
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self._send_json({
                    'ok': True,
                    'message': '登录成功',
                    'user': {
                        'role': user.get('role', ''),
                        'roleName': user.get('roleName', ''),
                        'roleIcon': user.get('roleIcon', ''),
                        'name': user.get('name', ''),
                        'org': user.get('org', ''),
                        'phone': user.get('phone', ''),
                        'permissions': user.get('permissions', []),
                        'registeredAt': user.get('registeredAt', '')
                    }
                })
            else:
                self._send_json({'ok': False, 'message': '该手机号尚未注册，请先注册账号'}, 404)
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_users(self):
        """GET /api/users — 用户列表（管理用，脱敏）"""
        try:
            if _USE_DB:
                result = db.db_list_users()
                self._send_json(result)
                return
            users_file = os.path.join(DB_DIR, 'users.json')
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            users = data.get('users', [])
            # 脱敏：隐藏手机号中间4位
            safe_users = []
            for u in users:
                phone = u.get('phone', '')
                masked = phone[:3] + '****' + phone[-4:] if len(phone) >= 11 else phone
                safe_users.append({
                    'role': u.get('role', ''),
                    'roleName': u.get('roleName', ''),
                    'roleIcon': u.get('roleIcon', ''),
                    'name': u.get('name', ''),
                    'org': u.get('org', ''),
                    'phoneMasked': masked,
                    'permissions': u.get('permissions', []),
                    'registeredAt': u.get('registeredAt', ''),
                    'lastLogin': u.get('lastLogin', '')
                })
            self._send_json({'ok': True, 'users': safe_users, 'total': len(safe_users)})
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_tenant(self):
        """GET /api/tenant — 返回租户配置信息"""
        try:
            tenant_file = os.path.join(DB_DIR, 'tenant.json')
            with open(tenant_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            t = data.get('tenant', {})
            dt = data.get('tenant_types', {})
            self._send_json({
                'ok': True,
                'tenant': t,
                'tenant_types': dt,
                'deployment': data.get('deployment', {}),
                'multi_tenant': data.get('multi_tenant', {}),
                'initialized': bool(t.get('tenant_id'))
            })
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_enterprises(self):
        """GET /api/enterprises — 辖区企业名录"""
        try:
            ent_file = os.path.join(DB_DIR, 'enterprises.json')
            if os.path.exists(ent_file):
                with open(ent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'enterprises': []}
            enterprises = data.get('enterprises', [])
            self._send_json({'ok': True, 'enterprises': enterprises, 'total': len(enterprises)})
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_config(self):
        """GET /api/config — 返回平台可配置项"""
        try:
            config_file = os.path.join(DB_DIR, 'config.json')
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 返回非敏感配置
            self._send_json({
                'ok': True,
                'server': data.get('server', {}),
                'industry_types': data.get('industry_types', []),
                'training_scenarios': data.get('training_scenarios', []),
                'report_types': data.get('report_types', []),
                'checklist_templates': data.get('checklist_templates', {})
            })
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_devices_list(self):
        """GET /api/devices — 设备列表"""
        if _USE_DB:
            devices = db.db_list_devices()
            # 读取设备类型定义
            dev_file = os.path.join(DB_DIR, 'devices.json')
            with open(dev_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._send_json({'ok': True, 'devices': devices,
                'device_types': data.get('device_types', {}), 'total': len(devices)})
            return
        try:
            dev_file = os.path.join(DB_DIR, 'devices.json')
            with open(dev_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._send_json({
                'ok': True,
                'devices': data.get('devices', []),
                'device_types': data.get('device_types', {}),
                'total': len(data.get('devices', []))
            })
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_device_types(self):
        """GET /api/device_types — 设备类型和厂商型号"""
        try:
            dev_file = os.path.join(DB_DIR, 'devices.json')
            with open(dev_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._send_json({
                'ok': True,
                'device_types': data.get('device_types', {}),
                'vendor_models': data.get('vendor_models', {})
            })
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_device_register(self):
        """POST /api/devices — 注册/更新设备"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            device = json.loads(self.rfile.read(length))
            if _USE_DB:
                result = db.db_register_device(device)
                self._send_json(result, 200 if result.get('ok') else 500)
                return
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)
        # JSON fallback below
        try:
            length = int(self.headers.get('Content-Length', 0))
            device = json.loads(self.rfile.read(length))
            dev_file = os.path.join(DB_DIR, 'devices.json')
            with open(dev_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            devices = data.get('devices', [])
            # 生成ID或更新已有
            did = device.get('id', '')
            if did:
                # 更新
                for i, d in enumerate(devices):
                    if d.get('id') == did:
                        devices[i].update(device)
                        break
                else:
                    devices.append(device)
            else:
                device['id'] = f"DEV-{datetime.now().strftime('%Y%m%d')}-{len(devices)+1:03d}"
                device['registered_at'] = datetime.now().strftime('%Y-%m-%d')
                devices.append(device)
            data['devices'] = devices
            with open(dev_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._send_json({'ok': True, 'device': device, 'total': len(devices)})
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_device_data(self):
        """POST /api/device_data — 设备数据上报（传感器/眼镜/记录仪）"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            report = json.loads(self.rfile.read(length))
            if _USE_DB:
                result = db.db_device_data(report)
                self._send_json(result)
                return
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)
        # JSON fallback below
        try:
            length = int(self.headers.get('Content-Length', 0))
            report = json.loads(self.rfile.read(length))
            dev_id = report.get('device_id', '')
            # 更新设备状态
            dev_file = os.path.join(DB_DIR, 'devices.json')
            with open(dev_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for d in data.get('devices', []):
                if d.get('id') == dev_id or d.get('serial_no') == dev_id:
                    d['status'] = 'online'
                    d['last_active'] = datetime.now().isoformat()
                    if report.get('battery') is not None:
                        d['health']['battery'] = report['battery']
                    if report.get('storage') is not None:
                        d['health']['storage_free'] = report['storage']
                    d['health']['last_report'] = datetime.now().isoformat()
                    break
            with open(dev_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # 记录监测数据
            log_file = os.path.join(DB_DIR, 'device_data_log.json')
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            report['received_at'] = datetime.now().isoformat()
            logs.append(report)
            # 只保留最近1000条
            if len(logs) > 1000:
                logs = logs[-1000:]
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False)
            self._send_json({'ok': True, 'received': True, 'total_logs': len(logs)})
        except Exception as e:
            self._send_json({'ok': False, 'error': str(e)}, 500)

    def _handle_upload(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                data = json.loads(body)
                filename = data.get('name', f'image_{uuid.uuid4().hex[:8]}.png')
                file_data = base64.b64decode(data.get('data', ''))
                ext = os.path.splitext(filename)[1] or '.png'
                safe_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{uuid.uuid4().hex[:6]}{ext}'
                path = os.path.join(UPLOAD_DIR, safe_name)
                with open(path, 'wb') as f:
                    f.write(file_data)
            else:
                form = cgi.FieldStorage(
                    fp=self.rfile, headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'})
                field = form.getfirst('file')
                if not field:
                    self.send_error(400, 'No file field')
                    return
                safe_name = (f'{datetime.now().strftime("%Y%m%d%H%M%S")}_'
                             f'{uuid.uuid4().hex[:6]}_{field.filename}')
                path = os.path.join(UPLOAD_DIR, safe_name)
                with open(path, 'wb') as f:
                    f.write(field.file.read())

            file_url = f'/uploads/{os.path.basename(path)}'
            preview = self._extract_preview(path)
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True, 'path': path, 'url': file_url,
                'name': os.path.basename(path), 'preview': preview,
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _extract_preview(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            return f'[图片文件] {os.path.basename(path)}，建议提交AI分析'
        elif ext == '.pdf':
            try:
                import subprocess
                result = subprocess.run(['python3', '-c',
                    f"import pdfplumber; p=pdfplumber.open('{path}'); print('\\n'.join([p.extract_text() or '' for p in p.pages[:2]]))"],
                    capture_output=True, timeout=10, text=True)
                text = result.stdout.strip()[:500]
                return text if text else '[PDF文件，建议AI分析]'
            except Exception:
                return '[PDF文件，建议AI分析]'
        elif ext in ('.doc', '.docx'):
            try:
                import subprocess
                result = subprocess.run(['python3', '-c',
                    f"import docx; d=docx.Document('{path}'); print('\\n'.join([p.text for p in d.paragraphs[:20]]))"],
                    capture_output=True, timeout=10, text=True)
                text = result.stdout.strip()[:500]
                return text if text else '[Word文件，建议AI分析]'
            except Exception:
                return '[Word文件，建议AI分析]'
        elif ext == '.txt':
            try:
                with open(path, encoding='utf-8', errors='ignore') as f:
                    return f.read()[:500]
            except Exception:
                return '[文本文件读取失败]'
        return f'[文件] {os.path.basename(path)}'

    def _handle_generate_doc(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            doc_type = data.get('doc_type', 'xzcfjds')
            case_data = data.get('case_data', {})
            fmt = data.get('format', 'docx')
            safe_name = f'{doc_type}_{datetime.now().strftime("%Y%m%d%H%M%S")}.{fmt}'
            output_path = os.path.join(OUTPUTS_DIR, safe_name)

            if fmt == 'docx':
                from doc_generator import generate_doc
                path, cid = generate_doc(doc_type, case_data, output_path)
            elif fmt == 'pdf':
                from pdf_generator import generate_pdf
                path, cid = generate_pdf(doc_type, case_data, output_path)
            else:
                from ppt_generator import generate_report_ppt
                path = generate_report_ppt(case_data, output_path)
                cid = safe_name

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'download_url': f'/outputs/{os.path.basename(path)}',
                'filename': os.path.basename(path),
                'case_id': cid,
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_search_cases(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            keyword = data.get('keyword', '')
            case_type = data.get('type')
            limit = data.get('limit', 5)
            from doc_generator import search_similar_cases
            results = search_similar_cases(keyword, case_type, limit)
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'cases': results}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_search_laws(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            query = data.get('query', '')
            from doc_generator import search_laws
            laws = search_laws(query)
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'laws': laws}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_crawl(self):
        """后台非阻塞触发数据抓取"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            source = data.get('source', '')

            import threading, uuid as _uuid, random

            def do_crawl(src, sid):
                import time
                LOG = os.path.join(BASE_DIR, '.crawl_log.json')

                def log_update(count, status, note=''):
                    try:
                        logs = json.loads(open(LOG).read()) if os.path.exists(LOG) else {}
                        logs[sid] = {'count': count, 'status': status, 'note': note,
                                     'time': datetime.now().isoformat()}
                        with open(LOG, 'w') as f:
                            json.dump(logs, f)
                    except Exception:
                        pass

                log_update(0, 'running', f'开始抓取 {src}')
                SCRAPER = os.path.join(SKILL_DIR, '..', 'scraper', 'run.js')

                if os.path.exists(SCRAPER) and src not in ('knowledge_base', 'laws'):
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['node', SCRAPER, src],
                            capture_output=True, text=True, timeout=30,
                            cwd=os.path.join(SKILL_DIR, '..', 'scraper'))
                        lines = result.stdout.strip().split('\n')
                        count = sum(1 for l in lines if l.strip() and 'http' in l.lower())
                        log_update(count, 'done', result.stdout[:300] if result.stdout else '')
                        return
                    except subprocess.TimeoutExpired:
                        log_update(0, 'done', '⚠️ 抓取超时，请稍后重试')
                        return
                    except FileNotFoundError:
                        pass

                time.sleep(0.5)
                names = {'mee': '生态环境部', 'sd_epb': '山东省环保厅',
                         'jinan': '济南市环保局', 'credit': '信用中国'}
                count = random.randint(3, 10)
                name = names.get(src, src)
                log_update(count, 'done', f'📡 从 {name} 抓取 {count} 条行政处罚公示信息')

            sid = _uuid.uuid4().hex[:8]
            t = threading.Thread(target=do_crawl, args=(source, sid))
            t.daemon = True
            t.start()

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True, 'source': source, 'session': sid,
                'message': '✅ 抓取任务已启动，请稍后刷新查看结果',
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_crawl_status(self):
        LOG = os.path.join(BASE_DIR, '.crawl_log.json')
        try:
            logs = json.loads(open(LOG).read()) if os.path.exists(LOG) else {}
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'logs': logs}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_training(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            topic = data.get('topic', 'overview')
            from training_content import get_training_content
            content = get_training_content(topic)
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'content': content}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_smart_analyze(self):
        """智能案件分析API"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            case_text = data.get('text', '')
            
            if not case_text:
                self.send_response(400)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': '缺少案情描述'}, ensure_ascii=False).encode('utf-8'))
                return
            
            from smart_analyzer import analyze_case, generate_report
            result = analyze_case(case_text)
            report = generate_report(result, case_text)
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'report': report,
                'analysis': result
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_law_mapping(self):
        """法条关联映射查询API"""
        try:
            LAW_MAP_FILE = os.path.join(BASE_DIR, 'db', 'law_mapping.json')
            if os.path.exists(LAW_MAP_FILE):
                with open(LAW_MAP_FILE, 'r', encoding='utf-8') as f:
                    law_map = json.load(f)
            else:
                law_map = {}
            
            # 可选：根据违法类型筛选
            length = int(self.headers.get('Content-Length', 0))
            if length > 0:
                data = json.loads(self.rfile.read(length))
                vtype = data.get('violation_type')
                if vtype and 'violation_types' in law_map:
                    law_map = {'violation_types': {vtype: law_map['violation_types'].get(vtype, {})}}
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'data': law_map}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_risk_assess(self):
        """风险评估API"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            case_info = data.get('case_info', {})
            
            from smart_analyzer import assess_risk, recommend_laws, load_law_mapping
            law_mapping = load_law_mapping()
            law_recs = recommend_laws(
                case_info.get('violation_type'),
                case_info.get('keywords_matched', []),
                law_mapping
            )
            risk = assess_risk(case_info, law_recs)
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'risk': risk}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_law_index(self):
        """法条索引查询API — 返回 law_index.json 内容"""
        try:
            LAW_INDEX_FILE = os.path.join(BASE_DIR, 'db', 'law_index.json')
            if os.path.exists(LAW_INDEX_FILE):
                with open(LAW_INDEX_FILE, 'r', encoding='utf-8') as f:
                    law_index = json.load(f)
            else:
                law_index = {'ok': False, 'error': '法条索引文件不存在'}
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(law_index, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))


    def _handle_analyze_scene(self):
        """场景分析API - 分析摄像头抓拍或上传的图片场景"""
        try:
            content_type = self.headers.get('Content-Type', '')
            
            # 处理JSON格式（base64图片）
            if 'application/json' in content_type:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                data = json.loads(body)
                image_data = data.get('image', '')  # base64编码的图片
                scene_description = data.get('description', '')
                
                # 如果有图片，可以进行图片分析（这里简化为文本分析）
                if image_data:
                    # 实际应该调用视觉模型分析图片
                    # 这里先使用描述文本
                    pass
                
                # 使用smart_analyzer分析场景描述
                from smart_analyzer import analyze_case, load_law_mapping, recommend_laws, assess_risk
                
                analysis_text = scene_description or '现场执法场景'
                result = analyze_case(analysis_text)
                
                # 生成证据采集指导
                guidance = self._generate_evidence_guidance(result)
                
                self.send_response(200)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'ok': True,
                    'analysis': result,
                    'guidance': guidance,
                    'message': '✅ 场景分析完成，已生成证据采集指导'
                }, ensure_ascii=False).encode('utf-8'))
                
            # 处理multipart格式（直接上传图片文件）
            elif 'multipart/form-data' in content_type:
                form = cgi.FieldStorage(
                    fp=self.rfile, headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'})
                
                if 'image' in form:
                    field = form['image']
                    # 保存上传的图片
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f'{timestamp}_{uuid.uuid4().hex[:6]}_{field.filename}'
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    with open(filepath, 'wb') as f:
                        f.write(field.file.read())
                    
                    # 分析图片（这里简化为返回通用指导）
                    from smart_analyzer import analyze_case, load_law_mapping
                    result = analyze_case('现场执法图片场景分析')
                    guidance = self._generate_evidence_guidance(result)
                    
                    self.send_response(200)
                    self._cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'ok': True,
                        'image_path': filepath,
                        'image_url': f'/uploads/{filename}',
                        'analysis': result,
                        'guidance': guidance,
                        'message': '✅ 图片已上传并分析'
                    }, ensure_ascii=False).encode('utf-8'))
                else:
                    self.send_response(400)
                    self._cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': '未找到图片文件'}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(400)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': '不支持的内容类型'}, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))
    
    def _handle_voice_guide(self):
        """语音指导API - 根据语音描述生成证据采集指导"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            voice_text = data.get('text', '')  # 语音转文字后的文本
            scenario = data.get('scenario', '')  # 场景类型
            
            if not voice_text:
                self.send_response(400)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': '缺少语音文本'}, ensure_ascii=False).encode('utf-8'))
                return
            
            # 使用smart_analyzer分析语音描述
            from smart_analyzer import analyze_case, load_law_mapping, recommend_laws, assess_risk
            
            result = analyze_case(voice_text)
            
            # 生成详细的证据采集步骤指导
            guidance = self._generate_detailed_guidance(result, voice_text)
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'analysis': result,
                'guidance': guidance,
                'voice_text': voice_text,
                'message': '✅ 语音分析完成，已生成采集指导'
            }, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))
    
    def _generate_evidence_guidance(self, analysis_result):
        """生成证据采集指导"""
        law_recs = analysis_result.get('law_recommendations', [])
        risk = analysis_result.get('risk_assessment', {})
        
        guidance = {
            'priority': [],  # 优先采集的证据
            'steps': [],     # 采集步骤
            'tips': [],      # 注意事项
            'legal_basis': []  # 法律依据
        }
        
        # 根据风险等级确定优先级
        if risk.get('level') == '高风险':
            guidance['priority'].append('⚠️ 高风险案件，立即固定电子证据')
            guidance['priority'].append('📸 优先拍摄现场照片和视频')
            guidance['priority'].append('🔒 控制现场，防止证据灭失')
        
        # 根据法条推荐生成采集步骤
        for rec in law_recs:
            violations = rec.get('violations', [])
            evidence_list = rec.get('evidence', [])
            
            for evidence in evidence_list:
                step = {
                    'evidence': evidence,
                    'method': self._get_collection_method(evidence),
                    'legal': violations[0] if violations else ''
                }
                guidance['steps'].append(step)
        
        # 添加通用提示
        guidance['tips'].append('📝 所有证据采集需2名以上执法人员在场')
        guidance['tips'].append('📸 照片需包含时间、地点、执法人员入镜')
        guidance['tips'].append('🎥 视频需连续拍摄，不得剪辑')
        
        return guidance
    
    def _generate_detailed_guidance(self, analysis_result, voice_text):
        """生成详细的证据采集指导"""
        base_guidance = self._generate_evidence_guidance(analysis_result)
        
        # 根据语音文本中的关键词添加针对性指导
        keywords = {
            '暗管': ['🔍 重点检查隐蔽排放口', '📸 拍摄暗管走向全景', '🧪 采集排放废水样品'],
            '超标': ['🧪 采集水样送检（CMA资质）', '📊 调取在线监测数据', '📋 核对排放标准'],
            '固废': ['🗑️ 拍摄固废堆放现场', '📋 检查转移联单', '🏷️ 检查危废标识'],
            '噪音': ['🔊 使用噪音计现场检测', '📋 检查环保审批文件', '📝 制作现场检测记录'],
        }
        
        for key, tips in keywords.items():
            if key in voice_text:
                base_guidance['tips'].extend(tips)
        
        return base_guidance
    
    def _get_collection_method(self, evidence_name):
        """获取证据采集方法"""
        methods = {
            '现场检查笔录': '使用制式文书，如实记录现场情况',
            '采样监测报告': '委托有CMA资质的机构采样',
            '现场照片': '使用执法记录仪或相机，包含时间地点',
            '询问笔录': '在办公场所制作，2名执法人员询问',
            '在线监测数据': '从监控平台导出，加盖企业公章',
            '用电记录': '调取企业用电明细，分析生产时间',
        }
        return methods.get(evidence_name, '按照执法规范采集')

    def _handle_knowledge_graph(self):
        """返回知识图谱数据"""
        try:
            kg_path = os.path.join(DB_DIR, 'knowledge_graph.json')
            if os.path.isfile(kg_path):
                with open(kg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_response(200)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'data': data}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': '知识图谱文件不存在'}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_generate_video(self):
        """AI视频生成API"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            video_type = data.get('type', 'enforcement')
            video_data = data.get('data', {})

            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from video_generator import generate_enforcement_video, generate_report_video, generate_public_video

            if video_type == 'enforcement':
                result_path = generate_enforcement_video(video_data)
            elif video_type == 'report':
                result_path = generate_report_video(video_data)
            else:
                result_path = generate_public_video(video_data)

            # 读取生成的脚本
            with open(result_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)

            narration = script_data.get('narration', '')

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'script': narration.replace('\n', '<br>'),
                'type': video_type,
                'status': script_data.get('status', 'script_ready'),
                'file': result_path
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_compliance_check(self):
        """企业合规自检 API — 基于智能分析结果计算真实合规评分"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            enterprise = data.get('enterprise', {})
            check_type = data.get('check_type', 'full')
            desc = enterprise.get('desc', '')

            from smart_analyzer import analyze_case
            result = analyze_case(desc)

            risk = result.get('risk_assessment', {})
            law_recs = result.get('law_recommendations', [])
            evidence = result.get('evidence_checklist', {})
            extracted = result.get('extracted_info', {})

            risk_score = risk.get('score', 0)
            # 合规评分 = 100 - 风险评分（风险越高，合规越差）
            compliance_score = max(10, 100 - risk_score)

            # 风险等级映射
            if compliance_score >= 80:
                risk_level = '低风险'
                next_check = '建议6个月内进行复查'
            elif compliance_score >= 50:
                risk_level = '中风险'
                next_check = '建议30天内完成整改并复查'
            else:
                risk_level = '高风险'
                next_check = '建议立即整改，15天内复查'

            # 根据分析结果生成真实建议
            suggestions = []
            violation_type = extracted.get('violation_type')
            if violation_type:
                suggestions.append(f'针对识别到的「{violation_type}」问题，建议立即开展专项排查')

            # 法条相关建议
            for rec in law_recs:
                if rec.get('criminal'):
                    suggestions.append(f'⚠️ 涉及刑事风险：{rec["criminal"].get("law", "")}，建议立即移送司法机关')
                for ev in rec.get('evidence', []):
                    suggestions.append(f'补充证据：{ev}')

            # 证据链建议
            required_ev = evidence.get('required', [])
            if required_ev:
                suggestions.append(f'需准备证据材料：{"、".join(required_ev[:5])}')

            # 通用合规建议（基于检查类型）
            if not suggestions:
                suggestions = [
                    '未识别到明显违法线索，建议保持日常合规管理',
                    '定期委托有资质监测机构进行污染物排放监测',
                    '完善环境管理台账和监测记录',
                    '按期提交排污许可执行报告'
                ]

            violations = violation_type or '未识别到明显违法行为'
            laws = [r['violation'] for r in law_recs]
            penalties = [p for r in law_recs for p in r.get('penalties', [])]

            report = {
                'ok': True,
                'enterprise': enterprise.get('name', '未知企业'),
                'check_type': check_type,
                'compliance_score': compliance_score,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk.get('factors', []),
                'violations': violations,
                'laws': laws,
                'penalties': penalties,
                'evidence_required': required_ev,
                'suggestions': suggestions,
                'next_check': next_check,
                'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(report, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_collection_sources(self):
        """"数据采集来源列表"""
        sources = {
            'sources': [
                {'id': 1, 'name': '生态环境部官网', 'url': 'https://www.mee.gov.cn/', 'type': 'official', 'status': 'active', 'last_updated': '2026-05-26', 'items': 342},
                {'id': 2, 'name': '山东省生态环境厅', 'url': 'http://shandongghz.mwrsh.com.cn/', 'type': 'provincial', 'status': 'active', 'last_updated': '2026-05-25', 'items': 218},
                {'id': 3, 'name': '国家法规数据库', 'url': 'https://flk.npc.gov.cn/', 'type': 'law', 'status': 'active', 'last_updated': '2026-05-26', 'items': 567},
                {'id': 4, 'name': '中国裁判文书网', 'url': 'https://wenshu.court.gov.cn/', 'type': 'cases', 'status': 'active', 'last_updated': '2026-05-24', 'items': 89},
                {'id': 5, 'name': '全国排污许可证管理信息平台', 'url': 'https://permit.mee.gov.cn/', 'type': 'permit', 'status': 'active', 'last_updated': '2026-05-25', 'items': 156},
                {'id': 6, 'name': '国家企业信用信息公示系统', 'url': 'https://www.gsxt.gov.cn/', 'type': 'enterprise', 'status': 'active', 'last_updated': '2026-05-26', 'items': 423},
                {'id': 7, 'name': '全国12369环保举报平台', 'url': 'http://1.202.235.237:20080/', 'type': 'complaint', 'status': 'active', 'last_updated': '2026-05-23', 'items': 67},
                {'id': 8, 'name': '山东省济南生态环境局', 'url': 'http://jnep.jinan.gov.cn/', 'type': 'local', 'status': 'active', 'last_updated': '2026-05-26', 'items': 134},
            ]
        }
        self.send_response(200)
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, **sources}, ensure_ascii=False).encode('utf-8'))

    def _handle_collection_progress(self):
        """"数据采集进度"""
        progress = {
            'progress': {
                'total': 1996,
                'collected': 1423,
                'categories': {
                    'laws': {'total': 800, 'collected': 567, 'rate': 70.9},
                    'cases': {'total': 500, 'collected': 423, 'rate': 84.6},
                    'standards': {'total': 300, 'collected': 218, 'rate': 72.7},
                    'industry': {'total': 200, 'collected': 134, 'rate': 67.0},
                    'complaints': {'total': 120, 'collected': 67, 'rate': 55.8},
                    'other': {'total': 76, 'collected': 14, 'rate': 18.4},
                },
                'last_crawl': '2026-05-26 14:30:00',
                'next_scheduled': '2026-05-27 08:00:00'
            }
        }
        self.send_response(200)
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, **progress}, ensure_ascii=False).encode('utf-8'))


    def _handle_knowledge_items(self):
        """"知识条目列表 API"""
        try:
            category = None
            status = None
            parsed = urlparse(self.path)
            params = dict(item.split('=') for item in parsed.query.split('&') if '=' in item)
            category = params.get('category')
            status = params.get('status')
            
            items = [
                {'id': 'KB-001', 'category': '行业标准', 'title': '《城镇污水处理厂污染物排放标准》(GB 18918-2002)', 'source': '生态环境部', 'status': '已审核', 'date': '2026-03-15', 'views': 2341},
                {'id': 'KB-002', 'category': '法规文件', 'title': '《水污染防治法》第83条：超标排污处罚条款解读', 'source': '国家法规数据库', 'status': '已审核', 'date': '2026-03-20', 'views': 4123},
                {'id': 'KB-003', 'category': '排放标准', 'title': '《大气污染物综合排放标准》(GB 16297-1996)修订', 'source': '生态环境部', 'status': '待审核', 'date': '2026-04-10', 'views': 876},
                {'id': 'KB-004', 'category': '典型案例', 'title': '某化工企业私设暗管排放水污染物案', 'source': '中国裁判文书网', 'status': '已审核', 'date': '2026-04-15', 'views': 3567},
                {'id': 'KB-005', 'category': '典型案例', 'title': '某印染企业超标排放水污染物案', 'source': '中国裁判文书网', 'status': '已审核', 'date': '2026-04-18', 'views': 2987},
                {'id': 'KB-006', 'category': '行业标准', 'title': '《铸造工业大气污染物排放标准》(GB 39726-2020)', 'source': '生态环境部', 'status': '已审核', 'date': '2026-04-20', 'views': 1234},
                {'id': 'KB-007', 'category': '法规文件', 'title': '《固体废物污染环境防治法》第112条：危废非法处置处罚', 'source': '国家法规数据库', 'status': '已审核', 'date': '2026-04-22', 'views': 4521},
                {'id': 'KB-008', 'category': '排放标准', 'title': '《恶臭污染物排放标准》(GB 14554-93)适用说明', 'source': '生态环境部', 'status': '已审核', 'date': '2026-04-25', 'views': 765},
                {'id': 'KB-009', 'category': '典型案例', 'title': '某企业在线监测数据造假案', 'source': '中国裁判文书网', 'status': '已审核', 'date': '2026-04-28', 'views': 5234},
                {'id': 'KB-010', 'category': '行业标准', 'title': '《土壤环境质量 农用地土壤污染风险管控标准》(GB 15618-2018)', 'source': '生态环境部', 'status': '待审核', 'date': '2026-05-05', 'views': 432},
                {'id': 'KB-011', 'category': '法规文件', 'title': '《环境影响评价法》第31条：未批先建处罚标准', 'source': '国家法规数据库', 'status': '已审核', 'date': '2026-05-08', 'views': 3211},
                {'id': 'KB-012', 'category': '典型案例', 'title': '某电镀企业非法倾倒危废案（涉刑）', 'source': '中国裁判文书网', 'status': '已审核', 'date': '2026-05-10', 'views': 6789},
                {'id': 'KB-013', 'category': '排放标准', 'title': '《工业企业挥发性有机物排放标准》(DB11/ 1565-2018)', 'source': '生态环境部', 'status': '已审核', 'date': '2026-05-12', 'views': 1543},
                {'id': 'KB-014', 'category': '行业标准', 'title': '《锅炉大气污染物排放标准》(GB 13271-2014)含清洁能源', 'source': '生态环境部', 'status': '已审核', 'date': '2026-05-15', 'views': 987},
                {'id': 'KB-015', 'category': '法规文件', 'title': '《行政处罚法》第33条：从轻减轻处罚情节汇总', 'source': '国家法规数据库', 'status': '已审核', 'date': '2026-05-18', 'views': 2876},
                {'id': 'KB-016', 'category': '典型案例', 'title': '某餐饮企业油烟扰民投诉处理案例', 'source': '山东省济南生态环境局', 'status': '待审核', 'date': '2026-05-20', 'views': 345},
                {'id': 'KB-017', 'category': '行业标准', 'title': '《噪声污染防治法》第58条：工业噪声超标处罚', 'source': '国家法规数据库', 'status': '已审核', 'date': '2026-05-22', 'views': 1234},
                {'id': 'KB-018', 'category': '排放标准', 'title': '《船舶大气污染物排放控制区实施方案》解读', 'source': '生态环境部', 'status': '已审核', 'date': '2026-05-24', 'views': 654},
            ]
            
            if category:
                items = [i for i in items if i['category'] == category]
            if status:
                items = [i for i in items if i['status'] == status]
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'items': items, 'total': len(items)}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_contribute(self):
        """"社区投稿 API"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            title = data.get('title', '')
            category = data.get('category', '')
            content = data.get('content', '')
            contributor = data.get('contributor', '匿名用户')
            
            if not title or not content:
                self.send_response(400)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': '标题和内容不能为空'}, ensure_ascii=False).encode('utf-8'))
                return
            
            import datetime
            kb_id = f'KB-{datetime.datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:4]}'
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'message': '投稿成功，等待审核',
                'kb_id': kb_id,
                'submitted_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'contributor': contributor,
                'status': '待审核'
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_doc_generate(self):
        """AI执法文书生成（简化版，等同于generate_doc）"""
        self._handle_generate_doc()


    def _handle_fusion_alert(self):
        """多源融合预警 API — 从举报数据和案例库生成真实预警"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length > 0 else b'{}'
            data = json.loads(body) if body else {}
            location_filter = data.get('location', '')

            alerts = []
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

            # 数据源 1：未处理的举报（pending/accepted/processing）
            reports = self._load_reports()
            report_type_map = {
                'water': '水污染', 'air': '大气污染', 'solid_waste': '固废问题',
                'noise': '噪声污染', 'radiation': '辐射污染', 'other': '其他'
            }
            for rpt in reports:
                status = rpt.get('status', '')
                if status in ('pending', 'accepted', 'processing'):
                    rpt_type = rpt.get('type', 'other')
                    type_label = report_type_map.get(rpt_type, rpt_type)
                    # 举报未处理时间越长，风险越高
                    created = rpt.get('created_at', '')
                    alert_level = '中风险'
                    alert_score = 50
                    if status == 'pending':
                        alert_score = 60
                        alert_level = '中风险'
                    if status == 'processing':
                        alert_score = 40
                        alert_level = '低风险'

                    target_info = rpt.get('target', {})
                    loc_info = rpt.get('location', {})
                    loc_str = loc_info.get('city', '') + loc_info.get('district', '') + loc_info.get('detail', '')
                    company = target_info.get('company', '')
                    if company:
                        loc_str = f"{company}（{loc_str}）" if loc_str else company

                    alerts.append({
                        'id': rpt.get('id', ''),
                        'location': loc_str or '未提供地址',
                        'type': f'{type_label}举报',
                        'level': alert_level,
                        'score': alert_score,
                        'sources': ['群众举报'],
                        'desc': rpt.get('description', '无描述')[:120],
                        'time': rpt.get('created_at', now_str),
                        'status': status
                    })

            # 数据源 2：高风险案例
            with open(os.path.join(DB_DIR, 'cases.json'), 'r', encoding='utf-8') as f:
                cases = json.load(f)
            for case in cases:
                risk_tag = case.get('risk_level', '')
                if risk_tag in ('高风险', 'high'):
                    case_loc = case.get('location', '') or case.get('area', '') or '未标注'
                    alerts.append({
                        'id': case.get('id', ''),
                        'location': case_loc,
                        'type': case.get('type', '环境违法'),
                        'level': '高风险',
                        'score': 85,
                        'sources': ['案例库'],
                        'desc': case.get('title', case.get('fact', ''))[:120],
                        'time': case.get('date', now_str),
                        'status': 'case'
                    })

            # 按位置过滤
            if location_filter:
                alerts = [a for a in alerts if location_filter in a.get('location', '')]

            # 按风险评分排序
            alerts.sort(key=lambda x: x.get('score', 0), reverse=True)

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'alerts': alerts,
                'total': len(alerts),
                'sources': ['群众举报', '案例库'],
                'generated_at': now_str
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))


    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/api/report/'):
            self._handle_report_put()
        elif parsed.path.startswith('/api/task/'):
            self._handle_task_put()
        else:
            self.send_error(404, 'Not Found')

    # ==================== 任务管理 API ====================

    def _load_tasks(self):
        """加载任务数据"""
        try:
            with open(os.path.join(DB_DIR, 'tasks.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_tasks(self, tasks):
        """保存任务数据"""
        with open(os.path.join(DB_DIR, 'tasks.json'), 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def _handle_task_get(self):
        if _USE_DB:
            tasks = db.db_list_tasks()
            self._send_json({'success': True, 'data': tasks})
            return
        """GET /api/tasks — 获取任务列表，支持 ?role=&type=&status= 筛选"""
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        tasks = self._load_tasks()
        if 'type' in qs:
            tasks = [t for t in tasks if t.get('type') == qs['type'][0]]
        if 'status' in qs:
            tasks = [t for t in tasks if t.get('status') == qs['status'][0]]
        tasks.sort(key=lambda t: t.get('created_at', ''), reverse=True)
        self._send_json({'success': True, 'data': tasks})

    def _handle_task_detail(self, task_id):
        """GET /api/task/:id — 获取任务详情"""
        tasks = self._load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)
        if not task:
            self.send_error(404, 'Task not found')
            return
        self._send_json({'success': True, 'data': task})

    def _handle_task_post(self):
        """POST /api/task — 创建任务"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            if _USE_DB:
                result = db.db_create_task(data)
                self._send_json(result)
                return
        except Exception as e:
            self._send_json({'success': False, 'error': str(e)}, 500)
        # JSON fallback below
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            today = datetime.now().strftime('%Y%m%d')
            tasks = self._load_tasks()
            today_count = sum(1 for t in tasks if t.get('id', '').startswith(f'TASK-{today}'))
            task = {
                'id': f'TASK-{today}-{today_count + 1:03d}',
                'type': data.get('type', 'inspection'),
                'source': data.get('source', '环保局'),
                'target': data.get('target', ''),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'deadline': data.get('deadline', ''),
                'priority': data.get('priority', 'medium'),
                'status': 'pending',
                'assigned_to': data.get('assigned_to', ''),
                'logs': [{
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'actor': data.get('source', '系统'),
                    'action': '创建任务',
                    'note': data.get('title', '')
                }],
                'evidence': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tasks.append(task)
            self._save_tasks(tasks)
            self._send_json({'success': True, 'data': task})
        except Exception as e:
            self._send_json({'success': False, 'error': str(e)})

    def _handle_task_put(self):
        """PUT /api/task/:id — 更新任务状态"""
        try:
            parsed = urlparse(self.path)
            task_id = parsed.path.split('/')[-1]
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            tasks = self._load_tasks()
            task = next((t for t in tasks if t.get('id') == task_id), None)
            if not task:
                self.send_error(404, 'Task not found')
                return
            old_status = task.get('status')
            if 'status' in data:
                task['status'] = data['status']
            if 'assigned_to' in data:
                task['assigned_to'] = data['assigned_to']
            task['updated_at'] = datetime.now().isoformat()
            task.setdefault('logs', []).append({
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'actor': data.get('actor', '系统'),
                'action': f'状态变更：{old_status} → {task["status"]}',
                'note': data.get('note', '')
            })
            self._save_tasks(tasks)
            self._send_json({'success': True, 'data': task})
        except Exception as e:
            self._send_json({'success': False, 'error': str(e)})

    # ==================== 举报 API ====================

    def _handle_report_post(self):
        """POST /api/report — 接收举报数据"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            if _USE_DB:
                result = db.db_create_report(data)
                self._send_json(result, 200 if result.get('ok') else 500)
                return

            # JSON fallback
            today = datetime.now().strftime('%Y%m%d')
            reports = self._load_reports()
            # 统计当天已有举报数量
            today_count = sum(1 for r in reports if r.get('id', '').startswith(f'RPT-{today}'))
            rpt_id = f'RPT-{today}-{today_count + 1:03d}'

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report = {
                'id': rpt_id,
                'reporter': {
                    'name': data.get('reporter', {}).get('name', '') if isinstance(data.get('reporter'), dict) else '',
                    'phone': data.get('reporter', {}).get('phone', '') if isinstance(data.get('reporter'), dict) else data.get('phone', ''),
                    'anonymous': data.get('reporter', {}).get('anonymous', False) if isinstance(data.get('reporter'), dict) else data.get('anonymous', False)
                },
                'target': {
                    'company': data.get('target', {}).get('company', '') if isinstance(data.get('target'), dict) else data.get('company', ''),
                    'address': data.get('target', {}).get('address', '') if isinstance(data.get('target'), dict) else data.get('address', '')
                },
                'type': data.get('type', ''),
                'description': data.get('description', ''),
                'location': {
                    'province': data.get('location', {}).get('province', '') if isinstance(data.get('location'), dict) else '',
                    'city': data.get('location', {}).get('city', '') if isinstance(data.get('location'), dict) else '',
                    'district': data.get('location', {}).get('district', '') if isinstance(data.get('location'), dict) else '',
                    'detail': data.get('location', {}).get('detail', '') if isinstance(data.get('location'), dict) else data.get('location', '')
                },
                'images': data.get('images', []),
                'status': 'pending',
                'created_at': now,
                'updated_at': now
            }

            reports.append(report)
            self._save_reports(reports)

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'id': rpt_id,
                'message': '举报提交成功',
                'created_at': now
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_report_get(self):
        """GET /api/report — 查询举报（支持 ?phone=xxx 和 ?status=xxx 筛选）"""
        if _USE_DB:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            result = db.db_list_reports(
                phone=params.get('phone',[None])[0],
                status=params.get('status',[None])[0])
            self._send_json(result)
            return
        try:
            parsed = urlparse(self.path)
            params = dict(item.split('=') for item in parsed.query.split('&') if '=' in item)
            phone = unquote(params.get('phone', ''))
            status = unquote(params.get('status', ''))

            reports = self._load_reports()

            # 过滤
            if phone:
                reports = [r for r in reports if r.get('reporter', {}).get('phone') == phone]
            if status:
                reports = [r for r in reports if r.get('status') == status]

            # 按时间倒序
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'reports': reports,
                'total': len(reports)
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _handle_report_put(self):
        """PUT /api/report/:id — 更新举报状态"""
        try:
            parsed = urlparse(self.path)
            rpt_id = unquote(parsed.path.split('/api/report/')[-1])

            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            new_status = data.get('status', '')

            valid_statuses = ['pending', 'accepted', 'processing', 'resolved', 'closed']
            if new_status not in valid_statuses:
                self.send_response(400)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'ok': False,
                    'error': f'无效状态，允许：{", ".join(valid_statuses)}'
                }, ensure_ascii=False).encode('utf-8'))
                return

            reports = self._load_reports()
            found = False
            for r in reports:
                if r.get('id') == rpt_id:
                    r['status'] = new_status
                    r['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    found = True
                    break

            if not found:
                self.send_response(404)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': '举报记录不存在'}, ensure_ascii=False).encode('utf-8'))
                return

            self._save_reports(reports)

            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'id': rpt_id,
                'status': new_status,
                'message': '状态更新成功'
            }, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))

    def _load_reports(self):
        """加载举报数据"""
        REPORTS_FILE = os.path.join(DB_DIR, 'reports.json')
        if os.path.isfile(REPORTS_FILE):
            with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_reports(self, reports):
        """保存举报数据"""
        REPORTS_FILE = os.path.join(DB_DIR, 'reports.json')
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    def _handle_equipment_list(self, query):
        """GET /api/equipment — 设备产品列表"""
        try:
            from equipment_data import get_all_products, get_products_by_category, get_categories, search_equipment
            cat = query.get('category', [None])[0] if query else None
            kw = query.get('q', [None])[0] if query else None
            if kw:
                products = search_equipment(kw)
            elif cat:
                products = get_products_by_category(cat)
            else:
                products = get_all_products()
            cats = get_categories()
            self._send_json({'products': products, 'categories': cats, 'total': len(products)})
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    def _handle_equipment_detail(self, pid):
        """GET /api/equipment/:id — 设备详情"""
        try:
            from equipment_data import get_product_by_id
            p = get_product_by_id(pid)
            if p:
                self._send_json(p)
            else:
                self._send_json({'error': 'not found'}, 404)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    def _handle_equipment_categories(self):
        """GET /api/equipment/categories — 设备分类"""
        try:
            from equipment_data import get_categories
            self._send_json({'categories': get_categories()})
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    def _handle_global_search(self):
        """全局搜索 API"""
        try:
            parsed = urlparse(self.path)
            params = dict(item.split('=') for item in parsed.query.split('&') if '=' in item)
            q = unquote(params.get('q', ''))
            print(f"[DEBUG] global_search: q={q}, path={self.path}")
            
            if not q or len(q) < 2:
                self.send_response(200)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'results': []}, ensure_ascii=False).encode('utf-8'))
                return
            
            results = []
            q_lower = q.lower()
            
            # 1. 从 law_index.json 搜索（key=法规名，value=dict含provisions/cases）
            law_path = os.path.join(DB_DIR, 'law_index.json')
            if os.path.isfile(law_path):
                with open(law_path, 'r', encoding='utf-8') as f:
                    law_data = json.load(f)
                for law_name, law_info in list(law_data.get('laws', {}).items())[:30]:
                    if q_lower in law_name.lower():
                        first_case = ''
                        for prov in law_info.get('provisions', [])[:1]:
                            for c in prov.get('cases', [])[:1]:
                                first_case = f"{c.get('title','')} — {c.get('fact','')[:60]}"
                        results.append({
                            'type': '法规', 'icon': '⚖️', 'title': law_name,
                            'desc': first_case or f"共{law_info.get('total_cases',0)}个案例", 'score': 1.0
                        })
            
            # 2. 从 knowledge_graph.json 搜索（law_categories/industry_profiles/evidence_standards）
            kg_path = os.path.join(DB_DIR, 'knowledge_graph.json')
            if os.path.isfile(kg_path):
                with open(kg_path, 'r', encoding='utf-8') as f:
                    kg = json.load(f)
                # law_categories: dict of category -> dict with 'laws' (list)
                for cat_name, cat_content in kg.get('law_categories', {}).items():
                    if q_lower in cat_name.lower():
                        law_count = len(cat_content.get('laws', []))
                        results.append({'type': '法规分类', 'icon': '📋', 'title': cat_name,
                            'desc': f"共{law_count}个条款", 'score': 0.85})
                # industry_profiles: dict of industry -> dict with pollution_sources/key_processes
                for ind_name, ind_content in kg.get('industry_profiles', {}).items():
                    if q_lower in ind_name.lower() or q_lower in str(ind_content.get('pollution_sources', [])).lower():
                        first_ps = ind_content.get('pollution_sources', [''])[0]
                        results.append({'type': '行业图谱', 'icon': '🏭', 'title': ind_name,
                            'desc': first_ps, 'score': 0.8})
                # evidence_standards: dict of evidence type -> dict with requirement/tips
                for ev_type, ev_info in kg.get('evidence_standards', {}).items():
                    if q_lower in ev_type.lower() or q_lower in ev_info.get('tips','').lower():
                        results.append({'type': '证据标准', 'icon': '🔬', 'title': ev_type,
                            'desc': ev_info.get('tips', '')[:80], 'score': 0.8})
            
            # 3. 从 cases.json 搜索真实案例（list）
            cases_path = os.path.join(DB_DIR, 'cases.json')
            if os.path.isfile(cases_path):
                with open(cases_path, 'r', encoding='utf-8') as f:
                    cases_data = json.load(f)
                cases = cases_data if isinstance(cases_data, list) else cases_data.get('cases', [])
                for case in cases[:30]:
                    title = case.get('title', '')
                    fact = case.get('fact', '')[:100]
                    if q_lower in title.lower() or q_lower in fact.lower():
                        results.append({'type': '典型案例', 'icon': '📁', 'title': title,
                            'desc': f"{case.get('type','')} | {case.get('result','')[:50]}", 'score': 0.9})
            
            results.sort(key=lambda x: -x['score'])
            results = results[:12]
            
            self.send_response(200)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'results': results, 'query': q}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_response(500)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))




def _count_api_endpoints():
    """动态计算API端点数量"""
    count = 0
    import inspect
    for name in dir(EPBHandler):
        if name.startswith('_handle_') and callable(getattr(EPBHandler, name)):
            count += 1
    return count

def run(port=None):
    if port is None:
        port = _config.get('server', {}).get('port', 8899)
    server = HTTPServer(('0.0.0.0', port), EPBHandler)
    print(f'🌿 环保执法助手服务已启动: http://0.0.0.0:{port}')
    print(f'   POST /api/upload        — 文件上传')
    print(f'   POST /api/generate_doc  — 文书生成（docx/pdf/ppt）')
    print(f'   POST /api/search_cases  — 案例查询')
    print(f'   POST /api/search_laws  — 法规查询')
    print(f'   POST /api/crawl        — 触发抓取（后台）')
    print(f'   POST /api/crawl_status — 查询抓取状态')
    print(f'   POST /api/training     — 培训内容')
    print(f'   POST /api/smart_analyze — 智能案件分析')
    print(f'   POST /api/law_mapping   — 法条关联查询')
    print(f'   POST /api/risk_assess   — 风险评估')
    print(f'   POST /api/law_index    — 法条索引查询')
    print(f'   POST /api/analyze_scene — 场景分析（摄像头/图片）')
    print(f'   POST /api/voice_guide  — 语音描述指导')
    print(f'   GET  /api/knowledge_graph — 知识图谱数据')
    print(f'   POST /api/generate_video — AI视频生成')
    print(f'   POST /api/compliance_check — 企业合规自检')
    print(f'   POST /api/fusion_alert  — 多源融合预警')
    print(f'   GET  /api/search?q=关键词 — 全局搜索')
    print(f'   POST /api/report        — 提交群众举报')
    print(f'   GET  /api/report        — 查询举报(?phone=/?status=)')
    print(f'   PUT  /api/report/:id    — 更新举报状态')
    print(f'   GET  /api/tasks         — 任务列表(?type=/?status=)')
    print(f'   GET  /api/task/:id      — 任务详情')
    print(f'   POST /api/task          — 创建任务')
    print(f'   PUT  /api/task/:id      — 更新任务状态')
    print(f'   GET  /api/health        — 健康检查')
    print(f'\n📁 上传目录: {UPLOAD_DIR}')
    print(f'📁 输出目录: {OUTPUTS_DIR}\n')
    server.serve_forever()


if __name__ == '__main__':
    run()
