#!/usr/bin/env python3
"""
EPB Assistant — 确定性种子数据生成器
生成企业(50) / 设备(30) / IoT时序(30设备×5min×30天=86400) 并写入 SQLite
禁用 random，使用确定性公式: (seed * factor + offset) % range
"""

import sqlite3, os, json
from datetime import datetime, timedelta

# ── 路径 ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE  = os.path.join(BASE_DIR, 'epb.db')

# ── 确定性伪随机 ──────────────────────────────────
def det(seed, factor=2654435761, offset=12345, rng=10000):
    """确定性伪随机数 [0, rng)"""
    return (seed * factor + offset) % rng

def det_float(seed, lo, hi, factor=2654435761, offset=12345, rng=1000000):
    """确定性浮点 [lo, hi)"""
    r = (seed * factor + offset) % rng
    return lo + (hi - lo) * r / rng

# ── 企业数据 ──────────────────────────────────────
CITIES = [
    ('济南', 117.0, 36.65), ('青岛', 120.38, 36.07), ('烟台', 121.39, 37.54),
    ('潍坊', 119.16, 36.70), ('临沂', 118.35, 35.05), ('淄博', 118.05, 36.78),
    ('德州', 116.36, 37.45), ('聊城', 115.99, 36.46), ('滨州', 117.97, 37.38),
    ('东营', 118.67, 37.43), ('菏泽', 115.48, 35.24), ('济宁', 116.59, 35.41),
    ('泰安', 117.09, 36.19), ('威海', 122.12, 37.51), ('日照', 119.53, 35.38),
    ('枣庄', 117.56, 34.86),
]

INDUSTRIES = [
    ('化工',     ['COD', '氨氮', 'VOCs', '总磷', '苯系物']),
    ('建材',     ['粉尘', 'SO₂', 'NOx', '噪声']),
    ('造纸',     ['COD', 'BOD₅', 'SS', '氨氮']),
    ('纺织',     ['COD', '色度', 'SS', '苯胺类']),
    ('电镀',     ['六价铬', '总镍', '总铜', '氰化物']),
    ('食品',     ['COD', 'BOD₅', '动植物油', '氨氮']),
    ('制药',     ['COD', 'TOC', '残留药物', '氨氮']),
]

DISTRCTS = ['历下区', '市中区', '槐荫区', '天桥区', '历城区', '长清区',
            '章丘区', '济阳区', '莱芜区', '钢城区', '城阳区', '黄岛区',
            '崂山区', '即墨区', '芝罘区', '福山区', '牟平区', '奎文区',
            '寒亭区', '坊子区', '兰山区', '罗庄区', '河东', '张店区',
            '淄川区', '博山区', '德城区', '东昌府区', '滨城区', '东营区',
            '牡丹区', '任城区', '泰山区', '环翠区', '东港区', '薛城区']

COMPANY_PREFIX = [
    '山东', '鲁', '齐鲁', '华鲁', '鲁能', '鲁兴', '鲁润', '鲁昌',
    '鲁化', '鲁建', '鲁纺', '鲁纸', '鲁药', '鲁食', '鲁镀', '鲁材'
]
COMPANY_SUFFIX = {
    '化工': ['化工', '化学', '化工材料', '精细化工', '化工科技'],
    '建材': ['建材', '水泥', '新型建材', '建工材料', '建材科技'],
    '造纸': ['纸业', '造纸', '纸业股份', '浆纸', '包装纸业'],
    '纺织': ['纺织', '染织', '纺织科技', '印染', '棉纺织'],
    '电镀': ['电镀', '表面处理', '金属表面处理', '电镀科技', '镀饰'],
    '食品': ['食品', '食品科技', '食品加工', '生物科技', '粮油'],
    '制药': ['制药', '药业', '医药', '制药股份', '医药科技'],
}

CREDIT_LEVELS = ['A级', 'B级', 'C级', 'D级']
RISK_LEVELS   = ['低风险', '一般风险', '中风险', '高风险']
STATUSES      = ['正常生产', '正常生产', '正常生产', '正常生产', '停产整治', '限制生产']
CONTACT_SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                    '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']
CONTACT_GIVEN   = ['伟', '强', '磊', '军', '勇', '涛', '明', '超', '刚', '平',
                   '辉', '鹏', '华', '斌', '杰', '丽', '芳', '敏', '静', '艳']

