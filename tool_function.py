import time
from struct import pack


# 获取当前时间
def get_time():
    return time.strftime('[%H:%M:%S] ', time.localtime())


# 保存消息
def save_log(msg: bytes, info: str = ''):
    with open(time.strftime(f'logs/%Y-%m-%d_%H-%M-%S{info}', time.localtime()), 'wb') as f:
        f.write(msg)


# 发送消息添加头部
def encode(msg: str, op: int, seq: int) -> str:
    data = msg.encode('utf-8')
    packet_len = pack('>i', 16 + len(data))
    return packet_len + pack('>h', 16) + pack('>h', 0) + pack('>i', op) + pack('>i', seq) + data
