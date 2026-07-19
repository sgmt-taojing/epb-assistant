"""
EPB Assistant 5角色机器人 — 模拟真实业务流程
公众举报 → 执法受理 → 调查取证 → 审理处罚 → 监管督办 → 归档

每60秒运行一轮，产生真实案件流转和IoT数据。
"""
import json, time, hashlib, urllib.request, sqlite3, os
from datetime import datetime, timedelta
import random as _r  # 仅用于机器人行为模拟，非业务数据

BASE = 'http://127.0.0.1:8900'
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'epb.db')

# 5角色
ROLES = {
    'public': {
        'name': '张市民', 'role': 'public', 'roleName': '公众',
        'roleIcon': '📢', 'org': '济南市民',
        'actions': ['report_pollution', 'check_progress', 'view_laws']
    },
    'enterprise': {
        'name': '李经理', 'role': 'enterprise', 'roleName': '企业',
        'roleIcon': '🏭', 'org': '齐鲁化工有限公司',
        'actions': ['self_check', 'submit_report', 'view_devices', 'request_diagnosis']
    },
    'enforcement': {
        'name': '王执法', 'role': 'gov_enforcement', 'roleName': '执法',
        'roleIcon': '🚔', 'org': '济南市生态环境综合执法支队',
        'actions': ['accept_case', 'investigate', 'collect_evidence', 'issue_penalty']
    },
    'regulatory': {
        'name': '赵监管', 'role': 'regulatory', 'roleName': '监管',
        'roleIcon': '👁️', 'org': '山东省生态环境厅',
        'actions': ['monitor_all', 'check_sla', 'review_diagnosis', 'supervise']
    },
    'government': {
        'name': '孙主任', 'role': 'government', 'roleName': '政府',
        'roleIcon': '🏛️', 'org': '济南市政府',
        'actions': ['view_dashboard', 'check_stats', 'review_policy']
    }
}

# 举报模板
REPORT_TEMPLATES = [
    {'title': '齐鲁化工异味气体排放', 'type': '大气污染类', 'fact': '厂区周边持续闻到刺鼻化学气味，疑似废气处理设施停运', 'risk': '高风险'},
    {'title': '小清河排水口水质异常', 'type': '水污染类', 'fact': '排水口水体呈乳白色，疑似未经处理的生产废水直排', 'risk': '高风险'},
    {'title': '夜间施工噪声扰民', 'type': '噪声污染类', 'fact': '凌晨2点仍在施工，噪音严重超标影响居民休息', 'risk': '中风险'},
    {'title': '建筑工地扬尘严重', 'type': '固废污染类', 'fact': '工地未采取防尘措施，周边PM10严重超标', 'risk': '中风险'},
    {'title': '养殖场污水渗漏', 'type': '水污染类', 'fact': '养殖场粪污处理设施破损，污水渗入地下', 'risk': '中风险'},
    {'title': '电镀厂重金属超标排放', 'type': '水污染类', 'fact': '废水在线监测数据显示铬、镍超标', 'risk': '高风险'},
    {'title': '加油站油气回收不达标', 'type': '大气污染类', 'fact': '油气挥发严重，回收装置疑似故障', 'risk': '低风险'},
    {'title': '餐饮店油烟直排', 'type': '大气污染类', 'fact': '未安装油烟净化设施，油烟直接排放', 'risk': '低风险'},
]

ENTERPRISES = [
    '齐鲁化工有限公司', '济南钢铁集团', '山东造纸厂', '青岛纺织印染', 
    '淄博建材集团', '烟台电镀园', '潍坊食品加工', '临沂化工园'
]

POLLUTANTS = ['COD', '氨氮', 'PM2.5', 'PM10', 'SO2', 'NOx', 'VOCs', '噪声']

def api_call(method, path, data=None):
    """调用API"""
    url = BASE + path
    if data:
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url)
    req.get_method = lambda: method
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read())
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def insert_iot_data():
    """插入新的IoT数据点（每轮5-10条）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 获取所有设备
    devices = c.execute('SELECT id, type FROM devices LIMIT 30').fetchall()
    count = 0
    now = datetime.now()
    
    for dev_id, dev_type in devices:
        # 每台设备插入最新一条数据
        ts = now.strftime('%Y-%m-%dT%H:%M:%S')
        
        if dev_type == 'water_quality':
            params = [('pH', 6.5 + _r.random() * 2.5, '-', 'GB3838-2002'),
                      ('COD', 15 + _r.random() * 80, 'mg/L', 'GB8978-1996'),
                      ('氨氮', 0.5 + _r.random() * 3, 'mg/L', 'GB3838-2002')]
        elif dev_type == 'air_quality':
            params = [('PM2.5', 20 + _r.random() * 100, 'μg/m³', 'GB3095-2012'),
                      ('PM10', 30 + _r.random() * 120, 'μg/m³', 'GB3095-2012'),
                      ('SO2', 5 + _r.random() * 40, 'μg/m³', 'GB3095-2012')]
        elif dev_type == 'noise':
            params = [('噪声', 45 + _r.random() * 35, 'dB', 'GB12348-2008')]
        elif dev_type == 'emission_water':
            params = [('COD', 20 + _r.random() * 60, 'mg/L', 'GB8978-1996'),
                      ('氨氮', 1 + _r.random() * 4, 'mg/L', 'GB8978-1996')]
        elif dev_type == 'emission_gas':
            params = [('SO2', 10 + _r.random() * 80, 'mg/m³', 'GB16297-1996'),
                      ('NOx', 20 + _r.random() * 100, 'mg/m³', 'GB16297-1996')]
        elif dev_type == 'power':
            params = [('用电量', 100 + _r.random() * 500, 'kWh', '-')]
        elif dev_type == 'soil':
            params = [('重金属', 0.01 + _r.random() * 0.1, 'mg/kg', 'GB36600-2018')]
        else:
            params = [('数值', _r.random() * 100, '-', '-')]
        
        for param, value, unit, standard in params:
            c.execute(
                'INSERT INTO iot_data (device_id, param, value, unit, standard, timestamp) VALUES (?,?,?,?,?,?)',
                (dev_id, param, round(value, 4), unit, standard, ts)
            )
            count += 1
    
    conn.commit()
    conn.close()
    return count

def get_cases_by_status(status):
    """获取指定状态的案件"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT id, title, type FROM cases WHERE status = ? LIMIT 5', (status,)).fetchall()
    conn.close()
    return [{'id': r[0], 'title': r[1], 'type': r[2]} for r in rows]

