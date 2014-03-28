# demonstration of python sockets: UDP receiving
# https://wiki.python.org/moin/UdpCommunication
# 
# alternative: nc -ul 9000

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg=''
ip="127.0.0.1"
port=9000

sock.bind((ip,port))
print "Listening on %s:%s" % (ip,port)
while True:
    msg, addr = sock.recvfrom(1024)
    print "RX: '%s' over UDP from %s" %(msg, addr)
