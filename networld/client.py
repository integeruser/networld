import collections
import socket
import sys
import threading
import time
import zlib

import networking as n


def receive():
    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != saddr:
            continue

        packet = bytearray(zlib.decompress(recv_data))
        assert 4+1+1 <= len(packet) <= 1440
        deque.append(packet)
        print('Received %d bytes (decompressed: %d)' % (len(recv_data), len(packet)))

def send():
    while True:
        while deque:
            packet = deque.popleft()

            send_data = zlib.compress(packet)
            s.sendto(send_data, saddr)
            print('Sent back %d bytes (decompressed: %d)' % (len(send_data), len(packet)))
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s shost sport' % sys.argv[0])
        sys.exit(2)

    shost = sys.argv[1]
    sport = int(sys.argv[2])
    saddr = (shost, sport)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # send any message to server to start a connection
    s.sendto(b'\xde\xad\xbe\xef', saddr)

    deque = collections.deque(maxlen=3)
    threading.Thread(target=receive).start()
    threading.Thread(target=send).start()
