"""设备管理器 — 统一管理IoT设备接入、心跳、数据采集"""
import time, json, logging, threading
from app.models import get_db

logger = logging.getLogger(__name__)

class DeviceManager:
    def __init__(self):
        self.devices = {}  # device_id → {conn, last_heartbeat, status}
    
    def register_device(self, device_id, device_type, protocol, ip, params, interval=5):
        """注册设备"""
        self.devices[device_id] = {
            'type': device_type,
            'protocol': protocol,
            'ip': ip,
            'params': params,
            'interval': interval,
            'last_heartbeat': time.time(),
            'status': 'online'
        }
        logger.info(f'Device registered: {device_id} ({protocol}://{ip})')
    
    def receive_data(self, device_id, param, value, timestamp=None):
        """接收设备数据并写入数据库"""
        if device_id not in self.devices:
            logger.warning(f'Unknown device: {device_id}')
            return False
        
        ts = timestamp or time.strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db()
        conn.execute(
            'INSERT INTO iot_data (device_id, param, value, timestamp, quality) VALUES (?,?,?,?,?)',
            (device_id, param, value, ts, 'normal')
        )
        self.devices[device_id]['last_heartbeat'] = time.time()
        conn.commit()
        conn.close()
        return True
    
    def check_heartbeat(self, timeout=300):
        """检查设备心跳，超时标记离线"""
        now = time.time()
        for dev_id, dev in self.devices.items():
            if now - dev['last_heartbeat'] > timeout:
                dev['status'] = 'offline'
                logger.warning(f'Device timeout: {dev_id}')
    
    def get_device_history(self, device_id, param, hours=24):
        """查询设备历史数据"""
        conn = get_db()
        rows = conn.execute(
            'SELECT * FROM iot_data WHERE device_id=? AND param=? AND timestamp >= datetime("now", "-{} hours") ORDER BY timestamp'.format(hours),
            (device_id, param)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

# 全局单例
device_manager = DeviceManager()

if __name__ == '__main__':
    dm = DeviceManager()
    dm.register_device('IOT-W001', 'water_quality', 'hj212', '192.168.1.101', ['pH','COD','NH3N'], 5)
    dm.receive_data('IOT-W001', 'pH', 7.2)
    dm.receive_data('IOT-W001', 'COD', 28.5)
    print(f'Devices: {len(dm.devices)}')
    print(f'IOT-W001 status: {dm.devices["IOT-W001"]["status"]}')
