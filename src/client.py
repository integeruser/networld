#!/usr/bin/env python3
import argparse
import collections
import itertools
import json
import logging
import socket
import sys
import threading
import time

import pyglet
import yaml

import messages_pb2 as m
import netchannel as nc
import world as w

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
parser.add_argument('--no-gui', action='store_true')
args = parser.parse_args()

use_gui = not args.no_gui

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=args.loglevel or logging.INFO)


def process(message):
    sv_message = m.ServerMessage()
    sv_message.ParseFromString(message.data)

    if sv_message.op == m.ServerMessage.NOOP:
        pass
    elif sv_message.op == m.ServerMessage.SNAPSHOT:
        world.update(sv_message.data)
        max_snapshotseq_recv = message.seq
    else:
        raise NotImplementedError


def ack():
    while True:
        time.sleep(1. / config['cl_cmdrate'])

        cl_message = m.ClientMessage(data=b'ack')
        netchan.transmit(m.Message(reliable=False, data=cl_message.SerializeToString()))


# load the configuration and the world to simulate
with open('../data/config.yml') as f:
    config = yaml.load(f)
    logger.info(json.dumps(config, indent=4))
with open('../data/world.yml') as f:
    world = yaml.load(f)

# set up a netchannel
sv_addr = ('0.0.0.0', 31337)
cl_addr = ('0.0.0.0', 31338)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(cl_addr)
netchan = nc.NetChannel(sock, sv_addr, process)

threading.Thread(target=ack, daemon=use_gui).start()

if use_gui:
    window = pyglet.window.Window()

    @window.event
    def on_key_press(symbol, modifiers):
        pass

    @window.event
    def on_key_release(symbol, modifiers):
        pass

    @window.event
    def on_resize(width, height):
        pyglet.gl.glViewport(0, 0, 2 * width, 2 * height)
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
