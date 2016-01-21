import random
import socket
import sys
import threading
import time
import zlib

import entities as e
import messages as m
import networking as n
import physics as p


def receive():
    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != caddr:
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert 4 + 1 + 1 <= len(packet) <= 1440
        print('Received back %d bytes (decompressed: %d)' %
              (len(recv_data), len(packet)))


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

entities = list()
for i in range(3):
    entities.append(e.Cube(p.Vector.random(), i))

threading.Thread(target=receive).start()

# simulate updates to client
while True:
    smsg = m.ServerMessage()
    smsg.last_cmsg_received_seq = 42
    smsg.op = random.choice([m.ServerOperations.NOP,
                             m.ServerOperations.SNAPSHOT])
    smsg.server_time = time.perf_counter()
    smsg.last_frame_num = 1338
    smsg.entities = entities

    packet = m.ServerMessage.tobytes(smsg)
    send_data = zlib.compress(packet)
    s.sendto(send_data, caddr)
    print('Sent %d bytes (decompressed: %d)' % (len(send_data), len(packet)))
    time.sleep(abs(random.gauss(0.4, 0.3)))