def gen_enterprises(n=50):
    """生成50条企业数据"""
    rows = []
    for i in range(n):
        seed = (i + 1) * 7
        city_idx = det(seed, 31, 0, len(CITIES))
        city = CITIES[city_idx]
        ind_idx = det(seed + 1, 17, 3, len(INDUSTRIES))
        industry = INDUSTRIES[ind_idx]
        prefix_idx = det(seed + 2, 13, 7, len(COMPANY_PREFIX))
        suffix_idx = det(seed + 3, 11, 5, len(COMPANY_SUFFIX[industry[0]]))
        name = f'{COMPANY_PREFIX[prefix_idx]}{city[0]}{COMPANY_SUFFIX[industry[0]][suffix_idx]}有限公司'
        district_idx = det(seed + 4, 19, 9, len(DISTRCTS))
        address = f'山东省{city[0]}市{DISTRCTS[district_idx]}工业大道{100 + det(seed+5,7,3,900)}号'
        lng = round(city[1] + det_float(seed + 6, -0.08, 0.08), 6)
        lat = round(city[2] + det_float(seed + 7, -0.06, 0.06), 6)
        permit = f'SD-{city[0]}-EP-{2020 + det(seed+8,3,1,6)}-{str(1000+i).zfill(4)}'
        pollutants = industry[1]
        credit = CREDIT_LEVELS[det(seed + 9, 23, 11, len(CREDIT_LEVELS))]
        risk = RISK_LEVELS[det(seed + 10, 29, 13, len(RISK_LEVELS))]
        status = STATUSES[det(seed + 11, 37, 17, len(STATUSES))]
        sname = CONTACT_SURNAMES[det(seed + 12, 41, 19, len(CONTACT_SURNAMES))]
        gname = CONTACT_GIVEN[det(seed + 13, 43, 23, len(CONTACT_GIVEN))]
        contact_person = sname + gname
        contact_phone = f'1{3 + det(seed+14,5,2,7)}{str(det(seed+15,9,4,100000000)).zfill(9)}'
        # 2025-06-01 ~ 2026-07-18
        base = datetime(2025, 6, 1)
        days_offset = det(seed + 16, 47, 29, 414)
        last_check = (base + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        mp = [f'MP-{city[0]}-{j+1}' for j in range(1 + det(seed+17, 53, 31, 4))]
        eid = f'ENT-SD-{str(i+1).zfill(3)}'
        rows.append({
            'id': eid, 'name': name, 'type': industry[0], 'address': address,
            'lng': lng, 'lat': lat, 'permit_no': permit,
            'pollutants': json.dumps([(p,) for p in pollutants], ensure_ascii=False).replace('[','[').replace('),',',').replace('[(','["').replace(')','"]').replace(']','"]') if False else json.dumps([[p] for p in pollutants], ensure_ascii=False),
            'credit_level': credit, 'risk_level': risk, 'status': status,
            'contact_person': contact_person, 'contact_phone': contact_phone,
            'last_check_date': last_check,
            'monitoring_points': json.dumps(mp, ensure_ascii=False),
        })
    return rows


# ── 设备数据 ──────────────────────────────────────
# 7类设备, ID前缀映射
DEVICE_TYPES = [
    ('water_quality',    'IOT-W', '水质在线监测仪',   ['pH', 'COD', '氨氮', '总磷', '浊度']),
    ('air_quality',      'IOT-A', '空气质量监测仪',   ['PM2.5', 'PM10', 'SO₂', 'NOx', 'O₃']),
    ('noise',            'IOT-N', '噪声监测仪',       ['Leq', 'Lmax', 'Lmin']),
    ('emission_water',   'IOT-EW','废水排放监测仪',   ['流量', 'COD', '氨氮', '总铬']),
    ('emission_gas',     'IOT-EG','废气排放监测仪',   ['SO₂', 'NOx', '烟尘', '含氧量']),
    ('power',            'IOT-P', '用电监控仪',       ['电压', '电流', '功率', '用电量']),
    ('soil',             'IOT-S', '土壤监测仪',       ['pH', '镉', '铅', '砷', '汞']),
]

VENDORS = ['聚光科技', '雪迪龙', '宇星科技', '先河环保', '中环天仪',
           '皖仪科技', '钢研纳克', '北京吉天', '上海仪电', '杭州鼎利']

def gen_devices(n=30):
    """生成30台设备, 覆盖7类"""
    rows = []
    for i in range(n):
        seed = (i + 1) * 11
        dt_idx = i % len(DEVICE_TYPES)  # 确保7类均匀覆盖
        dt = DEVICE_TYPES[dt_idx]
        prefix = dt[1]
        seq = i // len(DEVICE_TYPES) + 1
        dev_id = f'{prefix}{str(seq).zfill(3)}'
        name = f'{dt[2]}-{str(seq).zfill(3)}号'
        vendor = VENDORS[det(seed, 17, 3, len(VENDORS))]
        model = f'M{1000 + det(seed+1, 13, 7, 900)}'
        serial = f'SN{2026}{str(det(seed+2, 19, 11, 10000)).zfill(5)}'
        # 分配给企业 (每企业1~2台)
        ent_idx = det(seed + 3, 23, 13, 50)
        assigned_to = f'ENT-SD-{str(ent_idx+1).zfill(3)}'
        status = ['online', 'online', 'online', 'offline', 'maintenance'][det(seed+4, 29, 17, 5)]
        health = {
            'battery': 60 + det(seed + 5, 31, 19, 40),
            'storage_free': 1024 + det(seed + 6, 37, 23, 64512),
            'temperature': round(det_float(seed + 7, 15.0, 45.0), 1),
        }
        config = {
            'interval': 300,
            'params': dt[3],
            'threshold': 'GB-3838-2002' if dt[0] == 'water_quality' else
                         'GB-3095-2012' if dt[0] == 'air_quality' else
                         'GB-12348-2008' if dt[0] == 'noise' else
                         'GB-8978-1996' if dt[0] == 'emission_water' else
                         'GB-13271-2014' if dt[0] == 'emission_gas' else
                         'GB-T-17215-2002' if dt[0] == 'power' else
                         'GB-15618-2018',
        }
        reg_date = (datetime(2025, 1, 1) + timedelta(days=det(seed+8, 41, 29, 540))).strftime('%Y-%m-%d')
        last_active = (datetime(2026, 7, 19) - timedelta(minutes=det(seed+9, 43, 31, 1440))).strftime('%Y-%m-%dT%H:%M:%S')
        rows.append({
            'id': dev_id, 'name': name, 'type': dt[0], 'vendor': vendor,
            'model': model, 'serial_no': serial, 'assigned_to': assigned_to,
            'status': status, 'health': json.dumps(health, ensure_ascii=False),
            'config': json.dumps(config, ensure_ascii=False),
            'registered_at': reg_date, 'last_active': last_active,
        })
    return rows


# ── IoT 时序数据 ──────────────────────────────────
# 每类设备对应参数的国标合理范围 (min, max)
PARAM_RANGES = {
    # water_quality
    'pH':       (6.0, 9.0),
    'COD':      (15.0, 120.0),
    '氨氮':      (0.5, 8.0),
    '总磷':      (0.1, 1.5),
    '浊度':      (1.0, 20.0),
    # air_quality
    'PM2.5':    (10.0, 150.0),
    'PM10':     (20.0, 250.0),
    'SO₂':       (0.01, 0.30),
    'NOx':      (0.02, 0.50),
    'O₃':        (0.04, 0.20),
    # noise
    'Leq':      (45.0, 75.0),
    'Lmax':     (55.0, 90.0),
    'Lmin':     (35.0, 55.0),
    # emission_water
    '流量':      (5.0, 200.0),
    '总铬':      (0.05, 1.0),
    # emission_gas
    '烟尘':      (10.0, 80.0),
    '含氧量':    (8.0, 21.0),
    # power
    '电压':      (200.0, 240.0),
    '电流':      (5.0, 80.0),
    '功率':      (1.0, 30.0),
    '用电量':    (100.0, 2000.0),
    # soil
    '镉':        (0.05, 1.0),
    '铅':        (5.0, 100.0),
    '砷':        (5.0, 50.0),
    '汞':        (0.05, 1.5),
}

QUALITY_CODES = ['good', 'good', 'good', 'normal', 'normal', 'warning']

def gen_iot_data(devices, days=30, interval_min=5):
    """生成30天5分钟间隔的时序数据"""
    rows = []
    # 每设备的参数列表
    dev_params = {}
    for d in devices:
        cfg = json.loads(d['config'])
        dev_params[d['id']] = cfg['params']
    
    total_points = days * 24 * (60 // interval_min)  # 8640 points/device
    start = datetime(2026, 6, 19, 0, 0, 0)  # 6/19 ~ 7/18
    dev_count = 0
    for d in devices:
        did = d['id']
        params = dev_params[did]
        dev_idx = dev_count + 1
        for pi, param in enumerate(params):
            rng = PARAM_RANGES.get(param, (0.0, 100.0))
            lo, hi = rng
            base_val = lo + (hi - lo) * 0.4  # 基线在范围40%处
            amplitude = (hi - lo) * 0.3       # 波动幅度30%
            for t in range(total_points):
                ts = start + timedelta(minutes=t * interval_min)
                seed = dev_idx * 100000 + pi * 10000 + t
                # 确定性公式: 基线 + 正弦波周期波动 + 确定性噪声
                wave = (det(seed, 2654435761, 12345, 1000000) / 1000000.0 - 0.5) * amplitude
                # 添加日周期波动 (24小时)
                hour_frac = (t * interval_min) / 60.0
                day_cycle = 0.15 * amplitude * (0.5 + 0.5 * (1 if det(seed+7, 31, 13, 2000) > 1000 else -1))
                value = round(base_val + wave + day_cycle, 4)
                # 钳位到范围
                value = max(lo * 0.9, min(hi * 1.1, value))
                q = QUALITY_CODES[det(seed + 3, 17, 5, len(QUALITY_CODES))]
                rows.append((did, param, value, ts.strftime('%Y-%m-%dT%H:%M:%S'), q))
        dev_count += 1
    return rows


# ── 写入数据库 ────────────────────────────────────
def write_to_db(enterprises, devices, iot_rows):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 清空三张表
    c.execute('DELETE FROM enterprises')
    c.execute('DELETE FROM devices')
    c.execute('DELETE FROM iot_data')
    
    # 写企业
    for e in enterprises:
        c.execute('''INSERT OR REPLACE INTO enterprises
            (id, name, type, address, lng, lat, permit_no, pollutants,
             credit_level, risk_level, status, contact_person, contact_phone,
             last_check_date, monitoring_points)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (e['id'], e['name'], e['type'], e['address'], e['lng'], e['lat'],
             e['permit_no'], e['pollutants'], e['credit_level'], e['risk_level'],
             e['status'], e['contact_person'], e['contact_phone'],
             e['last_check_date'], e['monitoring_points']))
    
    # 写设备
    for d in devices:
        c.execute('''INSERT OR REPLACE INTO devices
            (id, name, type, vendor, model, serial_no, assigned_to, status,
             health, config, registered_at, last_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
            (d['id'], d['name'], d['type'], d['vendor'], d['model'], d['serial_no'],
             d['assigned_to'], d['status'], d['health'], d['config'],
             d['registered_at'], d['last_active']))
    
    # 写IoT数据 — 批量插入
    c.executemany('''INSERT INTO iot_data (device_id, param, value, timestamp, quality)
        VALUES (?,?,?,?,?)''', iot_rows)
    
    conn.commit()
    
    # 验证
    c.execute('SELECT COUNT(*) FROM enterprises')
    ent_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM devices')
    dev_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM iot_data')
    iot_count = c.fetchone()[0]
    
    conn.close()
    return ent_count, dev_count, iot_count


# ── 主流程 ────────────────────────────────────────
def main():
    print('='*60)
    print('EPB Assistant — 确定性种子数据生成')
    print(f'数据库: {DB_FILE}')
    print('='*60)
    
    print('\n[1/4] 生成企业数据 (50条)...')
    enterprises = gen_enterprises(50)
    print(f'  ✅ {len(enterprises)} 条企业')
    
    print('\n[2/4] 生成设备数据 (30台)...')
    devices = gen_devices(30)
    type_counts = {}
    for d in devices:
        type_counts[d['type']] = type_counts.get(d['type'], 0) + 1
    print(f'  ✅ {len(devices)} 台设备')
    for t, n in sorted(type_counts.items()):
        print(f'     {t}: {n}台')
    
    print('\n[3/4] 生成IoT时序数据 (30设备 × 5min × 30天)...')
    iot_rows = gen_iot_data(devices, days=30, interval_min=5)
    print(f'  ✅ {len(iot_rows):,} 条IoT数据')
    
    print('\n[4/4] 写入SQLite数据库...')
    ent_n, dev_n, iot_n = write_to_db(enterprises, devices, iot_rows)
    
    print('\n' + '='*60)
    print('✅ 种子数据生成完成!')
    print('='*60)
    print(f'  enterprises : {ent_n:>6} 条')
    print(f'  devices     : {dev_n:>6} 条')
    print(f'  iot_data    : {iot_n:>6,} 条')
    print(f'  DB文件      : {DB_FILE}')
    print(f'  DB大小      : {os.path.getsize(DB_FILE)/1024/1024:.1f} MB')
    
    # 抽样验证
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    print('\n--- 抽样验证 ---')
    c.execute('SELECT id, name, type, address FROM enterprises LIMIT 3')
    for r in c.fetchall():
        print(f'  企业 {r[0]}: {r[1]} ({r[2]}) @ {r[3]}')
    c.execute('SELECT id, name, type, assigned_to FROM devices LIMIT 5')
    for r in c.fetchall():
        print(f'  设备 {r[0]}: {r[1]} [{r[2]}] → {r[3]}')
    c.execute('SELECT device_id, param, value, timestamp FROM iot_data LIMIT 3')
    for r in c.fetchall():
        print(f'  IoT  {r[0]} {r[1]}={r[2]} @ {r[3]}')
    c.execute('SELECT COUNT(DISTINCT device_id) FROM iot_data')
    print(f'  IoT涉及设备数: {c.fetchone()[0]}')
    c.execute('SELECT MIN(timestamp), MAX(timestamp) FROM iot_data')
    r = c.fetchone()
    print(f'  IoT时间范围: {r[0]} ~ {r[1]}')
    conn.close()


if __name__ == '__main__':
    main()
