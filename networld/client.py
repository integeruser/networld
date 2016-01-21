import collections
import random
import socket
import sys
import threading
import time
import zlib

import messages as m
import networking as n


def receive():
    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != saddr:
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert 4 + 1 + 1 <= len(packet) <= 1440
        print('Received %d bytes (decompressed: %d)' %
              (len(recv_data), len(packet)))


def send():
    while True:
        while cmsg_deque:
            cmsg = cmsg_deque.popleft()
            packet = m.ClientMessage.tobytes(cmsg)
            send_data = zlib.compress(packet)
            s.sendto(send_data, saddr)
            print('Sent %d bytes (decompressed: %d)' %
                  (len(send_data), len(packet)))
        time.sleep(1)


if len(sys.argv) != 3:
    print('Usage: %s shost sport' % sys.argv[0])
    sys.exit(2)

shost = sys.argv[1]
sport = int(sys.argv[2])
saddr = (shost, sport)

cmsg_deque = collections.deque()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# send any message to server to start a connection
s.sendto(b'\xde\xad\xbe\xef', saddr)

threading.Thread(target=receive).start()
threading.Thread(target=send).start()

# simulate recording of client commands
while True:
    cmsg = m.ClientMessage()
    cmsg.server_id = 423
    cmsg.last_smsg_received_seq = 13375

    cmsg_deque.append(cmsg)
    time.sleep(abs(random.gauss(0.4, 0.3)))
