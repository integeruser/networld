#!/usr/bin/env python3
import argparse
import collections
import heapq
import itertools
import logging
import os
import random
import socket
import sys
import threading
import time
import zlib

import pyglet

import messages as m
import networking as n
import world as w


def process():
    to_process_buffer = []
    while True:
        while to_process_deque:
            # extract a message from the process queue
            smsg = to_process_deque.popleft()
            # and push it in the process buffer
            heapq.heappush(to_process_buffer, (smsg.id, smsg))

        swap = []
        global last_smsg_received_id
        prev_last_smsg_received_id = last_smsg_received_id
        while to_process_buffer:
            # extract a message from the process buffer
            smsg.id, smsg = heapq.heappop(to_process_buffer)

            # check if it can be processed
            if smsg.id <= last_smsg_received_id:
                continue
            elif smsg.id == last_smsg_received_id + 1:
                # process it
                if smsg.op == m.ServerOperations.SNAPSHOT:
                    world.update(smsg.world)
                # increment the count of received messages
                last_smsg_received_id = smsg.id
            else:
                swap.append((smsg.id, smsg))
                swap.extend(to_process_buffer)
                break
        to_process_buffer = swap

        # acknowledge the arrival of the last valid message
        assert last_smsg_received_id >= prev_last_smsg_received_id
        if last_smsg_received_id > prev_last_smsg_received_id:
            cmsg = m.ClientMessage()
            cmsg.last_smsg_received = last_smsg_received_id
            to_send_deque.append(cmsg)

        time.sleep(0.050)


def receive():
    sock.settimeout(3)

    while True:
        # read from socket
        try:
            recv_data, addr = sock.recvfrom(2048)
        except socket.timeout:
            logger.debug('Timeout!')
            os._exit(1)

        if addr != server_addr:
            continue
        packet = bytearray(zlib.decompress(recv_data))
        assert len(packet) <= 1440

        # add the received message to the process queue
        smsg = m.ServerMessage.frombytes(packet)
        logger.debug('Received id=%d op=%s bytes=%d' % (smsg.id, smsg.op, len(recv_data)))
        to_process_deque.append(smsg)


def send():
    cmsg_ids = itertools.count()

    while True:
        while to_send_deque:
            # extract a message from the send queue
            cmsg = to_send_deque.popleft()
            cmsg.id = next(cmsg_ids)  # to refactor
            packet = m.ClientMessage.tobytes(cmsg)

            # write on socket
            n = sock.sendto(zlib.compress(packet), server_addr)
            logger.debug('Sent id=%d bytes=%d' % (cmsg.id, n))
        time.sleep(0.700)


world = w.World()

last_smsg_received_id = -1

to_process_deque = collections.deque()
to_send_deque = collections.deque()


parser = argparse.ArgumentParser()
parser.add_argument('host')
parser.add_argument('port', type=int)
parser.add_argument('-g', '--gui', action='store_true')
args = parser.parse_args()

# load the logger
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# create the client socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# connect to the server
server_addr = (socket.gethostbyname(args.host), args.port)
sock.sendto(b'\xde\xad\xbe\xef', server_addr)

# start the simulation
threading.Thread(target=process, daemon=args.gui).start()
threading.Thread(target=receive, daemon=True).start()
threading.Thread(target=send, daemon=True).start()

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

    def update(dt):
        world.tick(dt)

    pyglet.clock.schedule_interval(update, 1 / 60)
    pyglet.app.run()
