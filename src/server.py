#!/usr/bin/env python3
import argparse
import itertools
import random
import socket
import threading
import time
import zlib

import messages as m
import physics as p
import world as w

last_cmsg_received = -1
world = w.World()


def receive():
    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != caddr:
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert 4 + 1 + 1 <= len(packet) <= 1440
        cmsg = m.ClientMessage.frombytes(packet)
        last_cmsg_received = cmsg.id
        print('Received id=%d (%d bytes, %d decompressed)' %
              (last_cmsg_received, len(recv_data), len(packet)))


def send():
    smsg_count = itertools.count()

    t = 0
    dt = 0.200  # seconds
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
            # snapshot and send
            smsg = m.ServerMessage()
            smsg.id = next(smsg_count)
            smsg.last_cmsg_received = last_cmsg_received
            smsg.op = random.choice([m.ServerOperations.NOP,
                                     m.ServerOperations.SNAPSHOT])
            if smsg.op == m.ServerOperations.SNAPSHOT:
                smsg.server_time = time.perf_counter()
                smsg.frame_count = frame_count
                smsg.world = w.World.diff(w.World.dummy(), world)
                smsg.world_len = len(smsg.world)
                smsg.n_entities = len(world.entities)

            packet = m.ServerMessage.tobytes(smsg)
            send_data = zlib.compress(packet)
            s.sendto(send_data, caddr)
            print('Sent %d bytes (decompressed: %d)' %
                  (len(send_data), len(packet)))
            t += dt
            acc -= dt


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

t = threading.Thread(target=receive)
t.daemon = True
t.start()
t = threading.Thread(target=send)
t.daemon = True
t.start()

# run simulation
t = 0
dt = 0.010  # seconds
acc = 0
frame_count = 0
currenttime = time.perf_counter()
while True:
    newtime = time.perf_counter()
    frametime = newtime - currenttime
    if frametime > 0.250:
        frametime = 0.250
    currenttime = newtime

    acc += frametime
    while acc >= dt:
        world.update(dt)
        t += dt
        acc -= dt
        frame_count += 1
