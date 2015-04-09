class DES:
    import tables
    import collections

    _data = bytes()
    key = bytes()

    @property
    def dataBytes(self):
        return self._data

    @dataBytes.setter
    def data(self, value):
        self._data = value

    @dataBytes.deleter
    def data(self):
        del self._data

    @property
    def dataList(self):
        return self.bytes2list(self._data)

    @dataList.setter
    def dataList(self, value):
        self._data = self.list2bytes(value)

    @dataList.deleter
    def dataList(self):
        del self._data


    def __init__(self, data=bytes(), key=bytes()):
        self._data = data
        self.key = key

    def encode(self, cycles=16):
        self.dataList = self.permutation(self.dataList, self.tables.ip)
        self.feistel_network(cycles=cycles)
        self.dataList = self.permutation(self.dataList, self.tables.pi)

    def decode(self):
        self.dataList = self.permutation(self.dataList, self.tables.ip)
        self.feistel_network(decode=True)
        self.dataList = self.permutation(self.dataList, self.tables.pi)


    def feistel_network(self, cycles = 16, decode=False):
        r = self.dataList[:32]
        l = self.dataList[32:]

        l_old = l.copy()
        r_old = r.copy()

        for i in range(0, cycles):
            ## Rn = L(n-1) + f(R(n-1), K(n))
            key = (15 - i) if decode else i
            f = self.F(r_old, key)  # f(R(n-1), K(n))
            l = r_old.copy()
            r = list()
            for j in range(0, 32):
                r += [l_old[j] != f[j]]  # XOR
            l_old = l.copy()
            r_old = r.copy()

        rl = l + r
        self.dataList = rl
        return rl

    def F(self, r, n):
        r0 = self.permutation(r, self.tables.E)
        kn = self.K(n)
        xor = list()
        for i in range(0, 48):
            xor += [r0[i] != kn[i]]
        # print(self.list2str(xor))
        res = list()
        for i in range(7, -1, -1):
            byte = xor[i * 6: (i + 1) * 6]
            addr = (byte[1] + byte[2] * 2 + byte[3] * 4 + byte[4] * 8) + (byte[0] + byte[5] * 2) * 16
            s = self.tables.S[7 - i][addr]
            res = self.dec2list(s, 4) + res
        #print(self.list2str(res))

        res = self.permutation(res, self.tables.P)
        #print(self.list2str(res))
        return res

    def dec2list(self, val, bits):
        s = str(bin(val)).replace("0b", "").zfill(bits)
        res = list()
        for i in range(1, len(s) + 1):
            res += [s[-i] == "1"]
        return res

    def permutation(self, input, table):
        return [input[-i] for i in reversed(table)]

    def K(self, n):
        key = self.bytes2list(self.key)

        keyShort = list()

        for i in self.tables.PC1:
            keyShort = [key[-i]] + keyShort

        ci = keyShort[:28];
        di = keyShort[28:];

        for i in self.tables.KshiftEncode[:n + 1]:
            ci = self.rotate(ci, - i)  # shift right because lowest bit is on the left side
            di = self.rotate(di, - i)  # shift right because lowest bit is on the left side

        return self.permutation(ci + di, self.tables.PC2)


    def bytes2list(self, data=bytes()):
        res = list()
        for byte in data:
            for i in range(0, 8):
                res.append((int(byte) >> i) % 2 == 1)
        return res

    def list2bytes(self, data):
        res = str(encoding="latin-1")
        for i in range(0, len(data)):
            if (i % 8 == 0):
                num = 0;
                j = 0;
            if (data[i]):
                num |= 2 ** j
            if (j == 7 or i == (len(data) - 1)):
                res += chr(num)
            j += 1
        return bytes(res, 'latin-1')

    def rotate(self, l, y=1):
        if len(l) == 0:
            return l
        y = y % len(l)  # Why? this works for negative y
        return l[y:] + l[:y]

    def list2str(self, list):
        return (str(list[::-1])
            .replace("True", "1")
            .replace("False", "0")
            .replace(" ", "")
            .replace(",", "")
        )

'''
dd = DES(bytes(str(12345678), encoding="latin-1"))
dd.dataList = [True, True, True, True, False, True, True, True, True, False, True, True, False, False, True, True, True,
               True, False, True, False, True, False, True, True, False, False, True, False, False, False, True, True,
               True, True, False, False, True, True, False, True, False, True, False, False, False, True, False, True,
               True, False, False, False, True, False, False, True, False, False, False, False, False, False, False]
print("Data:\n", dd.list2str(dd.dataList))
dd.key = dd.list2bytes(
    [True, False, False, False, True, True, True, True, True, True, True, True, True, False, True, True, False, False,
     True, True, True, True, False, True, True, True, False, True, True, False, False, True, True, False, False, True,
     True, True, True, False, True, True, True, False, True, False, True, False, False, False, True, False, True, True,
     False, False, True, True, False, False, True, False, False, False])
print("Key:\n", dd.list2str(dd.bytes2list(dd.key)))
dd.encode()
print("Encoded\n", dd.list2str(dd.dataList))
dd.decode()
print("Decoded\n", dd.list2str(dd.dataList))
'''
