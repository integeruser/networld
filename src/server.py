#!/usr/bin/env python3
import argparse
import copy
import json
import logging
import random
import socket
import sys
import threading
import time

import yaml

import entities as e
import messages_pb2 as m
import netchannel as nc
import physics as p
import world as w

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=args.loglevel or logging.INFO)

lock = threading.Lock()

################################################################################


def delete_random_entity(command):
    entity = None
    with lock:
        if world.entities:
            entity = world.entities.pop(random.choice(list(world.entities.keys())))
    logger.info(f'delete_random_entity entity={entity}')


def sim_pause(command):
    world.toggle_pause()


def spawn_random_entity(command):
    cube = e.Cube(p.Vector(0, 0, 0), 1)
    cube.speed = p.random.uniform(-3, 3)
    cube.direction = p.Vector.random(-0.5, 0.5).normalize()
    cube.color = p.Vector.random(0, 1)
    with lock:
        world.add_entity(cube)
    logger.info(f'spawn_random_entity entity={cube}')


handlers = {
    m.ClientMessage.Command.Type.Value('DELETE_RANDOM_ENTITY'): delete_random_entity,
    m.ClientMessage.Command.Type.Value('SPAWN_RANDOM_ENTITY'): spawn_random_entity,
    m.ClientMessage.Command.Type.Value('SIM_PAUSE'): sim_pause
}

################################################################################


def process(message):
    cl_message = m.ClientMessage()
    cl_message.ParseFromString(message.data)

    global last_snapshot_ack
    with lock:
        # update most recent snapshot acknowledged
        last_snapshot_ack = max(filter(lambda seq: seq < message.ack, snapshots_history.keys()))

    # execute client commands
    for command in cl_message.commands:
        logger.info(f'process exec command id={m.ClientMessage.Command.Type.Name(command.id)}')
        handlers[command.id](command)


def snapshot():
    while True:
        time.sleep(1. / config['sv_updaterate'])

        global snapshots_history
        with lock:
            # keep only the most recent snapshots
            snapshots_history = {seq: world for seq, world in snapshots_history.items() if seq >= last_snapshot_ack}

            # create the snapshot using the last acknowledged state
            snapshot = bytes(w.World.diff(snapshots_history[last_snapshot_ack], world))

        # build and transmit the message
        sv_message = m.ServerMessage(op=m.ServerMessage.SNAPSHOT, data=snapshot)
        message_seq = netchan.transmit(m.Message(reliable=False, data=sv_message.SerializeToString()))

        logger.info(f'snapshot id={message_seq} using id={last_snapshot_ack}')

        with lock:
            # keep the snapshot in the history
            snapshots_history[message_seq] = copy.deepcopy(world)


def noise():
    while True:
        time.sleep(0.20)

        sv_message = m.ServerMessage(op=m.ServerMessage.NOOP, data=b'noop')
        netchan.transmit(m.Message(reliable=False, data=sv_message.SerializeToString()))


# load the configuration and the world to simulate
with open('../data/config.yml') as f:
    config = yaml.load(f)
    logger.info(json.dumps(config, indent=4))
with open('../data/world.yml') as f:
    world = yaml.load(f)

last_snapshot_ack = 0

snapshots_history = {last_snapshot_ack: world}

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
