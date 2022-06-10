import time
from struct import pack, unpack
import zlib

from bilibili_web_header import Header


# 获取当前时间
def get_time():
    return time.strftime('[%H:%M:%S]', time.localtime())


# 保存消息
def save_log(msg: bytes, info: str = ''):
    with open(time.strftime(f'logs/%Y-%m-%d_%H-%M-%S{info}', time.localtime()), 'wb') as f:
        f.write(msg)


# 发送消息添加头部
def encode(msg: str, op: int, seq: int) -> str:
    data = msg.encode('utf-8')
    packet_len = pack('>i', 16 + len(data))
    return packet_len + pack('>h', 16) + pack('>h', 0) + pack('>i', op) + pack('>i', seq) + data


def split_msg(message: bytes) -> list:
    msg_list = []

    def recurse_split_msg(msg: bytes):
        header = Header(msg[:16])
        if header[0] != len(msg):
            recurse_split_msg(msg[:header[0]])
            recurse_split_msg(msg[header[0]:])
            return None
        if header[3] == 3:
            msg_list.append(b'\x00\x00' + msg[4:16] + b'{"cmd":"HEART_BEAT_REPLY","data":{"count":' + msg[16:] + b'}}')
        elif header[3] == 5:
            if header[2] == 2:
                recurse_split_msg(zlib.decompress(msg[16:]))
                return None
            msg_list.append(msg)
        elif header[3] == 8:
            msg_list.append(b'\x00\x00' + msg[4:16] + b'{"cmd":"AUTH_REPLY","data":' + msg[16:] + b'}')

    recurse_split_msg(message)
    return msg_list
