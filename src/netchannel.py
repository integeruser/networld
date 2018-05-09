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

    def __init__(self, sock, cl_addr, process_callback, recv_rate, send_rate):
        self.sock = sock
        self.cl_addr = cl_addr
        self.process_callback = process_callback
        self.recv_rate = recv_rate
        self.send_rate = send_rate

        self.pktseq_count = itertools.count(1)
        self.max_pktseq_recv = -1
        self.min_pktack_to_recv = -1

        self.msgseq_count = itertools.count(1)
        self.max_msgseq_recv = -1
        self.max_rel_msgseq_recv = -1

        self.rel_messages_deque = collections.deque()
        self.unrel_messages_deque = collections.deque()
        self.rel_messages_to_send = list()

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
                f'{self.sock.getsockname()}: _recv pktseq={packet.seq} pktack={packet.ack} messages={[message.seq for message in packet.messages]}'
            )

            if packet.seq < self.max_pktseq_recv:
                # discard the packet because a newer one was already received
                logger.debug(f'{self.sock.getsockname()}: _recv pktseq={packet.seq} is late')
                continue
            if packet.seq == self.max_pktseq_recv:
                # two packets cannot have the same seq number
                raise AssertionError
            self.max_pktseq_recv = packet.seq

            if packet.ack >= self.min_pktack_to_recv:
                # the current batch of reliable messages to send arrived at destination
                with lock:
                    self.rel_messages_to_send = list()
                    self.min_pktack_to_recv = -1

            # process the messages received
            for message in sorted(packet.messages, key=lambda message: message.seq):
                self.process(message)

    def _send(self):
        while True:
            time.sleep(1. / self.send_rate)

            # extract a batch of unreliable messages to send with this packet only
            unrel_messages_to_send = [
                self.unrel_messages_deque.popleft() for _ in range(len(self.unrel_messages_deque))
            ]

            with lock:
                if not self.rel_messages_to_send:
                    # extract a batch of reliable messages to send repeatedly until acknowledged
                    self.rel_messages_to_send = [
                        self.rel_messages_deque.popleft() for _ in range(len(self.rel_messages_deque))
                    ]

                messages_to_send = self.rel_messages_to_send + unrel_messages_to_send
            if not messages_to_send:
                continue

            # build the packet
            packet = m.Packet(seq=next(self.pktseq_count), ack=self.max_pktseq_recv, messages=messages_to_send)
            logger.debug(
                f'{self.sock.getsockname()}: _send packet pktseq={packet.seq} pktack={packet.ack} messages={[message.seq for message in packet.messages]}'
            )

            # send the packet
            n = self.sock.sendto(packet.SerializeToString(), self.cl_addr)
            assert n <= NetChannel.MAX_PACKET_LEN

            # update the ack number to receive if the packet sent contains reliable messages
            if self.rel_messages_to_send:
                self.min_pktack_to_recv = min(self.min_pktack_to_recv, packet.seq)

    def transmit(self, message):
        # assign the message a unique seq number
        assert message.seq == 0
        message.seq = next(self.msgseq_count)

        # acknowledge the arrival of the last message received
        assert message.ack == 0
        message.ack = self.max_msgseq_recv

        logger.debug(
            f'{self.sock.getsockname()}: transmit msgseq={message.seq} reliable={message.reliable} data={message.data}')

        # put the message in the appropriate deque for later sending
        if message.reliable:
            self.rel_messages_deque.append(message)
        else:
            self.unrel_messages_deque.append(message)

        return message.seq

    def process(self, message):
        logger.debug(
            f'{self.sock.getsockname()}: process msgseq={message.seq} msgack={message.ack} reliable={message.reliable} data={message.data}'
        )

        if message.reliable:
            if message.seq <= self.max_rel_msgseq_recv:
                # discard the message because a newer one was already received
                logger.debug(f'{self.sock.getsockname()}: process msgseq={message.seq} is late or duplicated')
                return
            self.max_rel_msgseq_recv = message.seq
        else:
            if message.seq <= self.max_msgseq_recv:
                # discard the message because a newer one was already received
                logger.debug(f'{self.sock.getsockname()}: process msgseq={message.seq} is late or duplicated')
                return
        self.max_msgseq_recv = max(self.max_msgseq_recv, message.seq)

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
        logger.info(
            f'sv: process_callback msgseq={message.seq} msgack={message.ack} reliable={message.reliable} data={message.data}'
        )
        if message.reliable:
            assert message.data == next(sv_data_to_recv)

    def cl_process_callback(message):
        logger.info(
            f'cl: process_callback msgseq={message.seq} msgack={message.ack} reliable={message.reliable} data={message.data}'
        )
        if message.reliable:
            assert message.data == next(cl_data_to_recv)

    recv_rate = send_rate = 10
    sv_netchan = NetChannel(sv_sock, cl_addr, sv_process_callback, recv_rate, send_rate)
    cl_netchan = NetChannel(cl_sock, sv_addr, cl_process_callback, recv_rate, send_rate)

    def noop(netchan):
        while True:
            time.sleep(0.30)

            netchan.transmit(m.Message(reliable=False, data=b'noop'))

    threading.Thread(target=noop, daemon=True, args=(sv_netchan, )).start()
    threading.Thread(target=noop, daemon=True, args=(cl_netchan, )).start()

    for i in range(num_reliable_messages_to_send):
        time.sleep(0.15)

        sv_netchan.transmit(m.Message(reliable=True, data=sv_data_to_send[i]))
        cl_netchan.transmit(m.Message(reliable=True, data=cl_data_to_send[i]))
    time.sleep(3.00)
