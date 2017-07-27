import json
import socket
import time

HOST, PORT = "192.168.0.86", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((HOST, PORT))
    req = dict(req_id = 11)
    req_string = json.dumps(req)
    while 1:
        sock.send(req_string)
        print "Requested value for id: {}".format(req['req_id'])
        # Receive data from the server and shut down
        received = sock.recv(1024)
        print "Received value : {}".format(received)
        time.sleep(1)

finally:
    sock.close()

