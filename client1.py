import socket

import socket
HOST = 'localhost'
PORT = 8006

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
msg = s.recv(1024)
print (msg)

while True:
    cmd = input("Please input msg:")
    s.send(cmd.encode("utf-8"))
    data = s.recv(1024)
    print (data)

    #s.close()