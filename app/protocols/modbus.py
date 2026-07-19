"""Modbus TCP 协议 — 用于噪声/土壤等工业传感器"""
import struct, logging

logger = logging.getLogger(__name__)

class ModbusClient:
    """简化版Modbus TCP客户端"""
    def __init__(self, host='localhost', port=502):
        self.host = host
        self.port = port
        self.transaction_id = 0
    
    def read_holding_register(self, address, count=1):
        """读取保持寄存器"""
        self.transaction_id += 1
        # 实际应发送TCP报文，这里返回模拟值
        # Modbus功能码03: 读保持寄存器
        logger.info(f'Read register {address} count={count}')
        # 模拟返回值（确定性）
        base = address * 10 + 100
        return [base + i for i in range(count)]
    
    def read_input_register(self, address, count=1):
        """读取输入寄存器"""
        self.transaction_id += 1
        logger.info(f'Read input register {address} count={count}')
        base = address * 5 + 50
        return [base + i for i in range(count)]

# 寄存器映射表
REGISTER_MAP = {
    'noise': {'address': 0, 'scale': 0.1, 'unit': 'dB(A)'},
    'temperature': {'address': 1, 'scale': 0.1, 'unit': '°C'},
    'humidity': {'address': 2, 'scale': 0.1, 'unit': '%RH'},
    'pm25': {'address': 3, 'scale': 1, 'unit': 'μg/m³'},
    'pm10': {'address': 4, 'scale': 1, 'unit': 'μg/m³'},
}

def read_param(client, param_name):
    """读取指定参数"""
    if param_name not in REGISTER_MAP:
        return None
    cfg = REGISTER_MAP[param_name]
    raw = client.read_holding_register(cfg['address'])[0]
    return {
        'param': param_name,
        'value': round(raw * cfg['scale'], 2),
        'unit': cfg['unit'],
        'raw': raw
    }

if __name__ == '__main__':
    client = ModbusClient('192.168.1.50')
    for param in ['noise', 'temperature', 'humidity']:
        result = read_param(client, param)
        print(f'{param}: {result}')
