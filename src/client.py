#!/usr/bin/env python3
import argparse
import collections
import itertools
import random
import socket
import threading
import time
import zlib

import pyglet

import messages as m
import networking as n
import world as w

last_smsg_received = -1


def receive():
    while True:
        recv_data, addr = sock.recvfrom(2048)
        if addr != server_addr:
            continue
        packet = bytearray(zlib.decompress(recv_data))
        assert len(packet) <= 1440

        smsg = m.ServerMessage.frombytes(packet)
        last_smsg_received = smsg.id
        print('Received id=%d op=%s bytes=%d' %
              (smsg.id, smsg.op, len(recv_data)))
        # todo w.World.update(world, smsg.world_len, smsg.world)


def send():
    while True:
        while cmsg_deque:
            cmsg = cmsg_deque.popleft()
            packet = m.ClientMessage.tobytes(cmsg)

            n = sock.sendto(zlib.compress(packet), server_addr)
            print('Sent id=%d op=%s bytes=%d' % (cmsg.id, cmsg.op, n))
        time.sleep(1)


parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('port', type=int)
parser.add_argument('-g', '--gui', action='store_true')
args = parser.parse_args()

cmsg_deque = collections.deque()

server_addr = (args.hostname, args.port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# send any message to server to start a connection
sock.sendto(b'\xde\xad\xbe\xef', server_addr)

threading.Thread(target=receive, daemon=args.gui).start()
threading.Thread(target=send, daemon=True).start()

if args.gui:
    cmsg_count = itertools.count()

    world = w.World.dummy()
    window = pyglet.window.Window()

    @window.event
    def on_key_press(symbol, modifiers):
        # simulate recording of client commands
        cmsg = m.ClientMessage()
        cmsg.id = next(cmsg_count)
        cmsg.last_smsg_received = last_smsg_received
        cmsg_deque.append(cmsg)

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
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT |
                          pyglet.gl.GL_DEPTH_BUFFER_BIT)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()
        world.draw()
        return pyglet.event.EVENT_HANDLED

    def update(dt):
        pass

    pyglet.clock.schedule_interval(update, 1 / 60)
    pyglet.app.run()
