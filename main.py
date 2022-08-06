from bilibili_live_message import Message, time_print


# 使用方法参考
# 你需要安装第三方库 websocket 与 websocket-client
def main():
    def danmu_msg(msg: dict):  # 弹幕消息处理方法
        time_print(f'{msg["info"][2][1]}: {msg["info"][1]}')

    def send_gift(msg: dict):  # 礼物消息处理方法
        time_print(f'{msg["Data"]["uname"]} '
                   f'{msg["Data"]["action"]}{msg["Data"]["giftName"]} x{msg["Data"]["num"]}')

    def guard_buy(msg: dict):  # 上船消息处理方法
        time_print(f'{msg["Data"]["username"]} 上了贼船并成为了 {msg["Data"]["gift_name"]}')

    message = Message(5050)  # 创建直播间消息类并设置直播间房间号
    message.console_print('Link', 'Error', 'GetPack')  # 设置需要打印的消息类型，Link：链接信息，Error：错误信息，GetPack：获取包信息
    message.cmd['DANMU_MSG'] = danmu_msg  # 设置弹幕消息处理方法
    message.cmd.set_function('SEND_GIFT', send_gift)  # 设置礼物消息处理方法
    cmd_dict = {
        'INTERACT_WORD': lambda msg: time_print(f'{msg["Data"]["uname"]} 进入了直播间'),  # 将进入直播间消息处理方法保存到字典中
        'GUARD_BUY': guard_buy,  # 将上船消息处理方法保存到字典中
    }
    message.cmd.set_function_dict(cmd_dict)  # 用字典的方法设置消息处理方法
    message.start()  # 开始爬取并处理直播间消息
    while True:
        cmd = input()
        if cmd == 'q':
            message.stop()
            break


if __name__ == '__main__':
    main()
