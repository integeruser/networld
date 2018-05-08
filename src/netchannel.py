import collections
import itertools
import logging
import sys
import threading
import time

import messages_pb2 as m

logger = logging.getLogger(__name__)

lock = threading.Lock()


class NetChannel:
    MAX_PACKET_LEN = 2048

    def __init__(self, sock, cl_addr, process_callback, recv_rate=20, send_rate=20):
        self.sock = sock
        self.cl_addr = cl_addr
        self.process_callback = process_callback
        self.recv_rate = recv_rate
        self.send_rate = send_rate

        self.seq_count = itertools.count(1)
        self.max_seq_recv = -1
        self.ack_to_send_back = -1
        self.min_ack_to_recv = -1

        self.rel_messages_deque = collections.deque()
        self.unrel_messages_deque = collections.deque()
        self.rel_messages_to_send = list()

        self.msgseq_count = itertools.count(1)
        self.max_msgseq_recv = -1

        threading.Thread(target=self._send, daemon=True).start()
        threading.Thread(target=self._recv, daemon=True).start()

    def _recv(self):
        while True:
            time.sleep(1. / self.recv_rate)

            # read data from the socket
            recv_data, _ = self.sock.recvfrom(NetChannel.MAX_PACKET_LEN)
            assert len(recv_data) <= NetChannel.MAX_PACKET_LEN

            # rebuild the packet
            packet = m.Packet()
            packet.ParseFromString(recv_data)
            logger.debug(
                f'{self.sock.getsockname()}: _recv packet seq={packet.seq} ack={packet.ack} messages={[message.seq for message in packet.messages]}'
            )

            # update the info on the latest packet received
            if packet.seq < self.max_seq_recv:
                logger.debug(f'{self.sock.getsockname()}: _recv packet seq={packet.seq} is late')
                continue
            if packet.seq == self.max_seq_recv:
                # two packets cannot have the same seq number
                raise AssertionError
            self.max_seq_recv = packet.seq

            if packet.ack >= self.min_ack_to_recv:
                # the last reliable messages sent arrived at destination
                with lock:
                    self.rel_messages_to_send = list()
                    self.min_ack_to_recv = -1

            for message in sorted(packet.messages, key=lambda message: message.seq):
                if message.reliable:
                    # acknowledge the arrival of the reliable message
                    assert self.ack_to_send_back <= packet.seq
                    self.ack_to_send_back = packet.seq
                self.process(message)

    def _send(self):
        while True:
            time.sleep(1. / self.send_rate)

            # extract a batch of unreliable messages to send this time only
            unrel_messages_to_send = [
                self.unrel_messages_deque.popleft() for _ in range(len(self.unrel_messages_deque))
            ]

            with lock:
                if not self.rel_messages_to_send:
                    # extract a batch of reliable messages to repeatedly send until acknowledged
                    self.rel_messages_to_send = [
                        self.rel_messages_deque.popleft() for _ in range(len(self.rel_messages_deque))
                    ]

                messages_to_send = self.rel_messages_to_send + unrel_messages_to_send
            if not messages_to_send: continue

            # build a packet
            packet = m.Packet(seq=next(self.seq_count), ack=self.ack_to_send_back, messages=messages_to_send)
            logger.debug(
                f'{self.sock.getsockname()}: _send packet seq={packet.seq} ack={packet.ack} messages={[message.seq for message in packet.messages]}'
            )

            # send the packet
            n = self.sock.sendto(packet.SerializeToString(), self.cl_addr)
            assert n <= NetChannel.MAX_PACKET_LEN

            # add the packet seq to the list of acks to receive if the packet contains reliable messages
            if self.rel_messages_to_send:
                self.min_ack_to_recv = min(self.min_ack_to_recv, packet.seq)

    def transmit(self, message):
        # assign the message a unique seq number
        assert message.seq == 0
        message.seq = next(self.msgseq_count)

        logger.debug(f'{self.sock.getsockname()}: transmit seq={message.seq} data={message.data}')

        # put the message in the appropriate deque
        if message.reliable: self.rel_messages_deque.append(message)
        else: self.unrel_messages_deque.append(message)

    def process(self, message):
        logger.debug(f'{self.sock.getsockname()}: process message seq={message.seq} data={message.data}')

        # update the info on the latest message received
        if message.seq <= self.max_msgseq_recv:
            logger.debug(f'{self.sock.getsockname()}: process message seq={message.seq} is late or duplicate')
            return
        self.max_msgseq_recv = message.seq

        self.process_callback(message)


if __name__ == '__main__':
    import argparse
    import random
    import socket

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=args.loglevel or logging.INFO)

    sv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv_addr = ('0.0.0.0', 31337)
    sv_sock.bind(sv_addr)

    cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cl_addr = ('0.0.0.0', 31338)
    cl_sock.bind(cl_addr)

    num_reliable_messages_to_send = 20
    sv_data_to_send = [
        random.randint(0, 0xffffffff).to_bytes(length=4, byteorder='little')
        for _ in range(num_reliable_messages_to_send)
    ]
    cl_data_to_send = [
        random.randint(0, 0xffffffff).to_bytes(length=4, byteorder='little')
        for _ in range(num_reliable_messages_to_send)
    ]
    sv_data_to_recv = iter(cl_data_to_send)
    cl_data_to_recv = iter(sv_data_to_send)

    def sv_process_callback(message):
        logger.info(f'sv: process callback seq={message.seq} data={message.data}')
        if message.reliable:
            assert message.data == next(sv_data_to_recv)

    def cl_process_callback(message):
        logger.info(f'cl: process callback seq={message.seq} data={message.data}')
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

    for i in range(num_reliable_messages_to_send):
        sv_netchan.transmit(m.Message(reliable=True, data=sv_data_to_send[i]))
        cl_netchan.transmit(m.Message(reliable=True, data=cl_data_to_send[i]))
        time.sleep(0.15)
    time.sleep(3.00)
