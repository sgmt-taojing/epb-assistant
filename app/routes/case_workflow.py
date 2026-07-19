"""案件全流程闭环 — 状态机驱动"""
from flask import Blueprint, jsonify, request
from app.models import get_db
import time, uuid

case_bp = Blueprint('case', __name__)

# 案件状态机
STATES = {
    'reported': {'name': '已举报', 'next': ['accepted', 'rejected'], 'sla': 24},
    'accepted': {'name': '已受理', 'next': ['investigating'], 'sla': 48},
    'investigating': {'name': '调查中', 'next': ['hearing'], 'sla': 168},
    'hearing': {'name': '审理中', 'next': ['penalty', 'closed'], 'sla': 72},
    'penalty': {'name': '处罚决定', 'next': ['executing'], 'sla': 24},
    'executing': {'name': '执行中', 'next': ['archived'], 'sla': 168},
    'archived': {'name': '已归档', 'next': [], 'sla': 0},
    'rejected': {'name': '已驳回', 'next': [], 'sla': 0},
    'closed': {'name': '已结案', 'next': [], 'sla': 0},
}

@case_bp.route('/report', methods=['POST'])
def create_report():
    """公众举报 → 创建案件"""
    data = request.get_json() or {}
    case_id = 'CASE-' + str(int(time.time()))[-8:]
    conn = get_db()
    conn.execute(
        'INSERT INTO cases (id, date, title, party, type, source, fact, status, risk_level, criminal, fetchedAt) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (case_id, time.strftime('%Y-%m-%d'), data.get('title','匿名举报'), data.get('party','匿名'),
         data.get('type','其他'), '公众举报', data.get('fact',''), 'reported', '中风险', 0, time.strftime('%Y-%m-%dT%H:%M:%S'))
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'case_id': case_id, 'status': 'reported', 'message': '举报成功，将在24小时内受理'})

@case_bp.route('/<case_id>/transition', methods=['POST'])
def transition(case_id):
    """案件状态流转"""
    data = request.get_json() or {}
    new_status = data.get('status')
    
    conn = get_db()
    case = conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
    if not case:
        conn.close()
        return jsonify({'ok': False, 'message': '案件不存在'}), 404
    
    current_status = case['status']
    if new_status not in STATES.get(current_status, {}).get('next', []):
        conn.close()
        return jsonify({'ok': False, 'message': f'不允许从{current_status}转到{new_status}'}), 400
    
    conn.execute('UPDATE cases SET status = ? WHERE id = ?', (new_status, case_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'ok': True, 
        'case_id': case_id, 
        'prev_status': current_status, 
        'new_status': new_status,
        'status_name': STATES[new_status]['name']
    })

@case_bp.route('/states')
def get_states():
    """获取状态机定义"""
    return jsonify({'states': {k: v for k, v in STATES.items()}})

@case_bp.route('/sla/<case_id>')
def check_sla(case_id):
    """检查案件SLA"""
    conn = get_db()
    case = conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
    conn.close()
    if not case:
        return jsonify({'ok': False, 'message': '案件不存在'}), 404
    
    state = STATES.get(case['status'], {})
    sla_hours = state.get('sla', 0)
    if sla_hours == 0:
        return jsonify({'ok': True, 'case_id': case_id, 'sla': 0, 'message': '无SLA要求'})
    
    # 计算已用时间（简化）
    return jsonify({
        'ok': True, 'case_id': case_id,
        'sla_hours': sla_hours,
        'status': case['status']
    })
