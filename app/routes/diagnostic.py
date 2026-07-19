"""国标对标与诊断报告引擎"""
from flask import Blueprint, jsonify, request
from app.models import get_db
import json, time

diag_bp = Blueprint('diagnostic', __name__)

# 国标库（内嵌）
STANDARDS = {
    'GB3838-2002': {
        'name': '地表水环境质量标准', 'category': '水质',
        'params': {
            'pH': {'limit': 9.0, 'unit': '-', 'min': 6.0},
            'COD': {'limit': 30, 'unit': 'mg/L'},
            'NH3N': {'limit': 1.5, 'unit': 'mg/L'},
            'TP': {'limit': 0.3, 'unit': 'mg/L'},
            'TN': {'limit': 1.5, 'unit': 'mg/L'},
        }
    },
    'GB3095-2012': {
        'name': '环境空气质量标准', 'category': '大气',
        'params': {
            'PM25': {'limit': 75, 'unit': 'μg/m³'},
            'PM10': {'limit': 150, 'unit': 'μg/m³'},
            'SO2': {'limit': 150, 'unit': 'μg/m³'},
            'NO2': {'limit': 80, 'unit': 'μg/m³'},
            'O3': {'limit': 200, 'unit': 'μg/m³'},
            'CO': {'limit': 4, 'unit': 'mg/m³'},
        }
    },
    'GB12348-2008': {
        'name': '厂界噪声排放标准', 'category': '噪声',
        'params': {
            'noise': {'limit': 60, 'unit': 'dB(A)'},
            'noise_night': {'limit': 50, 'unit': 'dB(A)'},
        }
    },
    'GB8978-1996': {
        'name': '污水综合排放标准', 'category': '废水排放',
        'params': {
            'COD': {'limit': 100, 'unit': 'mg/L'},
            'BOD5': {'limit': 30, 'unit': 'mg/L'},
            'SS': {'limit': 70, 'unit': 'mg/L'},
            'NH3N': {'limit': 15, 'unit': 'mg/L'},
            'oil': {'limit': 10, 'unit': 'mg/L'},
        }
    },
    'GB16297-1996': {
        'name': '大气污染物综合排放标准', 'category': '废气排放',
        'params': {
            'SO2': {'limit': 550, 'unit': 'mg/m³'},
            'NOx': {'limit': 240, 'unit': 'mg/m³'},
            'dust': {'limit': 120, 'unit': 'mg/m³'},
            'VOCs': {'limit': 80, 'unit': 'mg/m³'},
        }
    },
}

@diag_bp.route('/standards')
def list_standards():
    """获取国标列表"""
    return jsonify({'standards': [
        {'id': k, 'name': v['name'], 'category': v['category'], 'param_count': len(v['params'])}
        for k, v in STANDARDS.items()
    ]})

@diag_bp.route('/report', methods=['POST'])
def generate_report():
    """生成诊断报告
    输入: {enterprise: 'xxx', period_days: 30, standard: 'all'}
    输出: {score, grade, items: [...], suggestions: [...]}
    """
    data = request.get_json() or {}
    enterprise = data.get('enterprise', '')
    period = data.get('period_days', 30)
    std_filter = data.get('standard', 'all')
    
    # 查询时序数据
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM iot_data WHERE timestamp >= datetime("now", "-{} days")'.format(period)
    ).fetchall()
    conn.close()
    
    if not rows:
        # 无真实数据，用确定性模拟
        return _generate_mock_report(enterprise, std_filter)
    
    # 按参数分组计算
    param_values = {}
    for r in rows:
        p = r['param']
        if p not in param_values:
            param_values[p] = []
        param_values[p].append(r['value'])
    
    # 对标诊断
    items = []
    pass_count = 0
    warn_count = 0
    fail_count = 0
    
    for std_id, std in STANDARDS.items():
        if std_filter != 'all' and std_filter != std_id:
            continue
        for param, cfg in std['params'].items():
            if param not in param_values:
                continue
            values = param_values[param]
            avg_val = sum(values) / len(values)
            limit = cfg['limit']
            pct = avg_val / limit * 100
            
            if pct <= 80:
                status = 'pass'
                pass_count += 1
                suggestion = '继续保持，数据稳定达标。'
            elif pct <= 100:
                status = 'warn'
                warn_count += 1
                suggestion = '接近标准限值，建议加强治理设施运维。'
            else:
                status = 'fail'
                fail_count += 1
                suggestion = '已超标的建议立即排查治理设施运行状态。'
            
            items.append({
                'param': param,
                'value': round(avg_val, 2),
                'limit': limit,
                'unit': cfg['unit'],
                'pct': round(pct, 1),
                'status': status,
                'standard': std_id,
                'standard_name': std['name'],
                'suggestion': suggestion
            })
    
    total = pass_count + warn_count + fail_count
    score = round(pass_count / max(total, 1) * 100)
    grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'E'
    
    return jsonify({
        'ok': True,
        'enterprise': enterprise,
        'period_days': period,
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'score': score,
        'grade': grade,
        'pass_count': pass_count,
        'warn_count': warn_count,
        'fail_count': fail_count,
        'total_params': total,
        'items': items
    })

def _generate_mock_report(enterprise, std_filter):
    """无真实数据时生成确定性模拟报告"""
    import hashlib
    items = []
    pass_c = warn_c = fail_c = 0
    
    for std_id, std in STANDARDS.items():
        if std_filter != 'all' and std_filter != std_id:
            continue
        for param, cfg in std['params'].items():
            seed = int(hashlib.md5(f'{enterprise}{param}'.encode()).hexdigest()[:8], 16)
            pct = 30 + (seed % 90)  # 30-120%
            limit = cfg['limit']
            val = round(limit * pct / 100, 2)
            
            if pct <= 80:
                status = 'pass'
                pass_c += 1
                suggestion = '继续保持，数据稳定达标。'
            elif pct <= 100:
                status = 'warn'
                warn_c += 1
                suggestion = '接近标准限值，建议加强治理设施运维。'
            else:
                status = 'fail'
                fail_c += 1
                suggestion = '已超标的建议立即排查治理设施运行状态。'
            
            items.append({
                'param': param, 'value': val, 'limit': limit,
                'unit': cfg['unit'], 'pct': round(pct, 1),
                'status': status, 'standard': std_id,
                'standard_name': std['name'], 'suggestion': suggestion
            })
    
    total = pass_c + warn_c + fail_c
    score = round(pass_c / max(total, 1) * 100)
    grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'E'
    
    return jsonify({
        'ok': True, 'enterprise': enterprise, 'period_days': 30,
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'score': score, 'grade': grade,
        'pass_count': pass_c, 'warn_count': warn_c, 'fail_count': fail_c,
        'total_params': total, 'items': items,
        'note': '基于确定性模拟数据生成'
    })
