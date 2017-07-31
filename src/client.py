#!/usr/bin/env python3
import argparse
import collections
import itertools
import logging
import socket
import sys
import threading
import time

import pyglet

import messages_pb2 as m
import netchannel as nc
import world as w
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
parser.add_argument('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO)
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=args.loglevel)


def process(message):
    global last_processed_id
    if message.id > last_processed_id:
        if message.op == m.Message.SNAPSHOT:
            world.update(message.data)
        elif message.op == m.Message.NOOP:
            pass
        else:
            raise NotImplementedError
        last_processed_id = message.id


def ack():
    while True:
        netchan.transmit(m.Message(id=next(id_count), ack=last_processed_id, data=b'ack'))
        time.sleep(1. / config['cl_cmdrate'])


# load the configuration and the world to simulate
with open('../data/config.yml') as f:
    config = yaml.load(f)
with open('../data/world.yml') as f:
    world = yaml.load(f)

id_count = itertools.count(1)
last_processed_id = 0

# set up a netchannel
sv_addr = ('0.0.0.0', 31337)
cl_addr = ('0.0.0.0', 31338)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(cl_addr)
netchan = nc.NetChannel(sock, sv_addr, process)

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
