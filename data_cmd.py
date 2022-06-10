from tool_function import *


def danmu_msg(data: dict):
    print(f'{get_time()} {data["info"][2][1]}: {data["info"][1]}')


def send_gift(data: dict):
    print(f'{get_time()} {data["data"]["uname"]} '
          f'{data["data"]["action"]}{data["data"]["giftName"]} x{data["data"]["num"]}')


def combo_send(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def notice_msg(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def super_chat_message(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def super_chat_message_jpn(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def room_real_time_message_update(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def interact_word(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def stop_live_room_list(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def watched_change(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def online_rank_count(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def online_rank_v2(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def entry_effect(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def hot_rank_changed(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def hot_rank_changed_v2(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def online_rank_top3(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def voice_join_list(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def voice_join_room_count_info(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def widget_banner(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def common_notice_danmaku(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def live(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def preparing(data: dict):
    print(f'{get_time()} 已保存：{data["cmd"]}')
    return 'save'


def guard_buy(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


def user_toast_msg(data: dict):
    print(f'{get_time()} 收到包：{data["cmd"]}')


cmd = {'DANMU_MSG': danmu_msg,  # 弹幕
       'SEND_GIFT': send_gift,  # 礼物
       'COMBO_SEND': combo_send,  # 礼物连击
       'NOTICE_MSG': notice_msg,  # 舰长续费（可能）
       'SUPER_CHAT_MESSAGE': super_chat_message,  # 氪金弹幕
       'SUPER_CHAT_MESSAGE_JPN': super_chat_message_jpn,  # 也是氪金弹幕
       'ROOM_REAL_TIME_MESSAGE_UPDATE': room_real_time_message_update,  # 粉丝变化
       'INTERACT_WORD': interact_word,  # 直播间专属标签（可能）
       'STOP_LIVE_ROOM_LIST': stop_live_room_list,  # 停止房间列表，作用未知
       'WATCHED_CHANGE': watched_change,  # 直播观看人数变化
       'ONLINE_RANK_COUNT': online_rank_count,  # 氪金榜
       'ONLINE_RANK_V2': online_rank_v2,  # 氪金榜
       'ENTRY_EFFECT': entry_effect,  # 入场特效（可能）
       'HOT_RANK_CHANGED': hot_rank_changed,  # 主播热度
       'HOT_RANK_CHANGED_V2': hot_rank_changed_v2,  # 主播热度
       'ONLINE_RANK_TOP3': online_rank_top3,  # 氪金榜前三变动
       'VOICE_JOIN_LIST': voice_join_list,  # 未知
       'VOICE_ROOM_COUNT_INFO': voice_join_room_count_info,  # 未知
       'WIDGET_BANNER': widget_banner,  # bilibili活动横幅（可能）
       'COMMON_NOTICE_DANMAKU': common_notice_danmaku,  # 未知
       'LIVE': live,  # 未知
       'PREPARING': preparing,  # 未知，只有一个roomid
       'GUARD_BUY': guard_buy,  # 上船
       'USER_TOAST_MSG': user_toast_msg,  # 续费船
       }
