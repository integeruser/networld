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
        recv_data, addr = sock.recvfrom(2048)
        if addr != client_addr:
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
    current_time = time.perf_counter()
    while True:
        new_time = time.perf_counter()
        frame_time = new_time - current_time
        if frame_time > 0.250:
            frame_time = 0.250
        current_time = new_time

        acc += frame_time
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
            sock.sendto(send_data, client_addr)
            print('Sent %d bytes (decompressed: %d)' %
                  (len(send_data), len(packet)))
            t += dt
            acc -= dt


parser = argparse.ArgumentParser()
parser.add_argument('port', type=int)
args = parser.parse_args()

server_addr = ('127.0.0.1', args.port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_addr)

# wait for any message from client to start a connection
print('Waiting for connection...')
recv_data, client_addr = sock.recvfrom(2048)
print('Client %s connected, starting...' % str(client_addr))

threading.Thread(target=receive, daemon=True).start()
threading.Thread(target=send,    daemon=True).start()

# run simulation
t = 0
dt = 0.010  # seconds
acc = 0
frame_count = 0
current_time = time.perf_counter()
while True:
    new_time = time.perf_counter()
    frame_time = new_time - current_time
    if frame_time > 0.250:
        frame_time = 0.250
    current_time = new_time

    acc += frame_time
    while acc >= dt:
        world.update(dt)
        t += dt
        acc -= dt
        frame_count += 1
