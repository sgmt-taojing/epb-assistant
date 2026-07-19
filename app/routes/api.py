"""API路由 — 兼容现有前端fetch路径"""
from flask import Blueprint, jsonify, request
from app.models import get_db
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health():
    return jsonify({'ok': True, 'status': 'healthy', 'version': '2.1'})

@api_bp.route('/cases')
def cases():
    conn = get_db()
    rows = conn.execute('SELECT * FROM cases LIMIT 200').fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        for k in ['law', 'tags']:
            if d.get(k) and isinstance(d[k], str):
                try: d[k] = json.loads(d[k])
                except: pass
        result.append(d)
    return jsonify({'cases': result, 'total': len(result)})

@api_bp.route('/enterprises')
def enterprises():
    conn = get_db()
    rows = conn.execute('SELECT * FROM enterprises').fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        for k in ['pollutants', 'monitoring_points']:
            if d.get(k) and isinstance(d[k], str):
                try: d[k] = json.loads(d[k])
                except: pass
        result.append(d)
    return jsonify({'ok': True, 'enterprises': result, 'total': len(result)})

@api_bp.route('/devices')
def devices():
    conn = get_db()
    rows = conn.execute('SELECT * FROM devices').fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        for k in ['health', 'config']:
            if d.get(k) and isinstance(d[k], str):
                try: d[k] = json.loads(d[k])
                except: pass
        result.append(d)
    return jsonify({'ok': True, 'devices': result, 'total': len(result), 'device_types': 12})

@api_bp.route('/law_index')
def law_index():
    return jsonify({'version': 'v1.0', 'total_laws': 28, 'total_cases': 30})

@api_bp.route('/tasks')
def tasks():
    conn = get_db()
    rows = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(r) for r in rows]})

@api_bp.route('/users')
def users():
    conn = get_db()
    rows = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    safe = []
    for r in rows:
        d = dict(r)
        d.pop('password_hash', None)
        safe.append(d)
    return jsonify({'ok': True, 'users': safe, 'total': len(safe)})

@api_bp.route('/knowledge_graph')
def knowledge_graph():
    return jsonify({'ok': True, 'data': {'nodes': 35, 'edges': 52}})

@api_bp.route('/config')
def config():
    return jsonify({'ok': True, 'server': 'Flask', 'industry_types': ['化工','建材','造纸','纺织','电镀']})

@api_bp.route('/roles')
def roles():
    return jsonify({'version': '1.0', 'roles': [
        {'id': 'public', 'name': '公众'},
        {'id': 'enterprise', 'name': '企业'},
        {'id': 'gov_enforcement', 'name': '执法'},
        {'id': 'regulatory', 'name': '监管'},
        {'id': 'government', 'name': '政府'}
    ]})
