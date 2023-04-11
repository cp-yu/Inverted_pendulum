import socket
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address="localhost"
port=12345
s.bind((address, port))
s.listen(1)
conn,addr=s.accept()
print("Connection established")
while True:
    conn.send(str([1,0,45,0]).encode("utf-8"))
    print(conn.recv(1024).decode())

# conn.send(str([1.0,0.0,45.0,0.0]).encode("utf-8"))