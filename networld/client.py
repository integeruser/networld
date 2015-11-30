import socket
import sys
import zlib

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

    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != saddr:
            continue

        packet = zlib.decompress(recv_data)
        print("Received %d bytes (decompressed: %d)" % (len(recv_data), len(packet)))
        assert 4+1+1 <= len(packet) <= 1440
