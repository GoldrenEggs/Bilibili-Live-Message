import datetime
from threading import Thread
from time import sleep


class Log:
    def __init__(self, path: str = 'Log/' + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.log'):
        self.path = path
        self.save_interval = 5.0
        self.__temp_logs = []
        self.__is_log = True
        self.__is_write = False
        self.__write_thread = Thread(target=self.__write_file_per_seconds, daemon=True)
        self.__write_thread.start()

    def log(self, text: str, level: str = 'INFO'):
        self.__temp_logs.append(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] [{level}]: {text}\n')

    def stop(self):
        self.__is_log = False
        self.__write_file()

    def __write_file(self):
        if self.__temp_logs:
            self.__is_write = True
            with open(self.path, 'a', encoding='utf-8') as f:
                for log in self.__temp_logs:
                    f.writelines(log)
            self.__is_write = False
            self.__temp_logs.clear()

    def __write_file_per_seconds(self):
        while self.__is_log:
            sleep(self.save_interval)
            self.__write_file()

    def __str__(self):
        return str(self.__temp_logs)


if __name__ == '__main__':
    a = Log()
    for i in range(11):
        a.log('奴俊嚼你妈死了', 'INFO')
        print(a)
        sleep(1)
    a.stop()
