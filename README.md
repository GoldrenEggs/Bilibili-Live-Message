# Bilibili Live Message

#本库已过时，请使用[Bliveir](https://github.com/GoldrenEggs/BiLiveir)

使用方法请参考 [main.py](main.py)，或者看下文

消息的json格式请参考 [PackJson](PackJson)，如果你知道了某个json中的内容代表了什么，麻烦告诉我一声

`__handle_msg` 函数中有一行注释掉的代码，把他取消注释可以将未知的包保存在文件中，如果发现新的CMD也麻烦告诉我一声

目前 [log.py](log.py) 有问题，不能用，我还没办法安全结束进程

[api.py](api.py) 目前只能发包，不能收包，之后再写

---

**使用方法**

1. 导入Message类 `from bilibili_live_message import Message`
2. 创建Message类对象，并填入房间号 `message = Message(123)`
3. 定义消息处理方法，必须传入一个\<class dict>参数，例：
    ```
    def danmu_msg(msg: dict):
        print(f'{msg["info"][2][1]}: {msg["info"][1]}')
    ```
4. 使用以下随便哪种方法导入消息处理方法
    - `message.cmd['MESSAGE_CMD'] = function`
    - `message.set_function('MESSAGE_CMD', function)`
    - `message.set_function_dict({'MESSAGE_CMD': function, ...})`

       当然，function也可以用lambda表达式代替。
5. 你也可以设置在控制台打印哪些消息

    消息类型：

    - Link：链接消息
    - Error：错误消息
    - GetPack：接收包消息。
   
   例：`message.console_print('Link','GetPack')`
6. 使用 `Message.start()` 方法开始获取直播间信息，本类会创建一个子线程执行，不产生阻塞。
7. 使用 `Message.stop()` 方法停止获取信息。

---

**已知消息类型**

- [DANMU_MSG](PackJson/DANMU_MSG.json)：弹幕
- [INTERACT_WORD](PackJson/INTERACT_WORD.json)：入场消息
- [WATCHED_CHANGE](PackJson/WATCHED_CHANGE.json)：观看过的人数
- [SEND_GIFT](PackJson/SEND_GIFT.json)：礼物
- [COMBO_SEND](PackJson/COMBO_SEND.json)：连续投喂礼物
- [GUARD_BUY](PackJson/GUARD_BUY.json)：上船
- [USER_TOAST_MSG](PackJson/USER_TOAST_MSG.json)：续费船
- [ENTRY_EFFECT](PackJson/ENTRY_EFFECT.json)：入场特效
- [SUPER_CHAT_MESSAGE](PackJson/SUPER_CHAT_MESSAGE.json)：醒目留言
- [WIDGET_BANNER](PackJson/WIDGET_BANNER.json)：活动横幅

---

**其他**

- 可以使用链式表达，例：

    `Message.console_print('Link).set_function('DANMU_MSG': function).start()`

---

**注意事项**

1. `HEART_BEAT_REPLY` 与 `AUTH_REPLY` 是本项目自定义的指令，请不要作为其他项目的参考，二者皆不存在于 bilibili 官方 api 回复中。
2. 别忘了导入 `websocket` 与 `websocket-client` 库。
3. [bilibili_live_message](bilibili_live_message.py) 中的 `MessageCmd` 类还没写全，你可以自己添加一下，在 `cmd_tuple` 中添加新的字符串就行了。
