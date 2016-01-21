import collections
import socket
import sys
import threading
import time
import zlib

import entities as e
import networking as n
import physics as p
from enum import Enum


class Operations(Enum):
    NOP =            0x01
    GAMESTATE =      0x02
    SERVER_COMMAND = 0x05
    DOWNLOAD =       0x06
    SNAPSHOT =       0x07


def buildpacket(op, entities):
    packet = bytearray()

    last_client_command_received = 0
    n.w_int(packet, last_client_command_received)

    n.w_byte(packet, op.value)

    if op == Operations.SNAPSHOT:
        server_time = time.perf_counter()
        n.w_float(packet, server_time)

        last_frame_num = 0
        n.w_int(packet, last_frame_num)

        for entity in entities:
            msg = e.Entity.new(entity)
            packet.extend(msg)

        EOE = 0x3FF
        n.w_short(packet, EOE)
    elif op == Operations.NOP:
        pass
    else:
        raise NotImplementedError

    EOF = 0x08
    n.w_byte(packet, EOF)
    return packet


def receive():
    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != caddr:
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert 4+1+1 <= len(packet) <= 1440
        print('Received back %d bytes (decompressed: %d)' % (len(recv_data), len(packet)))

def send():
    op = None
    while True:
        op = Operations.NOP if op == Operations.SNAPSHOT else Operations.SNAPSHOT
        packet = buildpacket(op, entities)
        deque.append((packet, False))

        send_data = zlib.compress(packet)
        s.sendto(send_data, caddr)
        print('Sent %d bytes (decompressed: %d)' % (len(send_data), len(packet)))
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s sport' % sys.argv[0])
        sys.exit(2)

    sport = int(sys.argv[1])
    saddr = ('127.0.0.1', sport)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(saddr)

    # wait for any message from client to start a connection
    print('Waiting for connection...')
    recv_data, caddr = s.recvfrom(2048)
    print('Client %s connected, starting...' % str(caddr))

    deque = collections.deque(maxlen=3)

    entities = list()
    for i in range(3):
        entities.append(e.Cube(p.Vector.random(), i))

    threading.Thread(target=receive).start()
    threading.Thread(target=send).start()
