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
    to_process_minheap = []

    while True:
        # move messages from process queue to min-heap
        while to_process_deque:
            s_msg = to_process_deque.popleft()
            priority = s_msg.id
            heapq.heappush(to_process_minheap, (priority, s_msg))

        global last_smsg_received_id
        prev_last_smsg_received_id = last_smsg_received_id
        while to_process_minheap:
            # extract the next message with smallest id
            priority, s_msg = heapq.heappop(to_process_minheap)
            if s_msg.id <= last_smsg_received_id:
                # discard the message
                continue
            elif s_msg.id == last_smsg_received_id + 1:
                # process the message
                if s_msg.op == m.ServerOperations.SNAPSHOT:
                    world.update(s_msg.world)
                # increment the count of received messages
                last_smsg_received_id = s_msg.id
            else:
                # reinsert the message in the min-heap and stop
                logger.warning('Missing messages from server')
                heapq.heappush(to_process_minheap, (priority, s_msg))
                break

        # acknowledge the arrival of the last valid message
        assert last_smsg_received_id >= prev_last_smsg_received_id
        if last_smsg_received_id > prev_last_smsg_received_id:
            cmsg = m.ClientMessage()
            cmsg.last_smsg_received = last_smsg_received_id
            to_send_deque.append(cmsg)

        time.sleep(0.050)


def receive():
    sock.settimeout(1)

    while True:
        # read data from socket
        try:
            recv_data, recv_addr = sock.recvfrom(2048)
        except socket.timeout:
            logger.info('Timeout!')
            os._exit(1)

        if recv_addr != server_addr:
            logger.warning('Received data from unknown %s' % str(recv_addr))
            continue

        # decompress the received data
        assert len(recv_data) <= 1440
        packet = bytearray(zlib.decompress(recv_data))

        # add the received message to the process queue
        s_msg = m.ServerMessage.frombytes(packet)
        logger.debug('Received msg id=%d op=%s len=%d' % (s_msg.id, s_msg.op, len(recv_data)))
        to_process_deque.append(s_msg)


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
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

# load the logger
logger = logging.getLogger(__name__)
levels = [logging.WARNING, logging.INFO, logging.DEBUG]
logging.basicConfig(stream=sys.stdout, level=levels[min(args.verbose, len(levels) - 1)])

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
