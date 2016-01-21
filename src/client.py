import argparse
import collections
import random
import socket
import threading
import time
import zlib

import pyglet

import messages as m
import networking as n


def receive():
    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != saddr:
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert 4 + 1 + 1 <= len(packet) <= 1440
        print('Received %d bytes (decompressed: %d)' %
              (len(recv_data), len(packet)))


def send():
    while True:
        while cmsg_deque:
            cmsg = cmsg_deque.popleft()
            packet = m.ClientMessage.tobytes(cmsg)
            send_data = zlib.compress(packet)
            s.sendto(send_data, saddr)
            print('Sent %d bytes (decompressed: %d)' %
                  (len(send_data), len(packet)))
        time.sleep(1)


parser = argparse.ArgumentParser()
parser.add_argument('shost')
parser.add_argument('sport', type=int)
parser.add_argument('-g', '--gui', action='store_true')
args = parser.parse_args()

cmsg_deque = collections.deque()

saddr = (args.shost, args.sport)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# send any message to server to start a connection
s.sendto(b'\xde\xad\xbe\xef', saddr)

threading.Thread(target=receive).start()
threading.Thread(target=send).start()

if args.gui:
    window = pyglet.window.Window()

    @window.event
    def on_key_press(symbol, modifiers):
        # simulate recording of client commands
        cmsg = m.ClientMessage()
        cmsg.server_id = 423
        cmsg.last_smsg_received_seq = 13375
        cmsg_deque.append(cmsg)

    @window.event
    def on_key_release(symbol, modifiers):
        pass

    @window.event
    def on_resize(width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        # pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        # pyglet.gl.glLoadIdentity()
        # pyglet.gl.gluPerspective(45, width / height, 0.1, 1000)
        # pyglet.gl.gluLookAt(2, 3, -6, 0, 0, 0, 0, 1, 0)

    @window.event
    def on_draw():
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT |
                          pyglet.gl.GL_DEPTH_BUFFER_BIT)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()

    def update(dt):
        pass

    pyglet.clock.schedule_interval(update, 1 / 60)
    pyglet.app.run()
