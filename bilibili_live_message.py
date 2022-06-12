import json
import threading
import zlib
from os.path import isfile
from time import sleep, strftime, localtime
from struct import pack, unpack

import websocket


# 获取当前时间
def get_time():
    return strftime('[%H:%M:%S]', localtime())


# 为消息添加时间头
def time_print(msg: str):
    print(get_time() + ' ' + msg)


# 为消息添加头部
def encode(msg: str, op: int, seq: int) -> str:
    data = msg.encode('utf-8')
    packet_len = pack('>i', 16 + len(data))
    return packet_len + pack('>h', 16) + pack('>h', 0) + pack('>i', op) + pack('>i', seq) + data


# 解码消息
def split_msg(message: bytes) -> list:
    msg_list = []

    def iterate_msg(msg: bytes):
        header = Header(msg[:16])
        if header[0] != len(msg):
            iterate_msg(msg[:header[0]])
            iterate_msg(msg[header[0]:])
            return None
        if header[3] == 3:
            msg_list.append(b'\x00\x00\00\x00' + msg[4:16] + b'{"cmd":"HEART_BEAT_REPLY","data":{"count":'
                            + bytes(str(unpack('>i', msg[16:])[0]), encoding='utf-8') + b'}}')
        elif header[3] == 5:
            if header[2] == 2:
                iterate_msg(zlib.decompress(msg[16:]))
                return None
            msg_list.append(msg)
        elif header[3] == 8:
            msg_list.append(b'\x00\x00\x00\x00' + msg[4:16] + b'{"cmd":"AUTH_REPLY","data":' + msg[16:] + b'}')

    iterate_msg(message)
    return msg_list


