import collections
import itertools
import logging
import sys
import threading
import time

import messages_pb2 as m

logger = logging.getLogger(__name__)


class NetChannel:
    MAX_PACKET_LEN = 2048

    def __init__(self, sock, cl_addr, process_callback):
        self.sock = sock
        self.cl_addr = cl_addr
        self.process_callback = process_callback

        self.seq_count = itertools.count(1)
        self.last_seq_recv = 0
        self.ack_to_send_back = 0
        self.acks_to_recv = set()

        self.rel_messages_deque = collections.deque()
        self.unrel_messages_deque = collections.deque()
        self.rel_messages_to_send = list()

        self.id_count = itertools.count(1)
        self.last_id_recv = 0

        threading.Thread(target=self._send, daemon=True).start()
        threading.Thread(target=self._recv, daemon=True).start()

    def _recv(self):
        RECV_RATE = 20
        while True:
            time.sleep(1. / RECV_RATE)

            recv_data, _ = self.sock.recvfrom(NetChannel.MAX_PACKET_LEN)
            packet = m.Packet()
            packet.ParseFromString(recv_data)

            logger.debug('%s: recv seq=%d ack=%d messages=%d' % (self.sock.getsockname(), packet.seq, packet.ack,
                                                                 len(packet.messages)))
            assert packet.seq != self.last_seq_recv
            if packet.seq < self.last_seq_recv: return
            self.last_seq_recv = packet.seq

            self.process(packet)

    def _send(self):
        SEND_RATE = 20
        while True:
            time.sleep(1. / SEND_RATE)

            if not self.rel_messages_to_send:
                # extract a batch of reliable messages to repeatedly send until acknowledged
                self.rel_messages_to_send = [
                    self.rel_messages_deque.popleft() for _ in range(len(self.rel_messages_deque))
                ]
            # extract a batch of unreliable messages to send this time only
            unrel_messages_to_send = [
                self.unrel_messages_deque.popleft() for _ in range(len(self.unrel_messages_deque))
            ]

            messages_to_send = self.rel_messages_to_send + unrel_messages_to_send
            if not messages_to_send: continue

            # send the packet
            packet = m.Packet(seq=next(self.seq_count), ack=self.ack_to_send_back, messages=messages_to_send)
            n = self.sock.sendto(packet.SerializeToString(), self.cl_addr)
            assert n <= NetChannel.MAX_PACKET_LEN
            logger.debug('%s: sent seq=%d ack=%d messages=%d' % (self.sock.getsockname(), packet.seq, packet.ack,
                                                                 len(packet.messages)))

            self.acks_to_recv.add(packet.seq)

    def transmit(self, message):
        # assign the message a unique id
        assert message.id == 0
        message.id = next(self.id_count)

        # put the message in the appropriate deque
        if message.reliable: self.rel_messages_deque.append(message)
        else: self.unrel_messages_deque.append(message)

    def process(self, packet):
        # check if the last reliable message sent was acknowledged
        if packet.ack in self.acks_to_recv:
            self.rel_messages_to_send = None
            self.acks_to_recv = set()

        # process the messages
        for message in packet.messages:
            if message.reliable: self.ack_to_send_back = packet.seq

            if message.id <= self.last_id_recv: return
            self.last_id_recv = message.id

            self.process_callback(message)


if __name__ == '__main__':
    import argparse
    import random
    import socket

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=args.loglevel)

    sv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv_addr = ('0.0.0.0', 31337)
    sv_sock.bind(sv_addr)

    cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cl_addr = ('0.0.0.0', 31338)
    cl_sock.bind(cl_addr)

    num_reliable_messages = 20
    sv_data_to_send = [
        random.randint(0, 0xffffffff).to_bytes(length=4, byteorder='little') for _ in range(num_reliable_messages)
    ]
    cl_data_to_send = [
        random.randint(0, 0xffffffff).to_bytes(length=4, byteorder='little') for _ in range(num_reliable_messages)
    ]
    sv_data_to_recv = iter(cl_data_to_send)
    cl_data_to_recv = iter(sv_data_to_send)

    def sv_process_callback(message):
        if message.reliable:
            assert message.data == next(sv_data_to_recv)

    def cl_process_callback(message):
        if message.reliable:
            assert message.data == next(cl_data_to_recv)

    sv_netchan = NetChannel(sv_sock, cl_addr, sv_process_callback)
    cl_netchan = NetChannel(cl_sock, sv_addr, cl_process_callback)

    def noop(netchan):
        while True:
            netchan.transmit(m.Message(data=b'noop'))
            time.sleep(0.30)

    threading.Thread(target=noop, daemon=True, args=(sv_netchan, )).start()
    threading.Thread(target=noop, daemon=True, args=(cl_netchan, )).start()

    for i in range(num_reliable_messages):
        sv_netchan.transmit(m.Message(reliable=True, data=sv_data_to_send[i]))
        cl_netchan.transmit(m.Message(reliable=True, data=cl_data_to_send[i]))
        time.sleep(0.15)
    time.sleep(2.00)
