import socket

import socket
HOST = 'localhost'
PORT = 8005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
msg = s.recv(1024)
print (msg)
count = 0
while count < 5:
    cmd = input("Please input msg:")
    s.send(cmd.encode("utf-8"))
    data = s.recv(1024)
    print(data)
    count += 1
s.close()