# 参考json写入文件
def write_reference(d: dict):
    if not isfile(f'Logs/Json Reference/{d["cmd"]}.json'):
        with open(f'Logs/Json Reference/{d["cmd"]}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=4))
        print('\033[34m新增json参考文本已写入到文件\033[0m')


class Message:
    sequence = 0

    def __init__(self, roomid: int):
        self.webs = websocket.create_connection("ws://broadcastlv.chat.bilibili.com:2244/sub")
        self.roomid = roomid
        self.cmd = MessageCmd()
        self.heart_beat_thread = None
        self.recv_msg_thread = None
        self.__is_stop = False
        self.__console_link_print = False
        self.__console_error_print = False

    # 发送认证包
    def __send_auth(self):
        if self.__console_link_print:
            print(f'\033[34m{get_time()} 发送认证包\033[0m')
        self.sequence += 1
        self.webs.send(encode('{"roomid":%d}' % self.roomid, 7, self.sequence))
        return True if self.webs.recv()[16:] == b'{"code":0}' else False

    # 发送心跳包
    def __send_heartbeat(self):
        sleep(3)
        while not self.__is_stop:
            if self.__console_link_print:
                print(f'\033[34m{get_time()} 发送心跳包\033[0m')
            self.sequence += 1
            self.webs.send(encode('', 2, self.sequence))
            sleep(30)

    # 处理接收到的消息
    def __handle_msg(self, msg: bytes):
        msg_dict = json.loads(str(msg, encoding='utf-8'))
        try:
            # write_reference(msg_dict)
            self.cmd[msg_dict['cmd']](msg_dict)
        except KeyError:
            if self.__console_error_print:
                print(f'\033[31m{get_time()} 收到未知命令: {msg_dict["cmd"]}\033[0m')

    # 接收并处理消息
    def __recv_msg(self):
        while not self.__is_stop:
            message = self.webs.recv()
            msg_list = split_msg(message)
            for msg in msg_list:
                self.__handle_msg(msg[16:])

    # 维持进程
    def __keep_alive(self):
        while not self.__is_stop:
            sleep(0.5)

    def console_print(self, *args):
        for name in args:
            if name not in ('Link', 'Error', 'GetPack'):
                raise Exception(f"错误的打印类型：{name}, 可能的类型：'Link', 'Error', 'GetPack'")
        if 'Link' in args:
            self.__console_link_print = True
            self.cmd.console_link_print = True
        else:
            self.__console_link_print = False
            self.cmd.console_link_print = False
        if 'Error' in args:
            self.__console_error_print = True
        else:
            self.__console_error_print = False
        if 'GetPack' in args:
            self.cmd.console_get_pack_print = True
        else:
            self.cmd.console_get_pack_print = False
        return self

    def start(self):
        self.__is_stop = False
        if self.__send_auth():
            if self.__console_link_print:
                print(f'\033[34m{get_time()} 认证成功\033[0m')
            self.heart_beat_thread = threading.Thread(target=self.__send_heartbeat, daemon=True)
            self.heart_beat_thread.start()
            self.recv_msg_thread = threading.Thread(target=self.__recv_msg, daemon=True)
            self.recv_msg_thread.start()
            threading.Thread(target=self.__keep_alive).start()
        else:
            self.webs.close()
            raise Exception('认证失败')
        return self

    def stop(self):
        self.__is_stop = True
        return self


class MessageCmd:
    def __init__(self):
        self.cmd = {'DANMU_MSG': self.__get_pack,  # 弹幕
                    'SEND_GIFT': self.__get_pack,  # 礼物
                    'COMBO_SEND': self.__get_pack,  # 礼物连击
                    'NOTICE_MSG': self.__get_pack,  # 舰长续费（可能）
                    'SUPER_CHAT_MESSAGE': self.__get_pack,  # 氪金弹幕
                    'SUPER_CHAT_MESSAGE_JPN': self.__get_pack,  # 也是氪金弹幕
                    'ROOM_REAL_TIME_MESSAGE_UPDATE': self.__get_pack,  # 粉丝变化
                    'INTERACT_WORD': self.__get_pack,  # 直播间专属标签（可能）
                    'STOP_LIVE_ROOM_LIST': self.__get_pack,  # 停止房间列表，作用未知
                    'WATCHED_CHANGE': self.__get_pack,  # 直播观看人数变化
                    'ONLINE_RANK_COUNT': self.__get_pack,  # 氪金榜
                    'ONLINE_RANK_V2': self.__get_pack,  # 氪金榜
                    'ENTRY_EFFECT': self.__get_pack,  # 入场特效（可能）
                    'HOT_RANK_CHANGED': self.__get_pack,  # 主播热度
                    'HOT_RANK_CHANGED_V2': self.__get_pack,  # 主播热度
                    'ONLINE_RANK_TOP3': self.__get_pack,  # 氪金榜前三变动
                    'VOICE_JOIN_LIST': self.__get_pack,  # 未知
                    'VOICE_ROOM_COUNT_INFO': self.__get_pack,  # 未知
                    'WIDGET_BANNER': self.__get_pack,  # bilibili活动横幅（可能）
                    'COMMON_NOTICE_DANMAKU': self.__get_pack,  # 未知
                    'LIVE': self.__get_pack,  # 未知
                    'PREPARING': self.__get_pack,  # 未知，只有一个roomid
                    'GUARD_BUY': self.__get_pack,  # 上船
                    'USER_TOAST_MSG': self.__get_pack,  # 续费船
                    'LIVE_INTERACTIVE_GAME': self.__get_pack,  # 直播互动游戏，不知道是什么东西

                    'HEART_BEAT_REPLY': self.__heart_beat_reply,  # 自定义包：心跳包回复
                    'AUTH_REPLY': self.__get_pack,  # 自定义包：认证包回复
                    }
        self.console_get_pack_print = False
        self.console_link_print = False

    def __getitem__(self, item: str):
        return self.cmd[item]

    def __setitem__(self, key: str, value):
        self.cmd[key] = value

    def __get_pack(self, msg_dict: dict):
        if self.console_get_pack_print:
            print(f'\033[30m{get_time()} 收到包：{msg_dict["cmd"]}\033[0m')

    def __heart_beat_reply(self, msg_dict: dict):
        if self.console_link_print:
            print(f'\033[34m{get_time()} 收到心跳包回复：{msg_dict["data"]["count"]}\033[0m')

    def __auth_reply(self, msg_dict: dict):
        if self.console_link_print:
            print(f'\033[34m{get_time()} 收到认证包回复：{msg_dict["data"]["code"]}\033[0m')

    def set_function(self, name: str, func):
        self.cmd[name] = func
        return self

    def set_function_dict(self, func_dict: dict):
        for name, func in func_dict.items():
            self.cmd[name] = func


class Header:
    index = (4, 6, 8, 12, 16)
    names = ('length', 'header_length', 'zlib', 'pack', 'sequence')

    def __init__(self, string: bytes):
        if len(string) < 16:
            raise Exception(f'文件头长度小于16位，当前长度：{len(string)}，内容：{string}')
        self.string = string
        self.header_list = []
        for e, i in enumerate(self.index):
            self.header_list.append(string[0 if e == 0 else self.index[e - 1]:i])

    def __getitem__(self, item: int):
        temp = self.header_list[item]
        return unpack('>i' if len(temp) == 4 else '>h', temp)[0]

    def __str__(self):
        string_list = []
        for i in range(5):
            if i in (0, 3, 4):
                string_list.append(f'{self.names[i]}:{unpack(">i", self.header_list[i])[0]}')
            else:
                string_list.append(f'{self.names[i]}:{unpack(">h", self.header_list[i])[0]}')
        return ', '.join(string_list)
