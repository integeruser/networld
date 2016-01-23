import argparse
import random
import socket
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


def send():
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
        print('Sent %d bytes (decompressed: %d)' %
              (len(send_data), len(packet)))
        time.sleep(abs(random.gauss(0.4, 0.3)))


parser = argparse.ArgumentParser()
parser.add_argument('sport', type=int)
args = parser.parse_args()

saddr = ('127.0.0.1', args.sport)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(saddr)

# wait for any message from client to start a connection
print('Waiting for connection...')
recv_data, caddr = s.recvfrom(2048)
print('Client %s connected, starting...' % str(caddr))

entities = list()
for i in range(3):
    entities.append(e.Cube(p.Vector.random(), i))

t = threading.Thread(target=receive)
t.daemon = True
t.start()
t = threading.Thread(target=send)
t.daemon = True
t.start()

# run simulation
t = 0
dt = 0.010
acc = 0
currenttime = time.perf_counter()
while True:
    newtime = time.perf_counter()
    frametime = newtime - currenttime
    if frametime > 0.250:
        frametime = 0.250
    currenttime = newtime

    acc += frametime
    while acc >= dt:
        # world.update(dt)
        t += dt
        acc -= dt
