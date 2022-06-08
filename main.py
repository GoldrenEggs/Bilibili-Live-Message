import websocket
import zlib
from struct import unpack
import json
import threading
from time import sleep
from bilibili_web_header import Header

from tool_function import *

sequence = 0
roomid = 4069612


# 处理接收到的消息
def handle_msg(msg: bytes):
    data = json.loads(str(msg, encoding='utf-8'))
    if data['cmd'] == 'DANMU_MSG':
        print(f'{get_time()}{data["info"][2][1]}: {data["info"][1]}')
    elif data['cmd'] == 'SEND_GIFT':  # 礼物
        print(
            f'{get_time()}{data["data"]["uname"]} '
            f'{data["data"]["action"]}{data["data"]["giftName"]} x{data["data"]["num"]}')
    elif data['cmd'] == 'COMBO_SEND':  # 礼物连击
        ...
    elif data['cmd'] == 'NOTICE_MSG':  # 舰长续费啥的，先存着 批站直播公告
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'SUPER_CHAT_MESSAGE':  # 氪金弹幕
        ...
    elif data['cmd'] == 'SUPER_CHAT_MESSAGE_JPN':  # 也是氪金弹幕
        ...
    elif data['cmd'] == 'ROOM_REAL_TIME_MESSAGE_UPDATE':  # 粉丝变化
        ...
    elif data['cmd'] == 'INTERACT_WORD':  # 好像是房间专属表情
        ...
    elif data['cmd'] == 'STOP_LIVE_ROOM_LIST':  # 停止房间列表，作用未知
        ...
    elif data['cmd'] == 'WATCHED_CHANGE':  # 直播观看人数变化
        ...
    elif data['cmd'] == 'ONLINE_RANK_COUNT':  # 氪金榜
        ...
    elif data['cmd'] == 'ONLINE_RANK_V2':  # 氪金榜
        ...
    elif data['cmd'] == 'ENTRY_EFFECT':  # 可能是入场特效
        ...
    elif data['cmd'] == 'HOT_RANK_CHANGED':  # 主播热度
        ...
    elif data['cmd'] == 'HOT_RANK_CHANGED_V2':  # 主播热度
        ...
    elif data['cmd'] == 'ONLINE_RANK_TOP3':  # 氪金榜前3变动
        ...
    elif data['cmd'] == 'VOICE_JOIN_LIST':  # 未知，先存
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'VOICE_JOIN_ROOM_COUNT_INFO':  # 未知，先存
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'WIDGET_BANNER':  # 好像是批站直播活动横幅
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'COMMON_NOTICE_DANMAKU':  # 好像还是批站直播活动
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'LIVE':  # 未知，先存
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'PREPARING':  # 未知，先存，只有一个roomid
        save_log(msg, f'_{data["cmd"]}')
    elif data['cmd'] == 'GUARD_BUY':  # 上船
        ...
    elif data['cmd'] == 'USER_TOAST_MSG':  # 续费船
        ...
    else:
        print(f'{get_time()}未知命令: {data["cmd"]}')
        save_log(msg, f'_UnknownCmd_{data["cmd"]}')


# 发送认证包
def send_auth(ws):
    # r = requests.get('http://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo', params={'id': roomid})
    # key = r.json()['data']['token']
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
        cmd = input()
        if cmd == 'q':
            return


if __name__ == '__main__':
    main()
