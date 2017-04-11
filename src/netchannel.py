import collections
import itertools
import logging
import sys
import threading
import time
import zlib

import networking as n

logger = logging.getLogger(__name__)


def pack(reliable, seq, ack, data):
    msg = bytearray()
    n.w_byte(msg, reliable)
    n.w_int(msg, seq)
    n.w_int(msg, ack)
    n.w_int(msg, len(data))
    n.w_blob(msg, data)
    return msg


def unpack(msg):
    reliable = n.r_byte(msg)
    seq = n.r_int(msg)
    ack = n.r_int(msg)
    data = n.r_blob(msg, n.r_int(msg))
    return (reliable, seq, ack, data)


class Connection:
    def __init__(self, sock, cl_addr):
        self.sock = sock
        self.cl_addr = cl_addr

        self.send_deque = collections.deque()
        self.recv_deque = collections.deque()
        threading.Thread(target=self._send, daemon=True).start()
        threading.Thread(target=self._recv, daemon=True).start()

    def _send(self):
        while True:
            try:
                msg = self.send_deque.popleft()
            except IndexError:
                pass
            else:
                n = self.sock.sendto(zlib.compress(msg), self.cl_addr)
                assert n <= 2048
            time.sleep(0.005)

    def _recv(self):
        while True:
            recv_data, _ = self.sock.recvfrom(2048)
            msg = bytearray(zlib.decompress(recv_data))
            self.recv_deque.append(msg)

    def enqueue(self, msg):
        self.send_deque.append(msg)

    def dequeue(self):
        return self.recv_deque.popleft()


class NetChannel:
    def __init__(self, sock, cl_addr, process_callback):
        self.conn = Connection(sock, cl_addr)
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
                msg = pack(reliable, seq, ack, data)
                self.conn.enqueue(msg)

            # send all unreliables messages
            while True:
                try:
                    reliable, seq, ack, data = self.unrel_deque.popleft()
                except IndexError:
                    break
                else:
                    msg = pack(reliable, seq, ack, data)
                    self.conn.enqueue(msg)
            time.sleep(0.005)

    def _recv(self):
        while True:
            try:
                msg = self.conn.dequeue()
            except IndexError:
                pass
            else:
                reliable, seq, ack, data = unpack(msg)
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
    import socket
    import threading

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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

    sv_netchannel = NetChannel(sv_sock, cl_addr, lambda _: None)
    cl_netchannel = NetChannel(cl_sock, sv_addr, lambda _: None)

    threading.Thread(target=ack, daemon=True, args=[sv_netchannel]).start()
    threading.Thread(target=ack, daemon=True, args=[cl_netchannel]).start()

    for data in [b'a', b'b', b'c', b'd', b'e']:
        sv_netchannel.transmit(data, reliable=True)
        cl_netchannel.transmit(data, reliable=True)
    time.sleep(3)
