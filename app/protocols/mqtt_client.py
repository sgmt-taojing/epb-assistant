"""MQTT 客户端 — 用于用电监控等IoT设备数据接入"""
import json, time, logging

logger = logging.getLogger(__name__)

class MockMQTTClient:
    """模拟MQTT客户端（无paho-mqtt依赖时使用）"""
    def __init__(self, host='localhost', port=1883):
        self.host = host
        self.port = port
        self.subscriptions = {}
        self.connected = False
    
    def connect(self):
        logger.info(f'MQTT connecting to {self.host}:{self.port}')
        self.connected = True
        return True
    
    def disconnect(self):
        self.connected = False
    
    def subscribe(self, topic, callback):
        self.subscriptions[topic] = callback
        logger.info(f'Subscribed: {topic}')
    
    def publish(self, topic, payload):
        logger.info(f'Publish to {topic}: {payload}')
    
    def message_callback(self, topic, payload):
        """模拟收到消息"""
        if topic in self.subscriptions:
            self.subscriptions[topic](topic, payload)

# 设备数据格式
def parse_device_data(payload):
    """解析设备上报的JSON数据"""
    try:
        data = json.loads(payload)
        return {
            'device_id': data.get('deviceId'),
            'timestamp': data.get('timestamp', str(int(time.time()))),
            'params': data.get('params', {}),
            'quality': data.get('quality', 'normal')
        }
    except Exception as e:
        logger.error(f'Parse error: {e}')
        return None

if __name__ == '__main__':
    client = MockMQTTClient()
    client.connect()
    
    # 模拟用电监控数据
    test_payload = json.dumps({
        'deviceId': 'PWR-001',
        'timestamp': str(int(time.time())),
        'params': {'power': 285, 'voltage': 380, 'current': 42},
        'quality': 'normal'
    })
    
    client.subscribe('devices/PWR-001/data', lambda t, p: print(f'Received: {parse_device_data(p)}'))
    client.message_callback('devices/PWR-001/data', test_payload)
