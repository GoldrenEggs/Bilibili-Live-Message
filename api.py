import socket
import threading
from time import sleep


class Api:
    host = '127.0.0.1'

    def __init__(self, port: int, listen: int = 5):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.bind((self.host, port))
        self.skt.listen(listen)
        self.listen = listen
        self.connects = []
        threading.Thread(target=self.__accept, daemon=True).start()

    def __accept(self):
        while len(self.connects) <= self.listen:
            connect, address = self.skt.accept()
            # connect_recv = threading.Thread(target=self.recv, args=(connect, address), daemon=True)
            # connect_recv.start()
            # self.connects.append((connect, address, connect_recv))
            self.connects.append((connect, address))
            print(f'{address[0]}:{address[1]} 已连接')

    def recv(self, connect: socket.socket, address: tuple):
        while True:
            data = connect.recv(1024).decode('utf-8')
            if data != '':
                self.handle_recv(address, data)

    def handle_recv(self, address, data):
        print(f'收到 {address[0]}:{address[1]} 发来的消息：{data}')

    def send(self, text: str, target: int = -1):
        if target == -1:
            for connect in self.connects:
                connect[0].send(text.encode('utf-8'))
        elif 0 <= target < len(self.connects):
            self.connects[target][0].send(text.encode('utf-8'))


if __name__ == '__main__':
    a = Api(2333)
    while True:
        a.send('amazing')
        sleep(2)
