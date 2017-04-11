import collections
import itertools
import logging
import sys
import threading
import time
import zlib

import networking as n

logger = logging.getLogger(__name__)


class Connection:
    MAX_PACKET_LEN = 2048

    def __init__(self, sock, cl_addr, send_rate):
        self.sock = sock
        self.cl_addr = cl_addr
        self.send_rate = send_rate

        self.send_deque = collections.deque()
        self.recv_deque = collections.deque()
        threading.Thread(target=self._send, daemon=True).start()
        threading.Thread(target=self._recv, daemon=True).start()

    def _pack_messages(self):
        packet = bytearray()
        msg_count = 0

        while True:
            try:
                msg = self.send_deque.popleft()
            except IndexError:
                break
            else:
                if len(packet) + 2 + len(msg) < Connection.MAX_PACKET_LEN:
                    n.w_short(packet, len(msg))
                    n.w_blob(packet, msg)
                    msg_count += 1
                else:
                    self.send_deque.appendleft(msg)
                    break
        return packet, msg_count

    def _unpack_messages(self, packet):
        msg_count = 0
        while packet:
            msg = n.r_blob(packet, n.r_short(packet))
            self.recv_deque.append(msg)
            msg_count += 1
        return msg_count

    def _send(self):
        dt = 1. / self.send_rate
        acc = 0
        current_time = time.perf_counter()
        while True:
            new_time = time.perf_counter()
            frame_time = new_time - current_time
            current_time = new_time

            acc += frame_time
            while acc >= dt:
                acc -= dt

                packet, msg_count = self._pack_messages()
                if packet:
                    n = self.sock.sendto(zlib.compress(packet), self.cl_addr)
                    assert n <= Connection.MAX_PACKET_LEN
                    logger.debug('Sent to %s count=%d bytes=%d' % (self.cl_addr, msg_count, n))

    def _recv(self):
        while True:
            recv_data, _ = self.sock.recvfrom(Connection.MAX_PACKET_LEN)
            packet = bytearray(zlib.decompress(recv_data))
            msg_count = self._unpack_messages(packet)
            logger.debug('Recv fr %s count=%d bytes=%d' % (self.cl_addr, msg_count, len(recv_data)))
            time.sleep(0.005)

    def enqueue(self, msg):
        self.send_deque.append(msg)

    def dequeue(self):
        return self.recv_deque.popleft()


class NetChannel:
    def __init__(self, sock, cl_addr, send_rate, process_callback):
        self.conn = Connection(sock, cl_addr, send_rate)
        self.process_callback = process_callback

        self.seq_count = itertools.count()
        self.last_seq_proc = -1
        self.ack_to_send_back = -1
        self.ack_to_recv = None

        self.rel_deque = collections.deque()
        self.unrel_deque = collections.deque()
        self.rel_msg_to_send = None
        threading.Thread(target=self._send, daemon=True).start()
        threading.Thread(target=self._recv, daemon=True).start()

    @staticmethod
    def _pack_message(reliable, seq, ack, data):
        msg = bytearray()
        n.w_byte(msg, reliable)
        n.w_int(msg, seq)
        n.w_int(msg, ack)
        n.w_short(msg, len(data))
        n.w_blob(msg, data)
        return msg

    @staticmethod
    def _unpack_message(msg):
        reliable = n.r_byte(msg)
        seq = n.r_int(msg)
        ack = n.r_int(msg)
        data = n.r_blob(msg, n.r_short(msg))
        return (reliable, seq, ack, data)

    def _send(self):
        while True:
            if not self.rel_msg_to_send:
                # extract a new reliable message from the queue
                try:
                    self.rel_msg_to_send = self.rel_deque.popleft()
                except IndexError:
                    pass

            if self.rel_msg_to_send:
                # send the reliable message
                reliable, seq, ack, data = self.rel_msg_to_send
                self.ack_to_recv = seq
                msg = NetChannel._pack_message(reliable, seq, ack, data)
                self.conn.enqueue(msg)

            # send all unreliables messages
            while True:
                try:
                    reliable, seq, ack, data = self.unrel_deque.popleft()
                except IndexError:
                    break
                else:
                    msg = NetChannel._pack_message(reliable, seq, ack, data)
                    self.conn.enqueue(msg)
            time.sleep(0.005)

    def _recv(self):
        while True:
            try:
                msg = self.conn.dequeue()
            except IndexError:
                pass
            else:
                reliable, seq, ack, data = NetChannel._unpack_message(msg)
                self.process(reliable, seq, ack, data)
            time.sleep(0.005)

    def transmit(self, data, reliable=False):
        seq = next(self.seq_count)
        ack = self.ack_to_send_back

        msg = (reliable, seq, ack, data)
        if reliable: self.rel_deque.append(msg)
        else: self.unrel_deque.append(msg)
        logger.debug('Tran to %s r=%d seq=%s ack=%s data=%s' % (self.conn.cl_addr, reliable, seq,
                                                                ack, data))

    def process(self, reliable, seq, ack, data):
        # check if the last reliable message sent was acknowledged
        if ack == self.ack_to_recv and self.rel_msg_to_send:
            self.rel_msg_to_send = None
            logger.debug('Ack  fr %s for seq=%s' % (self.conn.cl_addr, ack))

        # acknowledge the arrival of the received message if this is reliable
        if reliable and seq > self.ack_to_send_back:
            self.ack_to_send_back = seq

        if seq <= self.last_seq_proc: return
        # process the received message
        self.last_seq_proc = seq
        self.process_callback(data)
        logger.debug('Proc fr %s r=%d seq=%s ack=%s data=%s' % (self.conn.cl_addr, reliable, seq,
                                                                ack, data))


if __name__ == '__main__':
    import argparse
    import socket
    import threading

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=args.loglevel)

    def ack(netchannel):
        while True:
            netchannel.transmit(b'ack')
            time.sleep(0.250)

    sv_addr = ('0.0.0.0', 31337)
    sv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv_sock.bind(sv_addr)

    cl_addr = ('0.0.0.0', 31338)
    cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cl_sock.bind(cl_addr)

    send_rate = 10
    process_callback = lambda _: None
    sv_netchannel = NetChannel(sv_sock, cl_addr, send_rate, process_callback)
    cl_netchannel = NetChannel(cl_sock, sv_addr, send_rate, process_callback)

    threading.Thread(target=ack, daemon=True, args=[sv_netchannel]).start()
    threading.Thread(target=ack, daemon=True, args=[cl_netchannel]).start()

    for data in [b'a', b'b', b'c', b'd', b'e']:
        sv_netchannel.transmit(data, reliable=True)
        cl_netchannel.transmit(data, reliable=True)
    time.sleep(5)
