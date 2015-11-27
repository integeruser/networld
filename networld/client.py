import socket
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s shost sport' % sys.argv[0])
        sys.exit(2)

    shost = sys.argv[1]
    sport = int(sys.argv[2])
    saddr = (shost, sport)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send any message to server to start a connection
    import time
    time.sleep(1)
    s.sendto(b'\xde\xad\xbe\xef', saddr)
    print('sent')

    while True:
        recv_data, addr = s.recvfrom(2048)
        if addr != saddr:
            continue

        print("Received %d bytes" % len(recv_data))
        assert 4+1+1 <= len(recv_data) <= 1440
