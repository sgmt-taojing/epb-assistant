"""API路由 — 兼容现有前端fetch路径"""
from flask import Blueprint, jsonify, request
from app.models import get_db
import json, time

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health():
    conn = get_db()
    # 真实统计
    case_count = conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
    ent_count = conn.execute('SELECT COUNT(*) FROM enterprises').fetchone()[0]
    dev_count = conn.execute('SELECT COUNT(*) FROM devices').fetchone()[0]
    iot_count = conn.execute('SELECT COUNT(*) FROM iot_data').fetchone()[0]
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    # 案件状态分布
    status_rows = conn.execute('SELECT status, COUNT(*) as cnt FROM cases GROUP BY status').fetchall()
    status_dist = {r['status']: r['cnt'] for r in status_rows}
    # 设备类型分布
    type_rows = conn.execute('SELECT type, COUNT(*) as cnt FROM devices GROUP BY type').fetchall()
    type_dist = {r['type']: r['cnt'] for r in type_rows}
    # 企业行业分布
    ind_rows = conn.execute('SELECT type, COUNT(*) as cnt FROM enterprises GROUP BY type').fetchall()
    ind_dist = {r['type']: r['cnt'] for r in ind_rows}
    # 最近24h活跃案件
    active_cases = conn.execute("SELECT COUNT(*) FROM cases WHERE status NOT IN ('archived','closed','rejected')").fetchone()[0]
    # IoT数据最新时间
    latest_iot = conn.execute('SELECT MAX(timestamp) FROM iot_data').fetchone()[0]
    conn.close()
    return jsonify({
        'ok': True, 'status': 'healthy', 'version': '3.0',
        'data_stats': {
            'cases': case_count,
            'enterprises': ent_count,
            'devices': dev_count,
            'iot_records': iot_count,
            'users': user_count,
            'active_cases': active_cases,
            'latest_iot': latest_iot,
            'law_index': 28,
            'knowledge_graph': 35,
            'law_mapping': 15
        },
        'case_status': status_dist,
        'device_types': type_dist,
        'industry_types': ind_dist,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    })

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
