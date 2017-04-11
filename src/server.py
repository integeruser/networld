#!/usr/bin/env python3
import argparse
import collections
import copy
import itertools
import logging
import socket
import sys
import threading
import time

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


class Snapshots:
    def __init__(self):
        self.history = {}
        self.last_ack_recv = -1

    def add(self, id, world):
        self.history[id] = world

    def receive(self, ack):
        self.last_ack_recv = max(self.last_ack_recv, ack)
        self.history = {
            sv_msg_id: world
            for sv_msg_id, world in self.history.items() if sv_msg_id >= self.last_ack_recv
        }
        logger.debug('Recv ack=%d history=%s' % (self.last_ack_recv, self.history))


def update():
    t = 0
    dt = 1. / config['tickrate']
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


def receive(data):
    cl_msg = m.ClientMessage.frombytes(data)
    snapshots.receive(cl_msg.ack)


def snapshot():
    while True:
        sv_msg = m.ServerMessage(m.ServerOperations.SNAPSHOT)
        sv_msg.world = w.World.diff(snapshots.history[snapshots.last_ack_recv], world)
        sv_msg.world_len = len(sv_msg.world)
        sv_msg.n_entities = len(world.entities)
        logger.debug('Snapshot id=%d using id=%d' % (sv_msg.id, snapshots.last_ack_recv))

        snapshots.add(sv_msg.id, world)

        netchannel.transmit(m.ServerMessage.tobytes(sv_msg))
        time.sleep(1. / config['sv_updaterate'])


def noise():
    while True:
        sv_msg = m.ServerMessage(m.ServerOperations.NOP)
        netchannel.transmit(m.ServerMessage.tobytes(sv_msg))
        time.sleep(0.500)


# load the configuration
with open('config.yml') as f:
    config = yaml.load(f)

# load the world to simulate
with open('world.yml') as f:
    world = yaml.load(f)

snapshots = Snapshots()
snapshots.history[snapshots.last_ack_recv] = world

# set up a netchannel
sv_addr = ('0.0.0.0', 31337)
cl_addr = ('0.0.0.0', 31338)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(sv_addr)
netchannel = nc.NetChannel(sock, cl_addr, receive)

# start the simulation
threading.Thread(target=update, daemon=False).start()
threading.Thread(target=snapshot, daemon=True).start()
threading.Thread(target=noise, daemon=True).start()
