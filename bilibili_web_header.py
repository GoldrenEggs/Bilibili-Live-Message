from struct import unpack


class HeaderError(Exception):
    def __init__(self, error_info):
        super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info

    __module__ = 'builtins'


class Header:
    index = (4, 6, 8, 12, 16)
    names = ('length', 'header_length', 'zlib', 'pack', 'sequence')

    def __init__(self, string: bytes):
        if len(string) < 16:
            raise HeaderError(f'文件头长度小于16位，当前长度：{len(string)}，内容：{string}')
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


if __name__ == '__main__':
    test_bytes = b'\x00\x00\x00d\x00\x10\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00'
    test_bytes2 = b'nmslasdafsd5ghet'
    header = Header(test_bytes)
    # header = Header(test_bytes2)
    print(header)
