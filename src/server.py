#!/usr/bin/env python3
import argparse
import collections
import copy
import heapq
import itertools
import logging
import random
import socket
import sys
import threading
import time
import zlib

import pyglet
import yaml

import entities as e
import messages as m
import physics as p
import world as w


def simulate():
    # run simulation
    t = 0
    dt = 0.010
    acc = 0
    current_time = time.perf_counter()
    frame_count = 0
    while True:
        new_time = time.perf_counter()
        frame_time = new_time - current_time
        if frame_time > 0.250:
            frame_time = 0.250
        current_time = new_time

        acc += frame_time
        while acc >= dt:
            world.tick(dt)
            t += dt
            acc -= dt
            frame_count += 1
        time.sleep(0.005)


def process():
    to_process_buffer = []
    while True:
        while to_process_deque:
            # extract a message from the process queue
            client, cmsg = to_process_deque.popleft()
            # and push it in the process buffer
            heapq.heappush(to_process_buffer, (client, cmsg.id, cmsg))

        swap = []
        global last_cmsg_received_id
        while to_process_buffer:
            # extract a message from the process buffer
            client, cmsg_id, cmsg = heapq.heappop(to_process_buffer)

            # check if it can be processed
            if cmsg.id <= last_cmsg_received_id[client]:
                continue
            elif cmsg.id == last_cmsg_received_id[client] + 1:
                # process it
                global serv_messages
                global last_snapshot_rec
                last_snapshot_rec[client] = serv_messages[client][cmsg.last_smsg_received]
                # increment the count of received messages
                last_cmsg_received_id[client] = cmsg.id
            else:
                swap.append((client, cmsg.id, cmsg))
                swap.extend(to_process_buffer)
                break
        to_process_buffer = swap

        time.sleep(0.050)


def receive():
    while True:
        # read from socket
        recv_data, addr = sock.recvfrom(2048)
        if addr not in clients:
            if recv_data == b'\xde\xad\xbe\xef':
                logger.info('Client %s connected' % str(addr))
                clients.append(addr)
            else:
                logger.warning('Client %s attempted to reconnect' % str(addr))
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert len(packet) <= 1440

        # add the received message to the process queue
        cmsg = m.ClientMessage.frombytes(packet)
        logger.debug('Received id=%d bytes=%d' % (cmsg.id, len(recv_data)))
        to_process_deque.append((addr, cmsg))


def send():
    smsg_ids = collections.defaultdict(itertools.count)

    while True:
        while to_send_deque:
            # extract a message from the send queue
            client, smsg = to_send_deque.popleft()
            smsg.id = next(smsg_ids[client])  # to refactor
            packet = m.ServerMessage.tobytes(smsg)

            # to refactor
            global serv_messages
            serv_messages[client][smsg.id] = copy.deepcopy(world)

            # write on socket
            n = sock.sendto(zlib.compress(packet), client)
            logger.debug('Sent client=%s id=%d op=%s bytes=%d' % (client, smsg.id, smsg.op, n))
        time.sleep(0.150)


def snapshot():
    while True:
        for client in clients:
            smsg = m.ServerMessage()
            smsg.op = m.ServerOperations.SNAPSHOT
            smsg.server_time = time.perf_counter()
            smsg.frame_count = -1  # todo
            smsg.world = w.World.diff(last_snapshot_rec[client], world)
            smsg.world_len = len(smsg.world)
            smsg.n_entities = len(world.entities)
            to_send_deque.append((client, smsg))
            time.sleep(0.300)


def noise():
    while True:
        for client in clients:
            smsg = m.ServerMessage()
            smsg.op = m.ServerOperations.NOP
            to_send_deque.append((client, smsg))
            time.sleep(0.200)


parser = argparse.ArgumentParser()
parser.add_argument('port', type=int)
parser.add_argument('-g', '--gui', action='store_true')
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# load world
with open('world.yml') as f:
    world = yaml.load(f)

last_cmsg_received_id = collections.defaultdict(lambda: -1)

to_process_deque = collections.deque()
to_send_deque = collections.deque()

serv_messages = collections.defaultdict(lambda: {0: w.World()})
last_snapshot_rec = collections.defaultdict(lambda: w.World())

snapshots = collections.deque()

# init sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', args.port))

# start accepting clients
clients = []
threading.Thread(target=receive, daemon=True).start()
logger.info('Waiting for a client...')
while not clients:
    time.sleep(0.5)

threading.Thread(target=simulate, daemon=args.gui).start()
threading.Thread(target=process, daemon=True).start()
threading.Thread(target=send, daemon=True).start()
threading.Thread(target=snapshot, daemon=True).start()
threading.Thread(target=noise, daemon=True).start()

if args.gui:
    window = pyglet.window.Window()

    @window.event
    def on_key_press(symbol, modifiers):
        pass

    @window.event
    def on_key_release(symbol, modifiers):
        pass

    @window.event
    def on_resize(width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.gluPerspective(45, width / height, 0.1, 1000)
        pyglet.gl.gluLookAt(2, 3, -6, 0, 0, 0, 0, 1, 0)
        return pyglet.event.EVENT_HANDLED

    @window.event
    def on_draw():
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()
        world.draw()
        return pyglet.event.EVENT_HANDLED

    pyglet.clock.schedule_interval(lambda *args, **kwargs: None, 1 / 60)
    pyglet.app.run()
