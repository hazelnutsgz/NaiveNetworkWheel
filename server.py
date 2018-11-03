import socket

HOST = 'localhost'
PORT = 8004

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
s.settimeout(0)
connection_pool = []

while True:
	for conn in connection_pool:
		data = ''
		try:
			conn.settimeout(0)
			temp = conn.recv(1024).decode("utf-8")
		except Exception:
			print ("Wrong")
			continue
		data += temp
		while True:
			try:
				temp = conn.recv(1024).decode("utf-8")
				data += temp
			except:
				break
		print (data)
		conn.send("server received you message.".encode("utf-8"))

	try:
	    conn, addr = s.accept()
	    print ('Connected by ', addr)
	    conn.send("Thanks for your registration..".encode("utf-8"))
	    connection_pool.append(conn)
	except socket.timeout:
		pass
	

        
    

    

# conn.close()