def run_robot_cycle():
    """运行一轮5角色机器人"""
    log = []
    
    # 1. 公众：举报污染
    template = _r.choice(REPORT_TEMPLATES)
    result = api_call('POST', '/api/case/report', {
        'title': template['title'],
        'type': template['type'],
        'fact': template['fact']
    })
    case_id = result.get('case_id', '')
    log.append(f"📢 公众·张市民 举报: {template['title']} → {case_id}")
    
    # 2. 执法：受理案件
    reported = get_cases_by_status('reported')
    for case in reported[:2]:  # 每轮受理2个
        result = api_call('POST', f'/api/case/{case["id"]}/transition', {'status': 'accepted'})
        if result.get('ok'):
            log.append(f"🚔 执法·王执法 受理: {case['title']} → 已受理")
        
        # 继续推进到调查中
        result = api_call('POST', f'/api/case/{case["id"]}/transition', {'status': 'investigating'})
        if result.get('ok'):
            log.append(f"🚔 执法·王执法 调查: {case['title']} → 调查中")
    
    # 3. 执法：推进调查中的案件到审理
    investigating = get_cases_by_status('investigating')
    for case in investigating[:2]:
        result = api_call('POST', f'/api/case/{case["id"]}/transition', {'status': 'hearing'})
        if result.get('ok'):
            log.append(f"🚔 执法·王执法 取证完毕: {case['title']} → 审理中")
    
    # 4. 审理 → 处罚决定
    hearing = get_cases_by_status('hearing')
    for case in hearing[:2]:
        result = api_call('POST', f'/api/case/{case["id"]}/transition', {'status': 'penalty'})
        if result.get('ok'):
            log.append(f"🚔 执法·王执法 处罚: {case['title']} → 处罚决定")
    
    # 5. 处罚 → 执行中
    penalty = get_cases_by_status('penalty')
    for case in penalty[:2]:
        result = api_call('POST', f'/api/case/{case["id"]}/transition', {'status': 'executing'})
        if result.get('ok'):
            log.append(f"🚔 执法·王执法 执行: {case['title']} → 执行中")
    
    # 6. 执行 → 归档
    executing = get_cases_by_status('executing')
    for case in executing[:1]:
        result = api_call('POST', f'/api/case/{case["id"]}/transition', {'status': 'archived'})
        if result.get('ok'):
            log.append(f"📁 案件归档: {case['title']} → 已归档")
    
    # 7. 企业：请求诊断报告
    ent = _r.choice(ENTERPRISES)
    result = api_call('POST', '/api/diag/report', {
        'enterprise': ent, 'period_days': 30, 'standard': 'all'
    })
    if result.get('ok'):
        log.append(f"🏭 企业·李经理 诊断: {ent} → 评分{result['score']}({result['grade']})")
    
    # 8. 监管：查看SLA
    all_cases = get_cases_by_status('investigating') + get_cases_by_status('hearing')
    if all_cases:
        case = all_cases[0]
        result = api_call('GET', f'/api/case/sla/{case["id"]}')
        log.append(f"👁️ 监管·赵监管 督办: {case['title']} SLA={result.get('sla_hours','?')}h")
    
    # 9. 政府：查看总览
    result = api_call('GET', '/api/health')
    stats = result.get('data_stats', {})
    log.append(f"🏛️ 政府·孙主任 总览: 案件{stats.get('cases',0)} 企业{stats.get('enterprises',0)} 设备{stats.get('devices',0)} IoT{stats.get('iot_records',0)}")
    
    # 10. 插入新IoT数据
    iot_count = insert_iot_data()
    log.append(f"📊 IoT数据: 新增{iot_count}条 → 累计{stats.get('iot_records',0)+iot_count}")
    
    return log

def main():
    print(f"{'='*60}")
    print(f"EPB Assistant 5角色机器人启动")
    print(f"{'='*60}")
    print(f"角色: 📢公众·张市民 / 🏭企业·李经理 / 🚔执法·王执法 / 👁️监管·赵监管 / 🏛️政府·孙主任")
    print(f"周期: 每60秒一轮")
    print(f"{'='*60}")
    
    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"\n--- 第{cycle}轮 [{ts}] ---")
        try:
            logs = run_robot_cycle()
            for line in logs:
                print(f"  {line}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print(f"  下次运行: 60秒后")
        time.sleep(60)

if __name__ == '__main__':
    main()
