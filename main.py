import websocket
import zlib
from struct import unpack
import json
import threading
from time import sleep
from bilibili_web_header import Header

from tool_function import *
from data_cmd import cmd

sequence = 0
roomid = 4069612


# 处理接收到的消息
def handle_msg(msg: bytes):
    data = json.loads(str(msg, encoding='utf-8'))
    try:
        cmd[data['cmd']](data, msg)
    except KeyError:
        print(f'{get_time()}未知命令: {data["cmd"]}')
        save_log(msg, f'_UnknownCmd_{data["cmd"]}')


# 发送认证包
def send_auth(ws):
    global sequence
    sequence += 1
    ws.send(encode('{"roomid":%d}' % roomid, 7, sequence))
    if ws.recv()[16:] == b'{"code":0}':
        return True
    return False


# 发送心跳包
def send_heartbeat(ws):
    while True:
        sleep(30)
        print(f'{get_time()}发送心跳包')
        global sequence
        sequence += 1
        ws.send(encode('', 2, sequence))


# 接收并处理传入消息
def recv_msg(ws):
    while True:
        msg = ws.recv()
        header = Header(msg[:16])
        if header[0] != len(msg):  # 一个包多条命令
            # 没见过，见过再补
            print('一个包多条命令')
            save_log(msg, ' 一个包多条命令')
        else:
            if header[3] == 3:  # 心跳包回复
                print(f'{get_time()}心跳包回复: {unpack(">i", msg[16:])[0]}')
            elif header[3] == 5:  # 普通包(命令)
                if header[2] == 0:  # 普通包不压缩
                    handle_msg(msg[16:])
                elif header[2] == 1:  # 心跳&认证包不压缩
                    # 没见过，见过再补
                    print(f'{get_time()}心跳&认证包不压缩')
                    save_log(msg, ' 心跳&认证包不压缩')
                elif header[2] == 2:  # 普通包使用zlib压缩
                    msg_decompress = zlib.decompress(msg[16:])
                    header_decompress = Header(msg_decompress[:16])
                    if header_decompress[0] == len(msg_decompress):  # 解压后单条命令
                        handle_msg(msg_decompress[16:])
                    else:  # 解压后多条命令
                        split_not_done = True
                        data_len2 = 0
                        while split_not_done:
                            data_len1 = unpack('>i', msg_decompress[data_len2:data_len2 + 4])[0]
                            data = msg_decompress[data_len2 + 16:data_len2 + data_len1]
                            handle_msg(data)
                            data_len2 += data_len1
                            if data_len2 == len(msg_decompress):
                                split_not_done = False
                elif header[2] == 3:  # 普通包正文使用brotli压缩,解压为一个带头部的协议0普通包
                    # 没见过，见过再补
                    print(f'{get_time()}普通包正文使用brotli压缩,解压为一个带头部的协议0普通包')
                    save_log(msg, ' brotli压缩')
            else:  # 其他包，没见过，见过再补
                print(f'{get_time()}其他包, 操作码: {unpack(">i", msg[8:12])[0]}')
                save_log(msg, f' 其他包 操作码: {unpack(">i", msg[8:12])[0]}')


def main():
    webs = websocket.create_connection("ws://broadcastlv.chat.bilibili.com:2244/sub")
    if send_auth(webs):
        print(f'{get_time()}认证成功')
        threading.Thread(target=send_heartbeat, args=(webs,), daemon=True).start()
        threading.Thread(target=recv_msg, args=(webs,), daemon=True).start()
    else:
        print('认证失败')
        webs.close()
        return
    while True:
        data_cmd = input()
        if data_cmd == 'q':
            return


if __name__ == '__main__':
    main()
