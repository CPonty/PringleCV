# demonstration of python sockets: UDP sending
# https://wiki.python.org/moin/UdpCommunication

import socket
from time import sleep

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg='{x:5,y:10,o:90,d:35}'
ip="127.0.0.1"
port=9000

while True:
    sock.sendto(msg,(ip,port))
    print "TX: '%s' over UDP to %s:%d" %(msg, ip, port)
    sleep(1)
