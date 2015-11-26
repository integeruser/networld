import struct

import physics as p


def r_byte(msg):
    b = msg[:1]
    del msg[:1]
    return struct.unpack('>b', b)[0]

def w_byte(msg, b):
    msg.extend(struct.pack('>b', b))


def r_int(msg):
    i = msg[:4]
    del msg[:4]
    return struct.unpack('>i', i)[0]

def w_int(msg, i):
    msg.extend(struct.pack('>i', i))


def r_float(msg):
    f = msg[:4]
    del msg[:4]
    return struct.unpack('>f', f)[0]

def w_float(msg, f):
    msg.extend(struct.pack('>f', f))


def r_vector(msg):
    x, y, z = r_float(msg), r_float(msg), r_float(msg)
    return p.Vector(x, y, z)

def w_vector(msg, v):
    w_float(msg, v.x)
    w_float(msg, v.y)
    w_float(msg, v.z)


if __name__ == '__main__':
    def test01():
        msg = bytearray()
        w_byte(msg, 3)
        w_int(msg, 4)
        w_float(msg, 5)
        w_vector(msg, p.Vector(1337, 31337, 42))

        b = r_byte(msg)
        i = r_int(msg)
        f = r_float(msg)
        v = r_vector(msg)
        assert b == 3 and i == 4 and f == 5
        assert v.x == 1337 and v.y == 31337 and v.z == 42

    test01()
    print('All tests passed!')
