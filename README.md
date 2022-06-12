## BilibiliLiveDanmaku

---

使用方法请参考 [main.py](main.py)，或者看下文

接收到消息的json格式请参考 [PackJson](PackJson)

目前 [log.py](log.py) 有问题，不能用，我还没办法安全结束进程

日后准备添加api.py

---

**使用方法：**

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
