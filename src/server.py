#!/usr/bin/env python3
import argparse
import collections
import copy
import itertools
import json
import logging
import socket
import sys
import threading
import time

import yaml

import messages_pb2 as m
import netchannel as nc
import world as w

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=args.loglevel or logging.INFO)


def process(message):
    cl_message = m.ClientMessage()
    cl_message.ParseFromString(message.data)

    global snapshots_history, last_snapshot_id
    if cl_message.id in snapshots_history:
        snapshots_history = {id: world for id, world in snapshots_history.items() if id >= last_snapshot_id}
        last_snapshot_id = cl_message.id


def snapshot():
    while True:
        time.sleep(1. / config['sv_updaterate'])

        id = next(id_count)
        snapshots_history[id] = world
        logger.info('Snapshot id=%d using id=%d' % (id, last_snapshot_id))

        sv_message = m.ServerMessage(
            id=id, op=m.ServerMessage.SNAPSHOT, data=bytes(w.World.diff(snapshots_history[last_snapshot_id], world)))
        netchan.transmit(m.Message(data=sv_message.SerializeToString()))


def noise():
    while True:
        time.sleep(0.20)

        sv_message = m.ServerMessage(op=m.ServerMessage.NOOP)
        netchan.transmit(m.Message(data=sv_message.SerializeToString()))


# load the configuration and the world to simulate
with open('../data/config.yml') as f:
    config = yaml.load(f)
    logger.info(json.dumps(config, indent=4))
with open('../data/world.yml') as f:
    world = yaml.load(f)

id_count = itertools.count(1)
last_snapshot_id = 0

snapshots_history = {last_snapshot_id: world}

# set up a netchannel
sv_addr = ('0.0.0.0', 31337)
cl_addr = ('0.0.0.0', 31338)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(sv_addr)
netchan = nc.NetChannel(sock, cl_addr, process)

threading.Thread(target=snapshot, daemon=True).start()
threading.Thread(target=noise, daemon=True).start()

# start the simulation
t = 0
dt = 1. / config['tickrate']
acc = 0
current_time = time.perf_counter()
frame_count = 0
while True:
    new_time = time.perf_counter()
    frame_time = new_time - current_time
    if frame_time > 0.25:
        frame_time = 0.25
    current_time = new_time

    acc += frame_time
    while acc >= dt:
        world.tick(dt)
        t += dt
        acc -= dt
        frame_count += 1
    time.sleep(0.01)
