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
    print(f'{get_time()} {msg}')


# 为消息添加头部
def encode(msg: str, op: int, seq: int) -> bytes:
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
            msg_list.append(b'\x00\x00\00\x00' + msg[4:16] + b'{"cmd":"HEART_BEAT_REPLY","Data":{"count":'
                            + bytes(str(unpack('>i', msg[16:])[0]), encoding='utf-8') + b'}}')
        elif header[3] == 5:
            if header[2] == 2:
                iterate_msg(zlib.decompress(msg[16:]))
                return None
            msg_list.append(msg)
        elif header[3] == 8:
            msg_list.append(b'\x00\x00\x00\x00' + msg[4:16] + b'{"cmd":"AUTH_REPLY","Data":' + msg[16:] + b'}')

    iterate_msg(message)
    return msg_list


# 参考json写入文件
def write_reference(d: dict):
    if not isfile(f'Logs/Json Reference/{d["cmd"]}.json'):
        with open(f'Logs/Json Reference/{d["cmd"]}.json', 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=4)
            # f.write(json.dumps(d, ensure_ascii=False, indent=4))
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
        return self.webs.recv()[16:] == b'{"code":0}'

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
        self.__console_error_print = 'Error' in args
        self.cmd.console_get_pack_print = 'GetPack' in args
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
    cmd_names = (
        'COMBO_SEND',  # 连续礼物
        'COMMON_NOTICE_DANMAKU',
        'DANMU_MSG',  # 弹幕消息
        'ENTRY_EFFECT',  # 入场特效
        'FULL_SCREEN_SPECIAL_EFFECT',
        'GUARD_BUY',  # 上船
        'HOT_RANK_CHANGED',
        'HOT_RANK_CHANGED_V2',
        'HOT_RANK_SETTLEMENT',
        'HOT_RANK_SETTLEMENT_V2',
        'HOT_ROOM_NOTIFY',
        'INTERACT_WORD',  # 入场消息
        'LIVE_INTERACTIVE_GAME',
        'NOTICE_MSG',  # 昂贵礼物投喂全直播间通知
        'ONLINE_RANK_COUNT',
        'ONLINE_RANK_TOP3',
        'ONLINE_RANK_V2',
        'PREPARING',
        'ROOM_BLOCK_MSG',  # 禁言（大概）
        'ROOM_REAL_TIME_MESSAGE_UPDATE',
        'SEND_GIFT',  # 礼物
        'SPECIAL_GIFT',  # 特殊礼物
        'STOP_LIVE_ROOM_LIST',
        'SUPER_CHAT_MESSAGE',  # 醒目留言
        'SUPER_CHAT_MESSAGE_DELETE',  # 删除醒目留言
        'SUPER_CHAT_MESSAGE_JPN',  # 还是醒目留言，但是汉奸
        'USER_TOAST_MSG',  # 自动续费大航海（可能）
        'VOICE_JOIN_LIST',
        'VOICE_JOIN_ROOM_COUNT_INFO',
        'VOICE_JOIN_STATUS',
        'WATCHED_CHANGE',  # 观看人数变化
        'WIDGET_BANNER',  # 活动横幅（可能）
        'AUTH_REPLY',  # 认证包回复（自定义包回复）
        'HEART_BEAT_REPLY',  # 心跳包回复（自定义包回复）
    )

    def __init__(self):
        self.cmd = {key: self.__get_pack for key in self.cmd_names}
        self.cmd['HEART_BEAT_REPLY'] = self.__heart_beat_reply
        self.cmd['AUTH_REPLY'] = self.__auth_reply
        self.console_get_pack_print = False
        self.console_link_print = False

    def __getitem__(self, item: str):
        return self.cmd[item]

    def __setitem__(self, key: str, value):
        self.cmd[key] = value

    def __delitem__(self, key):
        self.cmd[key] = self.__get_pack

    def __get_pack(self, msg_dict: dict):
        if self.console_get_pack_print:
            print(f'\033[30m{get_time()} 收到包：{msg_dict["cmd"]}\033[0m')

    def __heart_beat_reply(self, msg_dict: dict):
        if self.console_link_print:
            print(f'\033[34m{get_time()} 收到心跳包回复：{msg_dict["Data"]["count"]}\033[0m')

    def __auth_reply(self, msg_dict: dict):
        if self.console_link_print:
            print(f'\033[34m{get_time()} 收到认证包回复：{msg_dict["Data"]["code"]}\033[0m')

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
        self.header_list = [string[0 if e == 0 else self.index[e - 1]: i] for e, i in enumerate(self.index)]

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
