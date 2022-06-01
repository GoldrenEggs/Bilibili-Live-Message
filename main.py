import websocket
import zlib
from struct import pack, unpack
import json
import time
import threading
from time import sleep

sequence = 0


# 获取当前时间
def get_time():
    return time.strftime('[%H:%M:%S] ', time.localtime())


# 保存消息
def save_log(msg: bytes, info: str = ''):
    with open(time.strftime(f'%Y-%m-%d_%H-%M-%S{info}', time.localtime()), 'wb') as f:
        f.write(msg)


# 发送消息添加头部
def encode(msg: str, op: int, seq: int):
    data = msg.encode('utf-8')
    packet_len = pack('>i', 16 + len(data))
    return packet_len + pack('>h', 16) + pack('>h', 0) + pack('>i', op) + pack('>i', seq) + data


# 处理接收到的消息
def handle_msg(msg: bytes):
    data = json.loads(str(msg, encoding='utf-8'))
    if data['cmd'] == 'DANMU_MSG':
        print(f'{get_time()}{data["info"][2][1]}: {data["info"][1]}')
    else:
        print(f'{get_time()}未知命令: {data["cmd"]}')
        save_log(msg, f'_UnknownCmd_{data["cmd"]}')


# 发送认证包
def send_auth(ws: websocket.WebSocketApp):
    global sequence
    sequence += 1
    ws.send(encode('{"roomid":4069612}', 7, sequence))
    if ws.recv()[16:] == b'{"code":0}':
        return True
    return False


# 发送心跳包
def send_heartbeat(ws: websocket.WebSocketApp):
    while True:
        sleep(30)
        print(f'{get_time()}发送心跳包')
        global sequence
        sequence += 1
        ws.send(encode('', 2, sequence))


# 接收并处理传入消息
def recv_msg(ws: websocket.WebSocketApp):
    while True:
        msg = ws.recv()
        if unpack('>i', msg[0:4])[0] != len(msg):
            # 一个包多条命令
            # 没见过，见过再补
            print('一个包多条命令')
            save_log(msg, ' 一个包多条命令')
        else:
            if unpack('>i', msg[8:12])[0] == 3:
                # 心跳包回复
                print(f'{get_time()}心跳包回复: {unpack(">i", msg[16:])[0]}')
            elif unpack('>i', msg[8:12])[0] == 5:
                # 普通包(命令)
                if unpack('>h', msg[6:8])[0] == 0:
                    # 普通包不压缩
                    handle_msg(msg[16:])
                elif unpack('>h', msg[6:8])[0] == 1:
                    # 心跳&认证包不压缩
                    # 没见过，见过再补
                    print(f'{get_time()}心跳&认证包不压缩')
                    save_log(msg, ' 心跳&认证包不压缩')
                elif unpack('>h', msg[6:8])[0] == 2:
                    # 普通包使用zlib压缩
                    msg_decompress = zlib.decompress(msg[16:])
                    if unpack('>i', msg_decompress[:4])[0] == len(msg_decompress):
                        # 解压后单条命令
                        handle_msg(msg_decompress[16:])
                    else:
                        # 解压后多条命令
                        split_not_done = True
                        data_len2 = 0
                        while split_not_done:
                            data_len1 = unpack('>i', msg_decompress[data_len2:data_len2 + 4])[0]
                            data = msg_decompress[data_len2 + 16:data_len2 + data_len1]
                            handle_msg(data)
                            data_len2 += data_len1
                            if data_len2 == len(msg_decompress):
                                split_not_done = False
                elif unpack('>h', msg[6:8])[0] == 3:
                    # 普通包正文使用brotli压缩,解压为一个带头部的协议0普通包
                    # 没见过，见过再补
                    print(f'{get_time()}普通包正文使用brotli压缩,解压为一个带头部的协议0普通包')
                    save_log(msg, ' brotli压缩')
            else:
                # 其他包，没见过，见过再补
                print(f'{get_time()}其他包, 操作码: {unpack(">i", msg[8:12])[0]}')
                save_log(msg, f' 其他包 操作码: {unpack(">i", msg[8:12])[0]}')


def main():
    webs = websocket.create_connection("ws://broadcastlv.chat.bilibili.com:2244/sub")
    if send_auth(webs):
        print(f'{get_time()}认证成功')
        threading.Thread(target=send_heartbeat, args=(webs,)).start()
        threading.Thread(target=recv_msg, args=(webs,)).start()
    else:
        print('认证失败')
        webs.close()


if __name__ == '__main__':
    main()
