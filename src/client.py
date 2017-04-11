#!/usr/bin/env python3
import argparse
import collections
import heapq
import logging
import socket
import sys
import threading
import time

import pyglet
import yaml

import messages as m
import netchannel as nc
import world as w

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
parser.add_argument('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO)
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=args.loglevel)


def process():
    global last_id_proc
    while True:
        while True:
            try:
                _, sv_msg = heapq.heappop(to_process_minheap)
            except IndexError:
                break
            else:
                if sv_msg.id > last_id_proc:
                    # process the message
                    if sv_msg.op == m.ServerOperations.SNAPSHOT:
                        world.update(sv_msg.world)
                        last_id_proc = sv_msg.id
        time.sleep(0.010)


def receive(data):
    sv_msg = m.ServerMessage.frombytes(data)
    priority = sv_msg.id
    heapq.heappush(to_process_minheap, (priority, sv_msg))


def ack():
    while True:
        cl_msg = m.ClientMessage()
        cl_msg.ack = last_id_proc
        netchannel.transmit(m.ClientMessage.tobytes(cl_msg))
        time.sleep(1. / config['cl_cmdrate'])


# load the configuration
with open('config.yml') as f:
    config = yaml.load(f)

# load the world to simulate
with open('world.yml') as f:
    world = yaml.load(f)

to_process_minheap = []
last_id_proc = -1

# set up a netchannel
sv_addr = ('0.0.0.0', 31337)
cl_addr = ('0.0.0.0', 31338)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(cl_addr)
netchannel = nc.NetChannel(sock, sv_addr, receive)

threading.Thread(target=process, daemon=True).start()
threading.Thread(target=ack, daemon=True).start()

gui = True
if gui:
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

    pyglet.clock.schedule_interval(update, 1. / config['cl_refreshrate'])
    pyglet.app.run()
