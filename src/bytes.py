def c(*opts):
    for o in opts:
        if o is not None:
            return o
    return None

class Bit:
    def __init__(self, byte, bit):
        self._byte = byte
        self._bit = bit
    
    def __bool__(self):
        return self._byte.is_bit(self._bit)
    
    def __str__(self):
        return str(bool(self))

    def set(self):
        self._byte.set_bit(self._bit)

    def clear(self):
        self._byte.clear_bit(self._bit)
    
    def flip(self):
        self._byte.flip_bit(self._bit)

class Byte:
    def __init__(self, bytes, offset):
        self._bytes = bytes
        self._offset = offset
    
    def __int__(self):
        return self._bytes[self._offset] & 0xff
    
    def __str__(self):
        return str(int(self))
    
    def set(self, value):
        self._bytes[self._offset] = value & 0xff
    
    def bit(self, bit):
        return Bit(self, bit)

    def is_bit(self, bit):
        return self._bytes[self._offset] & 1 << bit > 0
    
    def set_bit(self, bit):
        self._bytes[self._offset] |= 1 << bit

    def clear_bit(self, bit):
        self._bytes[self._offset] &= ~(1 << bit)

    def flip_bit(self, bit):
        self._bytes[self._offset] ^= 1 << bit

class Word:
    def __init__(self, bytes, offset, signed=True):
        self._bytes = bytes
        self._offset = offset
        self._signed = signed
    
    def __int__(self):
        value = ((self._bytes[self._offset] & 0xff) << 8) + (self._bytes[self._offset + 1] & 0xff)
        return  -1 & value if self._signed and value >= 0x8000 else value
    
    def __str__(self):
        return str(int(self))

    def set(self, value):
        v = value & 0xffff
        self._bytes[self._offset] = v >> 8
        self._bytes[self._offset + 1] = v 

class Bytes:
    def __init__(self, bytes, key = None):
        self._bytes = bytes
        self._slice = key if key is not None else slice(0,len(bytes))
    
    def bit(self, offset, bit):
        return self.byte(offset).bit(bit)
    
    def byte(self, offset):
        assert offset + self._slice.start < self._slice.stop
        return Byte(self._bytes, offset + self._slice.start)
    
    def word(self, offset, signed=True):
        assert offset + self._slice.start + 1 < self._slice.stop
        return Word(self._bytes, offset + self._slice.start, signed)

    def address(self, offset):
        return self.word(offset, False)
    
    def bytes(self):
        return self._bytes[self._slice]

    def zchars(self, offset):
        o = offset
        r = []
        while True:
            w = int(self.address(o))
            r.append(w & 0x1f)
            r.append(w >> 5 & 0x1f)
            r.append(w >> 10 & 0x1f)
            o += 2
            if w >> 15 > 0:
                return r
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            newslice = slice(c(self._slice.start, 0) + c(key.start, 0), c(key.stop + c(self._slice.start, 0), self._slice.stop, len(self._bytes)))
            return Bytes(self._bytes, newslice)
        return self.byte(key)
    
    def __len__(self):
        return self._slice.stop - self._slice.start

class FrozenBit(Bit):
    def __init__(self, value):
        super().__init__(Byte(Bytes([0]),0),0)
        self._value = value
    
    def __bool__(self):
        return bool(self._value)


class FrozenWord(Word):
    def __init__(self, value):
        super().__init__(Bytes([0,0]),0)
        self._value = value
    
    def __int__(self):
        return int(self._value)

ON = FrozenBit(True)
OFF = FrozenBit(False)
ZERO = FrozenWord(0)