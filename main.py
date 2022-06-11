import zlib
from struct import unpack
import json
import threading
from time import sleep
import os.path

import websocket

from bilibili_live_web_header import Header
from tool_function import get_time, save_log, encode, split_msg, write_reference
from data_cmd import cmd

sequence = 0
# roomid = 4069612  # GoldenEggs
roomid = 9015372  # 不知道是谁


# 处理接收到的消息
def handle_msg(msg: bytes):
    data = json.loads(str(msg, encoding='utf-8'))
    try:
        write_reference(data)
        cmd[data['cmd']](data)
    except KeyError:
        print(f'\033[31m{get_time()} 未知命令: {data["cmd"]}\033[0m')
        # save_log(msg, f'_UnknownCmd_{data["cmd"]}')


# 发送认证包
def send_auth(ws):
    global sequence
    sequence += 1
    ws.send(encode('{"roomid":%d}' % roomid, 7, sequence))
    return True if ws.recv()[16:] == b'{"code":0}' else False


# 发送心跳包
def send_heartbeat(ws):
    sleep(3)
    while True:
        print(f'{get_time()} 发送心跳包')
        global sequence
        sequence += 1
        ws.send(encode('', 2, sequence))
        sleep(30)


# 接收并处理消息
def recv_msg(ws):
    while True:
        message = ws.recv()
        msg_list = split_msg(message)
        for msg in msg_list:
            handle_msg(msg[16:])


def main():
    webs = websocket.create_connection("ws://broadcastlv.chat.bilibili.com:2244/sub")
    if send_auth(webs):
        print(f'{get_time()} 认证成功')
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
